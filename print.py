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

__version__ = '2.0'
__title__ = 'Print Utility'
__doc__ = "A simple front end to 'lp'. Provides a print UI from the Device Manager if kprinter, gtklp, or xpp are not installed."

# Std Lib
import sys, os, getopt, re, socket

# Local
from base.g import *
from base.msg import *
from base import utils, device
import base.async_qt as async
from prnt import cups

log.set_module('hp-print')

app = None
printdlg = None
client = None

USAGE = [(__doc__, "", "name", True),
         ("Usage: hp-print [PRINTER|DEVICE-URI] [OPTIONS] [FILE LIST]", "", "summary", True),
         utils.USAGE_ARGS,
         utils.USAGE_DEVICE,
         ("To specify a CUPS printer:", "-P<printer>, -p<printer> or --printer=<printer>", "option", False),
         utils.USAGE_SPACE,
         utils.USAGE_OPTIONS,
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
         utils.USAGE_HELP,
         ("[FILELIST]", "", "heading", False),
         ("Optional list of files:", """Space delimited list of files to print. Files can also be selected for print by adding them to the file list in the UI.""", "option", False),
         utils.USAGE_SPACE,
         utils.USAGE_NOTES,
         utils.USAGE_STD_NOTES1, utils.USAGE_STD_NOTES2, 
         ]
                 

def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)
        
    utils.format_text(USAGE, typ, __title__, 'hp-print', __version__)
    sys.exit(0)



class print_client(async.dispatcher):

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
            if printdlg is not None:
                printdlg.close()
            qApp.quit()

        return ''

    # EVENT
    def handle_eventgui(self):
        global printdlg
        try:
            job_id = self.fields['job-id']
            event_code = self.fields['event-code']
            event_type = self.fields['event-type']
            retry_timeout = self.fields['retry-timeout']
            lines = self.data.splitlines()
            error_string_short, error_string_long = lines[0], lines[1]
            device_uri = self.fields['device-uri']

            log.debug("Event: %d '%s'" % (event_code, event_type))

            printdlg.EventUI(event_code, event_type, error_string_short,
                             error_string_long, retry_timeout, job_id,
                             device_uri)

        except:
            log.exception()

        return ''

    def handle_unknown(self):
        #return buildResultMessage('MessageError', None, ERROR_INVALID_MSG_TYPE)
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


try:
    opts, args = getopt.getopt(sys.argv[1:], 'P:p:d:hl:g',
                               ['printer=', 'device=', 'help', 
                                'help-rest', 'help-man', 'logging=', 'help-desc'])
except getopt.GetoptError:
    usage()

printer_name = None
device_uri = None
log_level = logger.DEFAULT_LOG_LEVEL
bus = 'cups'

if os.getenv("HPLIP_DEBUG"):
    log.set_level('debug')

for o, a in opts:
    if o in ('-h', '--help'):
        usage()

    elif o == '--help-rest':
        usage('rest')
        
    elif o == '--help-man':
        usage('man')

    elif o == '--help-desc':
        print __doc__,
        sys.exit(0)
    
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


# Security: Do *not* create files that other users can muck around with
os.umask (0077)

utils.log_title(__title__, __version__)

# PyQt
if not utils.checkPyQtImport():
    log.error("PyQt/Qt initialization error. Please check install of PyQt/Qt and try again.")
    sys.exit(1)

from qt import *
from ui.printerform import PrinterForm

try:
    client = print_client()
except Error:
    log.error("Unable to create client object.")
    sys.exit(0)

# create the main application object
app = QApplication(sys.argv)

printdlg = PrinterForm(client.socket, bus, device_uri, printer_name, args)
printdlg.show()
app.setMainWidget(printdlg)

user_config = os.path.expanduser('~/.hplip.conf')
loc = utils.loadTranslators(app, user_config)

try:
    log.debug("Starting GUI loop...")
    app.exec_loop()
except KeyboardInterrupt:
    pass
except:
    log.exception()

sys.exit(0)


