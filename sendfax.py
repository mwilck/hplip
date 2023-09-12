#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) Copyright 2003-2006 Hewlett-Packard Development Company, L.P.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# Author: Don Welch
#
# Thanks to Henrique M. Holschuh <hmh@debian.org> for various security patches
#

__version__ = '4.2'
__title__ = 'PC Sendfax Utility'
__doc__ = "Allows for sending faxes from the PC using HPLIP supported multifunction printers." 

# Std Lib
import sys, socket, os, os.path, getopt, signal, atexit
import ConfigParser, pwd, socket, time

# Local
from base.g import *
from base.msg import *
import base.utils as utils
import base.async_qt as async
from base import service, device

log.set_module('hp-sendfax')


USAGE = [(__doc__, "", "name", True),
         ("Usage: hp-sendfax [PRINTER|DEVICE-URI] [OPTIONS] [MODE] [FILES]", "", "summary", True),
         utils.USAGE_ARGS,
         utils.USAGE_DEVICE,
         utils.USAGE_PRINTER,
         utils.USAGE_SPACE,
         ("[MODE]", "", "header", False),
         ("Enter graphical UI mode:", "-u or --gui (Default)", "option", False),
         ("Run in non-interactive mode (batch mode):", "-n or --non-interactive", "option", False),
         utils.USAGE_SPACE,
         utils.USAGE_OPTIONS,
         ("Specify the fax number(s):", "-f<number(s)> or --faxnum=<number(s)> (-n only)", "option", False),
         ("Specify the recipient(s):", "-r<recipient(s)> or --recipient=<recipient(s)> (-n only)", "option", False), 
         ("Specify the groups(s):", "-g<group(s)> or --group=<group(s)> (-n only)", "option", False), 
         utils.USAGE_BUS1, utils.USAGE_BUS2,         
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2,# utils.USAGE_LOGGING3,
         ("Run in debug mode:", "--gg (same as option: -ldebug)", "option", False),
         utils.USAGE_HELP,
         ("[FILES]", "", "header", False),
         ("An optional list of files to add to the fax job.", "", "option", True),
         utils.USAGE_NOTES,
         utils.USAGE_STD_NOTES1,
         utils.USAGE_STD_NOTES2,
         ("3. Coversheets are not supported in non-interactive mode (-n)", "", "note", False),
         ("4. Fax numbers and/or recipients should be listed in comma separated lists (-n only).", "", "note", False),
         utils.USAGE_SPACE,
         utils.USAGE_SEEALSO,
         ("hp-fab", "", "seealso", False),
        ]

def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)
        
    utils.format_text(USAGE, typ, __title__, 'hp-sendfax', __version__)
    sys.exit(0)



