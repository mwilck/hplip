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

__version__ = '1.1'
__title__ = "Fax Address Book"
__doc__ = "A simple fax address book for HPLIP."

from base.g import *
from base import utils

import getopt

# PyQt
if not utils.checkPyQtImport():
    log.error("PyQt/Qt initialization error. Please check install of PyQt/Qt and try again.")
    sys.exit(1)

from qt import *

from ui.faxaddrbookform import FaxAddrBookForm

app = None
addrbook = None

def additional_copyright():
    log.info("Includes code from KirbyBase 1.8.1")
    log.info("Copyright (c) Jamey Cribbs (jcribbs@twmi.rr.com)")
    log.info("Licensed under the Python Software Foundation License.")
    log.info("")

USAGE = [(__doc__, "", "name", True),
         ("Usage: hp-fab [OPTIONS]", "", "summary", True),
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

    


def main(args):
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
    additional_copyright()
    
    log.set_module('fab')

    # Security: Do *not* create files that other users can muck around with
    os.umask (0077)

    # create the main application object
    global app
    app = QApplication(sys.argv)

    global addrbook
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

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
