#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) Copyright 2003-2007 Hewlett-Packard Development Company, L.P.
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

__version__ = '9.0'
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

log.set_module('hp-toolbox')

# UI Forms and PyQt
if not utils.checkPyQtImport():
    log.error("PyQt/Qt initialization error. Please check install of PyQt/Qt and try again.")
    sys.exit(1)

from qt import *
from ui.devmgr4 import DevMgr4


app = None
toolbox  = None

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

def toolboxCleanup():
    pass

def handleEXIT():
    if hpiod_sock is not None:
        hpiod_sock.close()

    if hpssd_sock is not None:
        hpssd_sock.close()

    try:
        app.quit()
    except:
        pass


prop.prog = sys.argv[0]

try:
    opts, args = getopt.getopt(sys.argv[1:], 'l:hg', 
        ['level=', 'help', 'help-rest', 'help-man', 'help-desc'])

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

    elif o == '--help-desc':
        print __doc__,
        sys.exit(0)



utils.log_title(__title__, __version__)

# Security: Do *not* create files that other users can muck around with
os.umask (0077)

# create the main application object
app = QApplication(sys.argv)

hpiod_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    hpiod_sock.connect((prop.hpiod_host, prop.hpiod_port))
except socket.error:
    log.error("Unable to connect to HPLIP I/O (hpiod).")
    sys.exit(1)

log.debug("Connected to hpiod on %s:%d" % (prop.hpiod_host, prop.hpiod_port))

hpssd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    hpssd_sock.connect((prop.hpssd_host, prop.hpssd_port))
except socket.error:
    log.error("Unable to connect to HPLIP I/O (hpssd).")
    sys.exit(1)

log.debug("Connected to hpssd on %s:%d" % (prop.hpssd_host, prop.hpssd_port))

toolbox = DevMgr4(hpiod_sock, hpssd_sock, toolboxCleanup, __version__)
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