class fax_client(async.dispatcher):

    def __init__(self, username):
        async.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((prop.hpssd_host, prop.hpssd_port)) 
        self.in_buffer = ""
        self.out_buffer = ""
        self.fields = {}
        self.data = ''
        self.error_dialog = None
        self.signal_exit = False

        # handlers for all the messages we expect to receive
        self.handlers = {
                        'eventgui'         : self.handle_eventgui,
                        'unknown'          : self.handle_unknown,
                        'exitguievent'     : self.handle_exitguievent,
                        }

        self.register_gui(username)

    def handle_read(self):
        log.debug("Reading data on channel (%d)" % self._fileno)

        self.in_buffer = self.recv(prop.max_message_len)
        log.debug(repr(self.in_buffer))

        if self.in_buffer == '':
            return False

        remaining_msg = self.in_buffer

        while True:
            try:
                self.fields, self.data, remaining_msg = parseMessage(remaining_msg)
            except Error, e:
                #log.debug(repr(self.in_buffer))
                log.warn("Message parsing error: %s (%d)" % (e.opt, e.msg))
                self.out_buffer = self.handle_unknown()
                log.debug(self.out_buffer)
                return True

            msg_type = self.fields.get('msg', 'unknown')
            log.debug("%s %s %s" % ("*"*40, msg_type, "*"*40))
            log.debug(repr(self.in_buffer))

            try:
                self.out_buffer = self.handlers.get(msg_type, self.handle_unknown)()
            except Error:
                log.error("Unhandled exception during processing")

            if len(self.out_buffer): # data is ready for send
                self.sock_write_notifier.setEnabled(True)

            if not remaining_msg:
                break

        return True

    def handle_write(self):
        if not len(self.out_buffer):
            return

        log.debug("Sending data on channel (%d)" % self._fileno)
        log.debug(repr(self.out_buffer))
        
        try:
            sent = self.send(self.out_buffer)
        except:
            log.error("send() failed.")

        self.out_buffer = self.out_buffer[sent:]
        

    def writable(self):
        return not ((len(self.out_buffer) == 0)
                     and self.connected)

    def handle_exitguievent(self):
        self.signal_exit = True
        if self.signal_exit:
            if sendfax is not None:
                sendfax.close()
            qApp.quit()

        return ''

    #def handle_faxgetdataresult(self):
    #    pass
    
    # EVENT (GUI)
    def handle_eventgui(self):
        if sendfax is not None:
            try:
                job_id = self.fields.get('job-id', 0)
                event_code = self.fields.get('event-code', 0)
                event_type = self.fields.get('event-type', 'event')
                retry_timeout = self.fields.get('retry-timeout', 0)
                
                lines = self.data.splitlines()
                try:
                    error_string_short, error_string_long = lines[0], lines[1]
                except IndexError:
                    error_string_short, error_string_long = '', ''
                
                device_uri = self.fields.get('device-uri', '')
                printer_name = self.fields.get('printer', '')
                title = self.fields.get('title', '')
                job_size = self.fields.get('job-size', 0)
    
                log.debug("Event: %d '%s'" % (event_code, event_type))
    
                sendfax.EventUI(event_code, event_type, error_string_short,
                                error_string_long, retry_timeout, job_id,
                                device_uri, printer_name, title, job_size)
    
            except:
                log.exception()
    
        return ''

    def handle_unknown(self):
        return ''

    def handle_messageerror(self):
        return ''

    def handle_close(self):
        log.debug("closing channel (%d)" % self._fileno)
        self.connected = False
        async.dispatcher.close(self)

    def register_gui(self, username):
        out_buffer = buildMessage("RegisterGUIEvent", None, 
                                  {'type': 'fax', 
                                   'username': username})
        self.send(out_buffer)






prop.prog = sys.argv[0]

device_uri = None
printer_name = None
username = prop.username
mode = GUI_MODE
mode_specified = False
faxnum_list = []
recipient_list = []
group_list = []
bus = device.DEFAULT_PROBE_BUS

try:
    opts, args = getopt.getopt(sys.argv[1:],'l:hz:d:p:b:g:unf:r:', 
        ['device=', 'printer=', 'level=', 
         'help', 'help-rest', 
         'help-man', 'logfile=', 'bus=',
         'gui', 'non-interactive'
         'faxnum=', 'recipients=',
         'gg', 'groups', 'help-desc'])

except getopt.GetoptError, e:
    log.error(e)
    sys.exit(1)
    

if os.getenv("HPLIP_DEBUG"):
    log.set_level('debug')

