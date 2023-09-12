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


__version__ = '1.2'
__title__ = "Make Copies Utility"
__doc__ = "A GUI front end for making copies on all-in-ones and MFP devices."


# Std Lib
import sys, os, getopt, re, socket, Queue, time

# Local
from base.g import *
from base.msg import *
from base import utils, device, pml, service
from copier import copier
import base.async_qt as async
from prnt import cups

log.set_module('hp-makecopies')


class makecopies_client(async.dispatcher):

    def __init__(self):
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
                        'eventgui' : self.handle_eventgui,
                        'unknown' : self.handle_unknown,
                        'exitguievent' : self.handle_exitguievent,
                        }

        self.register_gui()

    def handle_read(self):
        log.debug("Reading data on channel (%d)" % self._fileno)
        log.debug(repr(self.in_buffer))

        self.in_buffer = self.recv(prop.max_message_len)

        if self.in_buffer == '':
            return False

        remaining_msg = self.in_buffer

        while True:
            try:
                self.fields, self.data, remaining_msg = parseMessage(remaining_msg)
            except Error, e:
                log.debug(repr(self.in_buffer))
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
            if makecopiesdlg is not None:
                makecopiesdlg.close()
            qApp.quit()

        return ''

    # EVENT
    def handle_eventgui(self):
        global makecopiesdlg
        try:
            job_id = self.fields['job-id']
            event_code = self.fields['event-code']
            event_type = self.fields['event-type']
            retry_timeout = self.fields['retry-timeout']
            lines = self.data.splitlines()
            error_string_short, error_string_long = lines[0], lines[1]
            device_uri = self.fields['device-uri']

            log.debug("Event: %d '%s'" % (event_code, event_type))

            makecopiesdlg.EventUI(event_code, event_type, error_string_short,
                             error_string_long, retry_timeout, job_id,
                             device_uri)

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

    def register_gui(self):
        out_buffer = buildMessage("RegisterGUIEvent", None, 
                                  {'type': 'print', 
                                   'username': prop.username})
        self.send(out_buffer)


USAGE = [(__doc__, "", "name", True),
         ("Usage: hp-makecopies [PRINTER|DEVICE-URI] [MODE] [OPTIONS]", "", "summary", True),
         utils.USAGE_ARGS,
         utils.USAGE_DEVICE,
         ("To specify a CUPS printer:", "-P<printer>, -p<printer> or --printer=<printer>", "option", False),
         utils.USAGE_SPACE,
         ("[MODE]", "", "header", False),
         ("Enter graphical UI mode:", "-u or --gui (Default)", "option", False),
         ("Run in non-interactive mode (batch mode):", "-n or --non-interactive", "option", False),
         utils.USAGE_SPACE,
         utils.USAGE_OPTIONS,
         ("Number of copies:", "-m<num_copies> or --copies=<num_copies> or --num=<num_copies> (1-99)", "option", False),
         ("Reduction/enlargement:", "-r<%> or --reduction=<%> or --enlargement=<%> (25-400%)", "option", False),
         ("Quality:", "-q<quality> or --quality=<quality> (where quality is: 'fast', 'draft', 'normal', 'presentation', or 'best')", "option", False),
         ("Contrast:", "-c<contrast> or --contrast=<contrast> (-5 to +5)", "option", False),
         ("Fit to page (flatbed only):", "-f or --fittopage or --fit (overrides reduction/enlargement)", "option", False),
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
         utils.USAGE_HELP,
         utils.USAGE_SPACE,
         utils.USAGE_NOTES,
         utils.USAGE_STD_NOTES1, utils.USAGE_STD_NOTES2, 
         ("3. If any copy parameter is not specified (contrast, reduction, etc), the default values from the device are used.", "", "note", False),
         ]
                 

def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)
        
    utils.format_text(USAGE, typ, __title__, 'hp-makecopies', __version__)
    sys.exit(0)


