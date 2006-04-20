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
__title__ = 'Dependency/Version Check Utility'
__doc__ = "Check the existence and versions of HPLIP dependencies."

# Std Lib
import sys
import os
import getopt

# Local
from base.g import *
from base import utils
    

USAGE = [(__doc__, "", "name", True),
         ("Usage: hp-check [OPTIONS]", "", "summary", True),
         utils.USAGE_OPTIONS,
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
         utils.USAGE_HELP,
        ]

def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)
        
    utils.format_text(USAGE, typ, __title__, 'hp-check', __version__)
    sys.exit(0)        


try:
    opts, args = getopt.getopt(sys.argv[1:], 'hl:g', 
        ['help', 'help-rest', 'help-man', 'logging=']) 
        
except getopt.GetoptError:
    usage()
    sys.exit(1)
    
if os.getenv("HPLIP_DEBUG"):
    log.set_level('debug')

log_level = 'info'

for o, a in opts:
    if o in ('-h', '--help'):
        usage()
        
    elif o == '--help-rest':
        usage('rest')
    
    elif o == '--help-man':
        usage('man')
    
    elif o in ('-l', '--logging'):
        log_level = a.lower().strip()
        
    elif o == '-g':
        log.set_level('debug')
        
        
if not log.set_level(log_level):
    usage()
    
utils.log_title(__title__, __version__)    

log.info("Checking Python version...")
ver = sys.version_info
log.debug("sys.version_info = %s" % repr(ver))
ver_maj = ver[0]
ver_min = ver[1]
ver_pat = ver[2]

log.info("--> Version %d.%d.%d installed." % ver[:3])

if ver_maj == 2:
    if ver_min >= 1:
        log.info("--> OK")
    else:
        log.error("Please update to Python >= 2.1")

log.info("Checking for SIP...")
# SIP
try:
    import sip
except ImportError:
    log.error("SIP not installed.")
else:
    log.info("--> OK")

# PyQt
log.info("Checking for PyQt...")
try:
    from qt import *
except ImportError:
    log.error("PyQt not installed.")
else:
    log.info("--> OK")

# check version of Qt
log.info("Checking Qt version...")

qtMajor = int(qVersion().split('.')[0])
log.debug("qVersion() = %s" % qVersion())
log.info("--> Version %s installed." % qVersion())

if qtMajor < MINIMUM_QT_MAJOR_VER: 
    log.error("Incorrect version of Qt installed. Ver. 3.0 or greater required.")
else:
    log.info("--> OK")

log.info("Checking SIP version...")

try:
    import pyqtconfig
except ImportError:
    log.error("Unable to import pyqtconfig. PyQt may not be properly installed.")
else:
    c = pyqtconfig.Configuration()
    log.info("--> Version %s installed" % c.sip_version_str)
    log.info("--> OK")

log.info("Checking PyQt version...")

#check version of PyQt
try:
    pyqtVersion = PYQT_VERSION_STR
    log.debug("PYQT_VERSION_STR = %s" % pyqtVersion)
except:
    pyqtVersion = PYQT_VERSION
    log.debug("PYQT_VERSION = %s" % pyqtVersion)

while pyqtVersion.count('.') < 2:
    pyqtVersion += '.0'

(maj_ver, min_ver, pat_ver) = pyqtVersion.split('.')

if pyqtVersion.find('snapshot') >= 0:
    log.warning("A non-stable snapshot version of PyQt is installed.")
else:    
    try:
        maj_ver = int(maj_ver)
        min_ver = int(min_ver)
        pat_ver = int(pat_ver)
    except ValueError:
        maj_ver, min_ver, pat_ver = 0, 0, 0
    else:
        log.info("--> Version %d.%d.%d installed." % (maj_ver, min_ver, pat_ver))
        
    if maj_ver < MINIMUM_PYQT_MAJOR_VER or \
        (maj_ver == MINIMUM_PYQT_MAJOR_VER and min_ver < MINIMUM_PYQT_MINOR_VER):
        log.error("HPLIP may not function properly with the version of PyQt that is installed (%d.%d.%d)." % (maj_ver, min_ver, pat_ver))
        log.error("Incorrect version of PyQt installed. Ver. %d.%d or greater required." % (MINIMUM_PYQT_MAJOR_VER, MINIMUM_PYQT_MINOR_VER))
    else:
        log.info("--> OK")
    
log.info("")
log.info("If any errors or warnings were reported, please refer to the installation instructions for")
log.info("installing dependencies at: http://hpinkjet.sourceforge.net/install.php#setup_env")