for o, a in opts:
    if o in ('-l', '--logging'):
        log_level = a.lower().strip()
        if not log.set_level(log_level):
            usage()
            
    elif o == '--gg':
        log.set_level('debug')
            
    elif o in ('-z', '--logfile'):
        log.set_logfile(a)
        log.set_where(log.LOG_TO_CONSOLE_AND_FILE)

    elif o in ('-h', '--help'):
        usage()
        
    elif o == '--help-rest':
        usage('rest')
        
    elif o == '--help-man':
        usage('man')
        
    elif o == '--help-desc':
        print __doc__,
        sys.exit(0)
    
    elif o in ('-d', '--device'):
        device_uri = a

    elif o in ('-p', '--printer'):
        printer_name = a
        
    elif o in ('-b', '--bus'):
        bus = a.lower().strip()
        if not device.validateBusList(bus):
            usage()

    elif o in ('-n', '--non-interactive'):
        if mode_specified:
            log.error("You may only specify a single mode as a parameter (-n or -u).")
            sys.exit(1)

        mode = NON_INTERACTIVE_MODE
        mode_specified = True
        
    elif o in ('-u', '--gui'):
        if mode_specified:
            log.error("You may only specify a single mode as a parameter (-n or -u).")
            sys.exit(1)

        mode = GUI_MODE
        mode_specified = True
        
    elif o in ('-f', '--faxnum'):
        faxnum_list.extend(a.split(','))
        
    elif o in ('-r', '--recipient'):
        recipient_list.extend(a.split(','))
        
    elif o in ('-g', '--group'):
        group_list.extend(a.split(','))
        
        
utils.log_title(__title__, __version__)

# Security: Do *not* create files that other users can muck around with
os.umask (0077)

if mode == GUI_MODE:
    if not os.getenv('DISPLAY'):
        mode = NON_INTERACTIVE_MODE
    
    elif not utils.checkPyQtImport():
        mode = NON_INTERACTIVE_MODE

if mode == GUI_MODE:
    app = None
    sendfax = None
    client = None
    
    from qt import *
    
    # UI Forms
    from ui.faxsendjobform import FaxSendJobForm

    try:
        client = fax_client(username)
    except Error:
        log.error("Unable to create client object.")
        sys.exit(1)
    except socket.error:
        log.error("Unable to connect to HPLIP I/O. Please (re)start HPLIP and try again.")
        sys.exit(1)
        
    # create the main application object
    app = QApplication(sys.argv)
    
    sendfax = FaxSendJobForm(client.socket,
                             device_uri,  
                             printer_name, 
                             args) 
                             
    app.setMainWidget(sendfax)
    
    pid = os.getpid()
    log.debug('pid=%d' % pid)
    
    sendfax.show()
    
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
    
    user_config = os.path.expanduser('~/.hplip.conf')
    loc = utils.loadTranslators(app, user_config)
    
    try:
        log.debug("Starting GUI loop...")
        app.exec_loop()
    except KeyboardInterrupt:
        pass
    except:
        log.exception()
        