try:
    opts, args = getopt.getopt(sys.argv[1:], 'P:p:d:hl:gm:c:q:r:fun',
                               ['printer=', 'device=', 'help', 'logging=',
                                'num=', 'copies=', 'contrast=', 'quality='
                                'reduction=', 'enlargement=', 'fittopage', 
                                'fit', 'gui', 'help-rest', 'help-man',
                                'non-interactive'])
except getopt.GetoptError:
    usage()

printer_name = None
device_uri = None
log_level = logger.DEFAULT_LOG_LEVEL
bus = 'cups'
num_copies = None
reduction = None
reduction_spec = False
contrast = None
quality = None
fit_to_page = None
mode = GUI_MODE
mode_specified = False

if os.getenv("HPLIP_DEBUG"):
    log.set_level('debug')

for o, a in opts:
    if o in ('-h', '--help'):
        usage()
        
    elif o == '--help-rest':
        usage('rest')
        
    elif o == '--help-man':
        usage('man')

    elif o in ('-p', '-P', '--printer'):
        printer_name = a

    elif o in ('-d', '--device'):
        device_uri = a

    elif o in ('-l', '--logging'):
        log_level = a.lower().strip()
        if not log.set_level(log_level):
            usage()

    elif o == '-g':
        log.set_level('debug')
        
    elif o in ('-m', '--num', '--copies'):
        try:
            num_copies = int(a)
        except ValueError:
            log.warning("Invalid number of copies. Set to default of 1.")
            num_copies = 1
            
        if num_copies < 1: 
            log.warning("Invalid number of copies. Set to minimum of 1.")
            num_copies = 1
            
        elif num_copies > 99: 
            log.warning("Invalid number of copies. Set to maximum of 99.")
            num_copies = 99
            
    elif o in ('-c', '--contrast'):
        try:
            contrast = int(a)
        except ValueError:
            log.warning("Invalid contrast setting. Set to default of 0.")
            contrast = 0
            
        if contrast < -5: 
            log.warning("Invalid contrast setting. Set to minimum of -5.")
            contrast = -5
            
        elif contrast > 5: 
            log.warning("Invalid contrast setting. Set to maximum of +5.")
            contrast = 5
            
        contrast *= 25
            
    elif o in ('-q', '--quality'):
        a = a.lower().strip()
        
        if a == 'fast':
            quality = pml.COPIER_QUALITY_FAST
        
        elif a.startswith('norm'):
            quality = pml.COPIER_QUALITY_NORMAL
        
        elif a.startswith('pres'):
            quality = pml.COPIER_QUALITY_PRESENTATION
        
        elif a.startswith('draf'):
            quality = pml.COPIER_QUALITY_DRAFT
        
        elif a == 'best':
            quality = pml.COPIER_QUALITY_BEST
        
        else:
            log.warning("Invalid quality. Set to default of 'normal'.")
            
    elif o in ('-r', '--reduction', '--enlargement'):
        reduction_spec = True
        try:
            reduction = int(a.replace('%', ''))
        except ValueError:
            log.warning("Invalid reduction %. Set to default of 100%.")
            reduction = 100
            
        if reduction < 25:
            log.warning("Invalid reduction %. Set to minimum of 25%.")
            reduction = 25
            
        elif reduction > 400:
            log.warning("Invalid reduction %. Set to maximum of 400%.")
            reduction = 400
            
    elif o in ('-f', '--fittopage', '--fit'):
        fit_to_page = pml.COPIER_FIT_TO_PAGE_ENABLED
            
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
    
            
if fit_to_page == pml.COPIER_FIT_TO_PAGE_ENABLED and reduction_spec:
    log.warning("Fit to page specfied: Reduction/enlargement parameter ignored.")


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
    makecopiesdlg = None
    client = None

    from qt import *
    from ui.makecopiesform import MakeCopiesForm
    
    try:
        client = makecopies_client()
    except Error:
        log.error("Unable to create client object.")
        sys.exit(0)

    # create the main application object
    app = QApplication(sys.argv)

    makecopiesdlg = MakeCopiesForm(client.socket, bus, device_uri, printer_name, 
                                   num_copies, contrast, quality, reduction, fit_to_page)
                                   
    makecopiesdlg.show()
    app.setMainWidget(makecopiesdlg)

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
    if not device_uri and not printer_name:
        try:
            device_uri = device.getInteractiveDeviceURI(bus='cups')
            if device_uri is None:
                sys.exit(1)
        except Error:
            log.error("Error occured during interactive mode. Exiting.")
            sys.exit(1)
            
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((prop.hpssd_host, prop.hpssd_port))
    except socket.error:
        log.error("Unable to connect to HPLIP I/O (hpssd).")
        sys.exit(1)
    
    dev = copier.PMLCopyDevice(device_uri, printer_name, 
                               sock)
                               
                               
    if dev.copy_type != COPY_TYPE_DEVICE:
        log.error("Sorry, make copies functionality is not implemented for this device type.")
        sys.exit(1)
        
    try:
        dev.open()
        
        if num_copies is None:
            result_code, num_copies = dev.getPML(pml.OID_COPIER_NUM_COPIES)
            
        if contrast is None:
            result_code, contrast = dev.getPML(pml.OID_COPIER_CONTRAST)
            
        if reduction is None:
            result_code, reduction = dev.getPML(pml.OID_COPIER_REDUCTION)
        
        if quality is None:
            result_code, quality = dev.getPML(pml.OID_COPIER_QUALITY)
        
        if fit_to_page is None:
            result_code, fit_to_page = dev.getPML(pml.OID_COPIER_FIT_TO_PAGE)
        
        result_code, max_reduction = dev.getPML(pml.OID_COPIER_REDUCTION_MAXIMUM)
        result_code, max_enlargement = dev.getPML(pml.OID_COPIER_ENLARGEMENT_MAXIMUM)
    
    except Error, e:
        log.error(e.msg)
        sys.exit(1)
    
    #print num_copies, contrast, reduction, quality, fit_to_page, max_reduction, max_enlargement
    log.debug("num_copies = %d" % num_copies)
    log.debug("contrast= %d" % contrast)
    log.debug("reduction = %d" % reduction)
    log.debug("quality = %d" % quality)
    log.debug("fit_to_page = %d" % fit_to_page)
    log.debug("max_reduction = %d" % max_reduction)
    log.debug("max_enlargement = %d" % max_enlargement)
    
    update_queue = Queue.Queue()
    event_queue = Queue.Queue()
    
    dev.copy(num_copies, contrast, reduction,
             quality, fit_to_page, 
             update_queue, event_queue)
    
    try:
        cont = True
        while cont:
            while update_queue.qsize():
                try:
                    status = update_queue.get(0)
                except Queue.Empty:
                    break
    
                if status == copier.STATUS_IDLE:
                    log.debug("Idle")
                    continue
    
                elif status in (copier.STATUS_SETTING_UP, copier.STATUS_WARMING_UP):
                    log.info("Warming up...")
                    continue
    
                elif status == copier.STATUS_ACTIVE:
                    log.info("Copying...")
                    continue
    
                elif status in (copier.STATUS_ERROR, copier.STATUS_DONE):
    
                    if status == copier.STATUS_ERROR:
                        log.error("Copier error!")
                        service.sendEvent(sock, EVENT_COPY_JOB_FAIL, device_uri=device_uri)
                        cont = False
                        break
    
                    elif status == copier.STATUS_DONE:
                        cont = False
                        break
            
            time.sleep(2)
    
    except KeyboardInterrupt:
        event_queue.put(copier.COPY_CANCELED)
        service.sendEvent(sock, EVENT_COPY_JOB_CANCELED, device_uri=device_uri)            
        log.error("Cancelling...")
    
    dev.close()

    dev.waitForCopyThread()
    service.sendEvent(sock, EVENT_END_COPY_JOB, device_uri=device_uri)
    log.info("Done.")

sys.exit(0)

