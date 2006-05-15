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

__version__ = '2.1'
__title__ = 'PC Sendfax Utility'
__doc__ = "Allows for sending faxes from the PC using HPLIP supported multifunction printers. The utility can be invoked directly, or by printing to the appropriate fax CUPS printer." 

# Std Lib
import sys, socket, os, os.path, getopt, signal, atexit
import ConfigParser, pwd, socket

# Local
from base.g import *
from base.msg import *
import base.utils as utils
import base.async_qt as async
from base import service, device

app = None
sendfax = None
client = None

# PyQt
if not utils.checkPyQtImport():
    sys.exit(0)

from qt import *

# UI Forms
from ui.faxsendjobform import FaxSendJobForm


USAGE = [(__doc__, "", "name", True),
         ("Usage: hp-sendfax [PRINTER|DEVICE-URI] [OPTIONS] [FILES]", "", "summary", True),
         utils.USAGE_ARGS,
         utils.USAGE_DEVICE,
         utils.USAGE_PRINTER,
         utils.USAGE_SPACE,
         utils.USAGE_OPTIONS,
         utils.USAGE_BUS1, utils.USAGE_BUS2,         
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
         utils.USAGE_HELP,
         ("[FILES]", "", "header", False),
         ("An optional list of files to add to the fax job.", "", "option", True),
         utils.USAGE_NOTES,
         utils.USAGE_STD_NOTES1,
         utils.USAGE_STD_NOTES2,
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





def main(args):
    prop.prog = sys.argv[0]
    
    device_uri = None
    printer_name = None
    username = prop.username

    try:
        opts, args = getopt.getopt(sys.argv[1:],'l:hz:d:p:b:g', 
            ['device=', 'printer=', 'level=', 
             'help', 'help-rest', 
             'help-man', 'logfile=', 'bus='])

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
                
        elif o == '-g':
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
            
        elif o in ('-d', '--device'):
            device_uri = a

        elif o in ('-p', '--printer'):
            printer_name = a
            
        elif o in ('-b', '--bus'):
            bus = a.lower().strip()
            if not device.validateBusList(bus):
                usage()
            
            
    utils.log_title(__title__, __version__)
    
    # Security: Do *not* create files that other users can muck around with
    os.umask (0077)
    log.set_module('sendfax')

    global client
    try:
        client = fax_client(username)
    except Error:
        log.error("Unable to create client object.")
        sys.exit(1)
    except socket.error:
        log.error("Unable to connect to HPLIP I/O. Please (re)start HPLIP and try again.")
        sys.exit(1)
        
    # create the main application object
    global app
    app = QApplication(sys.argv)

    global sendfax
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

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
