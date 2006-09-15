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

__version__ = '6.2'
__title__ = 'HP Device Manager'
__doc__ = "The HP Device Manager (aka Toolbox) for HPLIP supported devices. Provides status, tools, and supplies levels."

# Std Lib
import sys
import socket
import os, os.path
import getopt
import signal
import atexit

# Local
from base.g import *

import base.utils as utils
from base.msg import *
from base import service

log.set_module('hp-toolbox')

# UI Forms and PyQt

pyqt_ok = True
try:
    import base.async_qt as async
except ImportError:
    pyqt_ok = False
    
if pyqt_ok:
    pyqt_ok = utils.checkPyQtImport()
    
if not pyqt_ok:
    log.error("PyQt/Qt initialization error. Please check install of PyQt/Qt and try again.")
    sys.exit(1)
    
from qt import *
from ui.devmgr4 import devmgr4


app = None
client = None
toolbox  = None
hpiod_sock = None


USAGE = [(__doc__, "", "name", True),
         ("Usage: hp-toolbox [OPTIONS]", "", "summary", True),
         utils.USAGE_OPTIONS,
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
         utils.USAGE_HELP,
         utils.USAGE_SEEALSO,
         ("hp-info", "", "seealso", False),
         ("hp-clean", "", "seealso", False),
         ("hp-colorcal", "", "seealso", False),
         ("hp-align", "", "seealso", False),
         ("hp-print", "", "seealso", False),
         ("hp-sendfax", "", "seealso", False),
         ("hp-fab", "", "seealso", False),
         ("hp-testpage", "", "seealso", False),
        ]

def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)
        
    utils.format_text(USAGE, typ, __title__, 'hp-toolbox', __version__)
    sys.exit(0)        


class tbx_client(async.dispatcher):

    def __init__(self):
        async.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connect((prop.hpssd_host, prop.hpssd_port)) 
        except socket.error:
            log.error("Unable to connect to HPLIP I/O. Check and make sure HPLIP is running.")
            raise Error(ERROR_UNABLE_TO_CONTACT_SERVICE)
        
        self.in_buffer = ""
        self.out_buffer = ""
        self.fields = {}
        self.data = ''
        self.error_dialog = None
        self.toolbox_active = False
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

        self.in_buffer = self.recv(prop.max_message_len)
        log.debug(repr(self.in_buffer))

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
            log.debug("%s %s %s" % ("*"*20, msg_type, "*"*20))
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
            if toolbox is not None:
                toolbox.close()
            qApp.quit()

        return ''

    # EVENT
    def handle_eventgui(self):
        #global toolbox
        if toolbox is not None:
            try:
                job_id = self.fields['job-id']
                event_code = self.fields['event-code']
                event_type = self.fields['event-type']
                retry_timeout = self.fields['retry-timeout']
                lines = self.data.splitlines()
                error_string_short, error_string_long = lines[0], lines[1]
                device_uri = self.fields['device-uri']
    
                log.debug("Event: %d '%s'" % (event_code, event_type))
    
                toolbox.EventUI(event_code, event_type, error_string_short,
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
        out_buffer = buildMessage("RegisterGUIEvent", None, {'username': prop.username, 'type':'tbx'})
        self.send(out_buffer)

def toolboxCleanup():
    pass

def handleEXIT():
    if client is not None:
        try:
            client.close()
        except:
            pass
            
    if hpiod_sock is not None:
        hpiod_sock.close()

    try:
        app.quit()
    except:
        pass


prop.prog = sys.argv[0]

try:
    opts, args = getopt.getopt(sys.argv[1:], 'l:hg', 
        ['level=', 'help', 'help-rest', 'help-man'])

except getopt.GetoptError:
    usage()

if os.getenv("HPLIP_DEBUG"):
    log.set_level('debug')
    
    
for o, a in opts:
    if o in ('-l', '--logging'):
        log_level = a.lower().strip()
        if not log.set_level(log_level):
            usage()
            
    elif o == '-g':
        log.set_level('debug')

    elif o in ('-h', '--help'):
        usage()
        
    elif o == '--help-rest':
        usage('rest')
    
    elif o == '--help-man':
        usage('man')
        
        
utils.log_title(__title__, __version__)

# Security: Do *not* create files that other users can muck around with
os.umask (0077)

# PyQt
#if not utils.checkPyQtImport():
#    log.error("PyQt/Qt initialization error. Please check install of PyQt/Qt and try again.")
#    sys.exit(1)

##from qt import *
##
### UI Forms
##from ui.devmgr4 import devmgr4

try:
    client = tbx_client()
except Error:
    log.error("Unable to create client object.")
    sys.exit(1)
except socket.error:
    log.error("Unable to connect to HPLIP I/O (hpiod).")
    sys.exit(1)
    
log.debug("Connected to hpssd on %s:%d" % (prop.hpssd_host, prop.hpssd_port))

# create the main application object
app = QApplication(sys.argv)

hpiod_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    hpiod_sock.connect((prop.hpiod_host, prop.hpiod_port))
except socket.error:
    log.error("Unable to connect to HPLIP I/O (hpiod).")
    sys.exit(1)

log.debug("Connected to hpiod on %s:%d" % (prop.hpiod_host, prop.hpiod_port))

toolbox = devmgr4(hpiod_sock, client.socket, toolboxCleanup)
app.setMainWidget(toolbox)

toolbox.show()

atexit.register(handleEXIT)
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

handleEXIT()

sys.exit(0)

