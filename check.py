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

__version__ = '2.1'
__title__ = 'Dependency/Version Check Utility'
__doc__ = "Check the existence and versions of HPLIP dependencies."

# Std Lib
import sys
import os
import getopt
import commands
import re

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


    
def run(cmd):    
    log.debug(cmd)
    try:
        status, output = commands.getstatusoutput(cmd)
    except:
        log.error("Command not found.")
        return -1, ''
        
    log.debug(output)
    log.debug(status)
    return status, output
    
    
def checklib(output, lib):
    log.info("Checking for %s..." % lib)
    if output.find(lib) >= 0:
        log.info("--> OK")
        return True
    else:
        log.error("Not found.")
        return False

log.set_module("hp-check")

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
        log_level = 'debug'
        
        
if not log.set_level(log_level):
    usage()
    
utils.log_title(__title__, __version__)    

log.info(utils.bold("Basic system info..."))
status, output = run('uname -a')
log.info("--> %s" % output)

log.info(utils.bold("\nCurrently installed version..."))
v = sys_cfg.hplip.version
if v:
    log.info("--> %s" % v )
else:
    log.info("--> None found.")

log.info(utils.bold("\nChecking Python version..."))
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
        sys.exit(1)

log.info(utils.bold("\nChecking for user interface dependencies..."))
        
log.info("Checking for SIP...")
# SIP
try:
    import sip
except ImportError:
    log.error("SIP not installed.")
else:
    log.info("--> OK")

pyqt = False
# PyQt
log.info("Checking for PyQt...")
try:
    from qt import *
except ImportError:
    log.error("PyQt not installed.")
else:
    log.info("--> OK")
    pyqt = True

if pyqt:
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

log.info(utils.bold("\nChecking for library dependencies..."))
ldconfig = utils.which('ldconfig')
status, output = run('%s -p' % os.path.join(ldconfig, 'ldconfig'))

checklib(output, "libnetsnmp")
checklib(output, "libjpeg")
checklib(output, "libusb")
checklib(output, "libcrypto")
checklib(output, "libpthread")

log.info(utils.bold("\nChecking for application dependencies..."))

log.info("Checking ghostscript...")
status, output = run('gs --version')
if status != 0:
    log.error("Not found!")
else:
    log.info("--> Version %s" % output)
    if output.strip() < "7.05":
        log.error("Must be version 7.05 or later!")
        
log.info("Checking gcc...")
status, output = run('gcc --version')
if status != 0:
    log.error("Not found!")
else:
    log.info("--> %s" % output.splitlines()[0])
    log.info("--> OK")

##log.info("Checking automake...")
##status, output = run('automake --version')
##if status != 0:
##    log.error("Not found!")
##else:
##    log.info("--> %s" % output.splitlines()[0])
##    log.info("--> OK")
##    
##log.info("Checking autoconf...")
##status, output = run('autoconf --version')
##if status != 0:
##    log.error("Not found!")
##else:
##    log.info("--> %s" % output.splitlines()[0])
##    log.info("--> OK")

log.info("Checking make...")
status, output = run('make --version')
if status != 0:
    log.error("Not found!")
else:
    log.info("--> %s" % output.splitlines()[0])
    log.info("--> OK")
    
log.info("Checking ReportLab (optional)...")
try:
    import reportlab
except ImportError:
    log.warning("Not installed. Fax coverpage support will be disabled.")
else:
    log.info("--> Version %s" % reportlab.Version)
    log.info("--> OK")
    
log.info(utils.bold("\nChecking kernel module..."))
log.info("Checking for ppdev (optional)...")
lsmod = utils.which('lsmod')
status, output = run('%s | grep ppdev' % os.path.join(lsmod, 'lsmod'))
if output:
    log.info("--> OK")
else:
    log.warning("Not found. Parallel printers will not work properly with HPLIP.")
    

log.info(utils.bold("\nChecking for CUPS..."))
status, output = run('lpstat -r')

if status > 0:
    log.error("CUPS is not running. Please start CUPS and try again.")
    sys.exit(1)
else:
    log.info("--> %s" % output)
    log.info("--> OK")

from base import device
log.info(utils.bold("\nChecking existing CUPS queues..."))

lpstat_pat = re.compile(r"""^device for (.*): (.*)""", re.IGNORECASE)

status, output = run('lpstat -v')
cups_printers = []
for p in output.splitlines():
    try:
        match = lpstat_pat.search(p)
        printer_name = match.group(1)
        device_uri = match.group(2)
        cups_printers.append((printer_name, device_uri))
    except AttributeError:
        pass
    
if cups_printers:
    
    max_device_uri, max_printer_name = 0, 0
    for p in cups_printers:
        max_device_uri = max(max_device_uri, len(p[1]))
        max_printer_name = max(max_printer_name, len(p[0]))
        
    
    formatter = utils.TextFormatter(
        (
            {'width': max_printer_name, 'margin': 2},
            {'width': max_device_uri, 'margin': 2},
            {'width': 20, 'alignment': utils.TextFormatter.CENTER, 'margin': 2},
        )
    )
    log.info(formatter.compose(("Printer", "Device URI", "HPLIP Installed?")))
    log.info(formatter.compose(('-'*(max_printer_name), '-'*(max_device_uri), '-'*20)))
    
    non_hp = False
    for p in cups_printers:
        try:
            back_end, is_hp, bus, model, serial, dev_file, host, port = \
                device.parseDeviceURI(p[1])
                
        except Error:
            is_hp = False
            
        if is_hp:
            x = 'Yes'
        else:
            x = 'No'
            non_hp = True
            
        log.info(formatter.compose((p[0], p[1], x)))
        
    if non_hp:
        log.info("\nNote: Any CUPS queues that are not 'HPLIP Installed', must be installed")
        log.info("with the 'hp:' or 'hpfax:' backends to have them work in HPLIP. Refer")
        log.info("to the install instructions on http://hplip.sourceforge.net for more help.")

else:
    log.info("No queues found.")


log.info("\nIf any errors or warnings were reported, please refer to the installation instructions at:")
log.info("http://hplip.sourceforge.net/install/index.html\n")