else: # NON_INTERACTIVE_MODE
    import struct, Queue

    from prnt import cups
    from base import magic, msg

    try:
        from fax import fax
    except ImportError:
        # This can fail on Python < 2.3 due to the datetime module
        log.error("Fax address book disabled - Python 2.3+ required.")
        sys.exit(1)    

    db =  fax.FaxAddressBook() # kirbybase instance

    phone_num_list = []
    
    log.debug("Faxnum list = %s" % faxnum_list)
    faxnum_list = utils.uniqueList(faxnum_list)
    log.debug("Unique list=%s" % faxnum_list)
    
    for f in faxnum_list:
        for c in f:
            if c not in '0123456789-(+) ':
                log.error("Invalid character in fax number '%s'. Only the characters '0123456789-(+) ' are valid." % f)
                sys.exit(1)
    
    log.debug("Group list = %s" % group_list)
    group_list = utils.uniqueList(group_list)
    log.debug("Unique list=%s" % group_list)

    for g in group_list:
        entries = db.GroupEntries(g)
        for e in entries:
            recipient_list.append(e)
    
    log.debug("Recipient list = %s" % recipient_list)
    recipient_list = utils.uniqueList(recipient_list)
    log.debug("Unique list=%s" % recipient_list)
    
    for r in recipient_list:
        if not db.select(['name'], [r]):
            log.error("Unknown fax recipient '%s' in the recipient list." % r)
            all_entries = db.AllRecordEntries()
            log.info(utils.bold("\nKnown recipients (entries):"))
            
            for a in all_entries:
                log.info(a.name)
            
            print
            sys.exit(1)
    

    for p in recipient_list:
        a = fax.AddressBookEntry(db.select(['name'], [p])[0])
        phone_num_list.append(a)
        log.debug("Name=%s Number=%s" % (a.name, a.fax))
        
    for p in faxnum_list:
        a = fax.AddressBookEntry((-1, "Unknown", "Unknown", "Unknown", "Unknown", p, "", ""))
        phone_num_list.append(a)
        log.debug("Name=%s Number=%s" % (a.name, a.fax))
        
    log.debug("Phone num list = %s" % phone_num_list)

    if not phone_num_list:
        log.error("No recipients specified. Please use -f, -r, and/or -g to specify recipients.")
        usage()
    
    allowable_mime_types = cups.getAllowableMIMETypes()
    allowable_mime_types.append("application/hplip-fax")
    allowable_mime_types.append("application/x-python")
    
    
    for f in args:
        path = os.path.realpath(f)
        log.debug(path)
        
        if os.path.exists(path):
            mime_type = magic.mime_type(path)
            log.debug(mime_type)
        else:
            log.error("File '%s' does not exist." % path)
            sys.exit(1)
            
        if mime_type not in allowable_mime_types:
            log.error("File '%s' has a non-allowed mime-type of '%s'" % (path, mime_type))
            sys.exit(1)
            
    if printer_name:
        printer_list = cups.getPrinters()
        found = False
        for p in printer_list:
            if p.name == printer_name:
                device_uri = p.device_uri
                found = True
                break
    
        if not found:
            log.error("Unknown printer name: %s" % printer_name)
            sys.exit(1)
            
        if not p.device_uri.startswith('hpfax:/'):
            log.error("You must specify a printer that has a device URI in the form 'hpfax:/'")
            sys.exit(1)
            
    if device_uri and not printer_name:
        cups_printers = cups.getPrinters()
        
        max_printer_size = 20
        printers = []
        for p in cups_printers:
            back_end, is_hp, bus, model, serial, dev_file, host, port = \
                device.parseDeviceURI(p.device_uri)
                
            if back_end == 'hpfax' and p.device_uri == device_uri:
                printers.append((p.name, p.device_uri))
                max_printer_size = max(len(p.name), max_printer_size)
                
        if not printers:
            log.error("No CUPS queue found for device %s" % device_uri)
            sys.exit(1)
        
        elif len(printers) == 1:
            printer_name = printers[0][0]
            
        else:
            log.info(utils.bold("\nChoose printer (fax queue) from installed printers in CUPS:\n"))
            
            formatter = utils.TextFormatter(
                    (
                        {'width': 4},
                        {'width': max_printer_size, 'margin': 2},
                    )
                )
            
            log.info(formatter.compose(("Num.", "CUPS Printer (queue)")))
            log.info(formatter.compose(('-'*4, '-'*(max_printer_size), )))
            
            i = 0
            for p in printers:
                log.info(formatter.compose((str(i), p[0])))
                i += 1
            
            while 1:
                user_input = raw_input(utils.bold("\nEnter number 0...%d for printer (q=quit) ?" % (i-1)))
    
                if user_input == '':
                    log.warn("Invalid input - enter a numeric value or 'q' to quit.")
                    continue
    
                if user_input.strip()[0] in ('q', 'Q'):
                    sys.exit(1)
    
                try:
                    x = int(user_input)
                except ValueError:
                    log.warn("Invalid input - enter a numeric value or 'q' to quit.")
                    continue
    
                if x < 0 or x > (i-1):
                    log.warn("Invalid input - enter a value between 0 and %d or 'q' to quit." % (i-1))
                    continue
    
                break
            
            print printers[x]
            printer_name = printers[x][0]
        
    
    if not device_uri and not printer_name:
        cups_printers = cups.getPrinters()
        log.debug(cups_printers)
        
        printers = []
        max_deviceid_size, max_printer_size = 0, 0
        
        for p in cups_printers:
            back_end, is_hp, bus, model, serial, dev_file, host, port = \
                device.parseDeviceURI(p.device_uri)
                
            if back_end == 'hpfax':
                printers.append((p.name, p.device_uri))
                max_deviceid_size = max(len(p.device_uri), max_deviceid_size)
                max_printer_size = max(len(p.name), max_printer_size)
                
        if not printers:
            log.error("No devices found.")
            sys.exit(1)
                
        if len(printers) == 1:
            printer_name, device_uri = printers[0]
        
        else:
            log.info(utils.bold("\nChoose printer (fax queue) from installed printers in CUPS:\n"))
            
            formatter = utils.TextFormatter(
                    (
                        {'width': 4},
                        {'width': max_printer_size, 'margin': 2},
                        {'width': max_deviceid_size, 'margin': 2},
                    )
                )
            
            log.info(formatter.compose(("Num.", "CUPS Printer", "Device URI")))
            log.info(formatter.compose(('-'*4, '-'*(max_printer_size), '-'*(max_deviceid_size))))
            
            i = 0
            for p in printers:
                log.info(formatter.compose((str(i), p[0], p[1])))
                i += 1
            
            while 1:
                user_input = raw_input(utils.bold("\nEnter number 0...%d for printer (q=quit) ?" % (i-1)))
    
                if user_input == '':
                    log.warn("Invalid input - enter a numeric value or 'q' to quit.")
                    continue
    
                if user_input.strip()[0] in ('q', 'Q'):
                    sys.exit(1)
    
                try:
                    x = int(user_input)
                except ValueError:
                    log.warn("Invalid input - enter a numeric value or 'q' to quit.")
                    continue
    
                if x < 0 or x > (i-1):
                    log.warn("Invalid input - enter a value between 0 and %d or 'q' to quit." % (i-1))
                    continue
    
                break
            
            print printers[x]
            printer_name, device_uri = printers[x]
            
            
    log.info(utils.bold("Using printer %s (%s)" % (printer_name, device_uri)))

    ppd_file = cups.getPPD(printer_name)

    if ppd_file is not None and os.path.exists(ppd_file):
        if file(ppd_file, 'r').read(8192).find('HP Fax') == -1:
            log.error("Fax configuration error. The CUPS fax queue for '%s' is incorrectly configured. Please make sure that the CUPS fax queue is configured with the 'HP Fax' Model/Driver." % printer_name)
            sys.exit(1)
    
    hpssd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        hpssd_sock.connect((prop.hpssd_host, prop.hpssd_port))
    except socket.error:
        log.error("Unable to contact HPLIP I/O (hpssd).")
        sys.exit(1) 
     
    out_buffer = buildMessage("RegisterGUIEvent", None, 
                              {'type': 'fax', 
                               'username': username})
    
    hpssd_sock.send(out_buffer)
                        
    
    if not args:
        log.error("No files specfied to send. Please specify the file(s) to send on the command line.")
        usage()
    
    file_list = []
    
    for f in args:
        
        #
        # Submit each file to CUPS for rendering by hpijsfax
        #
        path = os.path.realpath(f)
        log.debug(path)
        mime_type = magic.mime_type(path)
        
        if mime_type == 'application/hplip-fax': # .g3
            log.info("\nPreparing fax file %s..." % f)
            fax_file_fd = file(f, 'r')
            header = fax_file_fd.read(fax.FILE_HEADER_SIZE)
            fax_file_fd.close()
            
            mg, version, pages, hort_dpi, vert_dpi, page_size, \
                resolution, encoding, reserved1, reserved2 = struct.unpack(">8sBIHHBBBII", header)

            if mg != 'hplip_g3':
                log.error("%s: Invalid file header. Bad magic." % f)
                sys.exit(1)
            
            file_list.append((f, mime_type, "", "", pages))
            
        else:
            all_pages = True 
            page_range = ''
            page_set = 0
            nup = 1
    
            cups.resetOptions()
    
            if mime_type in ["application/x-cshell",
                             "application/x-perl",
                             "application/x-python",
                             "application/x-shell",
                             "text/plain",]:
    
                cups.addOption('prettyprint')
    
            if nup > 1:
                cups.addOption('number-up=%d' % nup)
    
            cups_printers = cups.getPrinters()
            #log.debug(self.cups_printers)
            
            printer_state = cups.IPP_PRINTER_STATE_STOPPED
            for p in cups_printers:
                if p.name == printer_name:
                    printer_state = p.state
                    
            log.debug("Printer state = %d" % printer_state)
            
            if printer_state == cups.IPP_PRINTER_STATE_IDLE:
                log.debug("Printer name = %s file = %s" % (printer_name, path))
                sent_job_id = cups.printFile(printer_name, path, os.path.basename(path))
                log.info("\nRendering file '%s' (job %d)..." % (path, sent_job_id))
                log.debug("Job ID=%d" % sent_job_id)
            else:
                log.error("The CUPS queue for '%s' is in a stopped or busy state. Please check the queue and try again." % printer_name)
                sys.exit(1)
        
            cups.resetOptions()
            
            #
            # Wait for the EVENT_FAX_RENDER_COMPLETE message
            #
            
            cont = True
            while cont: # TODO: timeout
                update_spinner()
                r, w, e = select.select([hpssd_sock], [], [], 1)
            
                if not r:
                    continue
            
                remaining_msg = hpssd_sock.recv(prop.max_message_read)
                
                while remaining_msg:
                    try:
                        fields, payload, remaining_msg = parseMessage(remaining_msg)
                    except Error, e:
                        err = e.opt
                        continue
    
                    event_code = fields.get('event-code', 0)
                    job_id = fields.get('job-id', -1)
                    
                    #print job_id, event_code
                    
                    log.debug("Rec'd msg: event_code=%d job_id=%d" % (event_code, job_id))
                    
                    if event_code == EVENT_END_FAX_PRINT_JOB:
                        continue
                    
                    if event_code == EVENT_FAX_RENDER_DISTANT_EARLY_WARNING:
                        log.debug("Fax data is arriving soon...")
                        continue
                    
                    if  event_code == EVENT_FAX_RENDER_COMPLETE and \
                       job_id == sent_job_id:
                       
                        title = fields['title']
                        log.info("Fax rendering complete for job %d!" % sent_job_id)
                        cont = False
                        break
            
            cleanup_spinner()
            
            #
            # Transfer the rendered data from hpssd to a .g3 file
            #
            log.info("\nTransfering fax data...")
            
            fax_dir = os.path.expanduser("~/hpfax")
    
            if not os.path.exists(fax_dir):
                os.mkdir(fax_dir)
    
            fax_file = os.path.expanduser(os.path.join(fax_dir, "hpfax-%d.g3" % sent_job_id))
            log.debug("Fax file = %s" % fax_file)
            
            fd = file(fax_file, 'w')
            bytes_read = 0
            header_read = False
            total_pages = 0
    
            while True:
                fields, data, result_code = \
                    msg.xmitMessage(hpssd_sock, "FaxGetData", None,
                                     {"username": username,
                                      "job-id": sent_job_id,
                                     })
    
                #log.debug(repr(data)), len(data)
                
                if len(data) and result_code == ERROR_SUCCESS:
                    fd.write(data)
                    bytes_read += len(data)
    
                    if not header_read and len(data) >= fax.FILE_HEADER_SIZE:
                        mg, version, total_pages, hort_dpi, vert_dpi, page_size, \
                            resolution, encoding, reserved1, reserved2 = \
                            struct.unpack(">8sBIHHBBBII", data[:fax.FILE_HEADER_SIZE])
    
                        log.debug("Magic=%s Ver=%d Pages=%d hDPI=%d vDPI=%d Size=%d Res=%d Enc=%d" %
                                  (mg, version, total_pages, hort_dpi, vert_dpi, page_size, resolution, encoding))
    
                        header_read = True
    
                else:
                    break
    
            fd.close()
            log.debug("Transfered %d bytes" % bytes_read)
            file_list.append((fax_file, mime_type, "", title, total_pages))

    #
    # Insure that the device is in an OK state
    #
    
    log.debug("\nChecking device state...")
    try:
        dev = fax.FaxDevice(device_uri=device_uri, 
                            printer_name=printer_name)
                        
        #try:
        if 1:
            try:
                dev.open()
            except Error, e:
                log.warn(e.msg)

            try:
                dev.queryDevice(quick=True)
            except Error, e:
                log.error("Query device error (%s)." % e.msg)
                dev.error_state = ERROR_STATE_ERROR

        #finally:
        
        #dev.close()

        if dev.error_state in (ERROR_STATE_WARNING, ERROR_STATE_ERROR, ERROR_STATE_BUSY):
            log.error("Device is busy or in an error state (code=%d). Please wait for the device to become idle or clear the error and try again." % dev.error_state)
            sys.exit(1)

        log.debug("File list:")

        for f in file_list:
            log.debug(str(f))

        service.sendEvent(hpssd_sock, EVENT_START_FAX_JOB, device_uri=device_uri)

        update_queue = Queue.Queue()
        event_queue = Queue.Queue()

        log.info("\nSending fax...")
        if not dev.sendFaxes(phone_num_list, file_list, "", 
                             "", None, printer_name,
                             update_queue, event_queue):

            log.error("Send fax is active. Please wait for operation to complete.")
            service.sendEvent(hpssd_sock, EVENT_FAX_JOB_FAIL, device_uri=device_uri)
            sys.exit(1)

        try:
            cont = True
            while cont:
                #print "1"
                while update_queue.qsize():
                    #print "2"
                    try:
                        status, page_num, phone_num = update_queue.get(0)
                    except Queue.Empty:
                        break
        
                    #print status, page_num, phone_num
                    
                    if status == fax.STATUS_IDLE:
                        log.debug("Idle")
                        
                    elif status == fax.STATUS_PROCESSING_FILES:
                        log.info("\nProcessing page %d" % page_num)
        
                    elif status == fax.STATUS_DIALING:
                        log.info("\nDialing %s..." % phone_num)
        
                    elif status == fax.STATUS_CONNECTING:
                        log.info("\nConnecting to %s..." % phone_num)
        
                    elif status == fax.STATUS_SENDING:
                        log.info("\nSending page %d to %s..." % (page_num, phone_num))
        
                    elif status == fax.STATUS_CLEANUP:
                        log.info("\nCleaning up...")
        
                    elif status in (fax.STATUS_ERROR, fax.STATUS_BUSY, fax.STATUS_COMPLETED):
                        cont = False
                        
                        if status  == fax.STATUS_ERROR:
                            log.error("Fax send error.")
                            service.sendEvent(hpssd_sock, EVENT_FAX_JOB_FAIL, device_uri=device_uri)
        
                        elif status == fax.STATUS_BUSY:
                            log.error("Fax device is busy. Please try again later.")
                            service.sendEvent(hpssd_sock, EVENT_FAX_JOB_FAIL, device_uri=device_uri)
        
                        elif status == fax.STATUS_COMPLETED:
                            log.info("\nCompleted successfully.")
                            service.sendEvent(hpssd_sock, EVENT_END_FAX_JOB, device_uri=device_uri)
                        
                update_spinner()
                time.sleep(2)
                
            cleanup_spinner()
        
        except KeyboardInterrupt:
            event_queue.put((fax.EVENT_FAX_SEND_CANCELED, '', '', ''))
            service.sendEvent(hpssd_sock, EVENT_FAX_JOB_CANCELED, device_uri=device_uri)
            log.error("Cancelling...")
            
        dev.waitForSendFaxThread()
    
    finally:
        dev.close()
        service.sendEvent(hpssd_sock, EVENT_END_FAX_JOB, device_uri=device_uri)
        hpssd_sock.close()
        
    log.info("\nDone.")
    

sys.exit(0)

