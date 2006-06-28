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
__title__ = "Fax Address Book"
__doc__ = "A simple fax address book for HPLIP."

from base.g import *
from base import utils

import getopt

log.set_module("hp-fab")


def additional_copyright():
    log.info("Includes code from KirbyBase 1.8.1")
    log.info("Copyright (c) Jamey Cribbs (jcribbs@twmi.rr.com)")
    log.info("Licensed under the Python Software Foundation License.")
    log.info("")

USAGE = [(__doc__, "", "name", True),
         ("Usage: hp-fab [MODE] [OPTIONS]", "", "summary", True),
         ("[MODE]", "", "header", False),
         ("Enter interactive mode:", "-i or --interactive", "option", False),
         ("Enter graphical UI mode:", "-u or --gui (Default)", "option", False),
         #("Run in non-interactive mode (batch mode):", "-n or --non-interactive", "option", False),
         utils.USAGE_SPACE,
         utils.USAGE_OPTIONS,
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
         utils.USAGE_HELP,
         utils.USAGE_SEEALSO,
         ("hp-sendfax", "", "seealso", False),
         ]
         
def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)
        additional_copyright()
        
    utils.format_text(USAGE, typ, __title__, 'hp-fab', __version__)
    sys.exit(0)

    

mode = GUI_MODE

try:
    opts, args = getopt.getopt(sys.argv[1:], 'l:hgi', 
        ['level=', 'help', 'help-rest', 'help-man',
         'gui', 'interactive'])

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
        
    elif o in ('-i', '--interactive'):
        mode = INTERACTIVE_MODE
        
    elif o in ('-u', '--gui'):
        mode = GUI_MODE
        

utils.log_title(__title__, __version__)
additional_copyright()

# Security: Do *not* create files that other users can muck around with
os.umask (0077)

if mode == GUI_MODE:
    if not os.getenv('DISPLAY'):
        mode = NON_INTERACTIVE_MODE
    elif not utils.checkPyQtImport():
        mode = NON_INTERACTIVE_MODE

if mode == GUI_MODE:
    from qt import *
    from ui.faxaddrbookform import FaxAddrBookForm
    
    app = None
    addrbook = None
    
    # create the main application object
    app = QApplication(sys.argv)
    
    addrbook = FaxAddrBookForm()
    addrbook.show()
    app.setMainWidget(addrbook)
    
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

else: # INTERACTIVE_MODE
    log.error("Sorry, -i not implemented yet.")
