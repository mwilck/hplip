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


__version__ = '1.9'
__title__ = 'Photo Card Access Utility'
__doc__ = "Access inserted photo cards on supported HPLIP printers. This provides an alternative for older devices that do not support USB mass storage or for access to photo cards over a network. (GUI version)"

# Std Lib
import sys
import getopt

# Local
from base.g import *
from base import utils, device
from prnt import cups

use_qt_splashscreen = False


USAGE = [(__doc__, "", "name", True),
         ("Usage: hp-unload [PRINTER|DEVICE-URI] [OPTIONS]", "", "summary", True),
         utils.USAGE_ARGS,
         utils.USAGE_DEVICE,
         utils.USAGE_PRINTER,
         utils.USAGE_SPACE,
         utils.USAGE_OPTIONS,
         utils.USAGE_BUS1, utils.USAGE_BUS2,
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
         utils.USAGE_HELP,
         utils.USAGE_SPACE,
         utils.USAGE_NOTES,
         utils.USAGE_STD_NOTES1, utils.USAGE_STD_NOTES2, 
         utils.USAGE_SEEALSO,
         ("hp-photo", "", "seealso", False),
         ]
         
def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)
        
    utils.format_text(USAGE, typ, __title__, 'hp-unload', __version__)
    sys.exit(0)

def __tr(s,c = None):
    return qApp.translate("Unload",s,c)
    

# PyQt
if not utils.checkPyQtImport():
    log.error("PyQt/Qt initialization error. Please check install of PyQt/Qt and try again.")
    sys.exit(1)

from qt import *
from ui import unloadform

try:
    opts, args = getopt.getopt(sys.argv[1:],
                                'p:d:hl:b:g',
                                ['printer=',
                                  'device=',
                                  'help', 'help-rest', 'help-man',
                                  'logging=',
                                  'bus='
                                ]
                              )
except getopt.GetoptError:
    usage()

if os.getenv("HPLIP_DEBUG"):
    log.set_level('debug')

printer_name = None
device_uri = None
bus = device.DEFAULT_PROBE_BUS
log_level = logger.DEFAULT_LOG_LEVEL


for o, a in opts:

    if o in ('-h', '--help'):
        usage()
        
    elif o == '--help-rest':
        usage('rest')
    
    elif o == '--help-man':
        usage('man')

    elif o in ('-p', '--printer'):
        if a.startswith('*'):
            printer_name = cups.getDefault()
        else:
            printer_name = a

    elif o in ('-d', '--device'):
        device_uri = a

    elif o in ('-b', '--bus'):
        bus = a.lower().strip()
        if not device.validateBusList(bus):
            usage()

    elif o in ('-l', '--logging'):
        log_level = a.lower().strip()
        if not log.set_level(log_level):
            usage()
            
    elif o == '-g':
        log.set_level('debug')

    
utils.log_title(__title__, __version__)
            

#try:
if 1:
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))

    if use_qt_splashscreen:
        pixmap = QPixmap(os.path.join(prop.image_dir, "hp-tux-printer.png"))
        splash = QSplashScreen(pixmap)
        splash.message(__tr("Loading..."), Qt.AlignBottom)
        splash.show()

    try:
        w = unloadform.UnloadForm(bus, device_uri, printer_name)
    except Error:
        log.error("Unable to connect to HPLIP I/O. Please (re)start HPLIP and try again.")
        sys.exit(1)
        
    a.setMainWidget(w)
    w.show()

    if use_qt_splashscreen:
        splash.finish(w)

    a.exec_loop()
#except Exception, e:
    #log.exception()


