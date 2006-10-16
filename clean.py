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


__version__ = '1.7'
__title__ = 'Printer Cartridge Cleaning Utility'
__doc__ = "Cartridge cleaning utility for HPLIP supported inkjet printers."

#Std Lib
import sys
import re
import getopt

# Local
from base.g import *
from base import device, utils, maint
from prnt import cups

USAGE = [(__doc__, "", "name", True),
         ("Usage: hp-clean [PRINTER|DEVICE-URI] [OPTIONS]", "", "summary", True),
         utils.USAGE_ARGS,
         utils.USAGE_DEVICE,
         utils.USAGE_PRINTER,
         utils.USAGE_SPACE,
         utils.USAGE_OPTIONS,
         ("Cleaning level:", "-v<level> or --level=<level>", "option", False),
         ("", "<level>: 1\*, 2, or 3 (\*default)", "option", False),
         utils.USAGE_BUS1, utils.USAGE_BUS2,
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
         utils.USAGE_HELP,
         utils.USAGE_EXAMPLES,
         ("""Clean CUPS printer named 'hp5550':""", """$ hp-clean -php5550""",  "example", False),
         ("""Clean printer with URI of 'hp:/usb/DESKJET_990C?serial=12345':""", """$ hp-clean -dhp:/usb/DESKJET_990C?serial=12345""", 'example', False),
         utils.USAGE_SPACE,
         utils.USAGE_NOTES,
         utils.USAGE_STD_NOTES1, utils.USAGE_STD_NOTES2, 
         utils.USAGE_SEEALSO,
         ("hp-align", "", "seealso", False),
         ("hp-colorcal", "", "seealso", False),
         ]
         
def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)
        
    utils.format_text(USAGE, typ, __title__, 'hp-clean', __version__)
    sys.exit(0)

log.set_module("hp-clean")

try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:d:hl:b:v:g',
                                ['printer=', 'device=', 'help', 'help-rest', 'help-man', 
                                 'logging=', 'bus=', 'level=', 'help-desc'])
except getopt.GetoptError:
    usage()

bus = device.DEFAULT_PROBE_BUS
log_level = logger.DEFAULT_LOG_LEVEL
printer_name = None
device_uri = None
level = 1

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

    elif o in ('-p', '--printer'):
        if a.startswith('*'):
            printer_name = cups.getDefault()
        else:
            printer_name = a

    elif o in ('-d', '--device'):
        device_uri = a

    elif o in ('-b', '--bus'):
        bus = a.lower().strip()

    elif o in ('-l', '--logging'):
        log_level = a.lower().strip()
        if not log.set_level(log_level):
            usage()
        
    elif o == '-g':
        log.set_level('debug')

    elif o in ('-v', '--level'):
        try:
            level = int(a)
        except ValueError:
            log.error("Invalid cleaning level, setting level to 1.")
            level = 1

            
if level < 1 or level > 3:
    log.error("Invalid cleaning level, setting level to 1.")
    level = 1

if not device.validateBusList(bus):
    usage()

if device_uri and printer_name:
    log.error("You may not specify both a printer (-p) and a device (-d).")
    usage()

utils.log_title(__title__, __version__)
    
if not device_uri and not printer_name:
    try:
        device_uri = device.getInteractiveDeviceURI(bus)
        if device_uri is None:
            sys.exit(0)
    except Error:
        log.error("Error occured during interactive mode. Exiting.")
        sys.exit(0)

try:
    d = device.Device(device_uri, printer_name)
except Error, e:
    log.error("Unable to open device: %s" % e.msg)
    sys.exit(0)

if d.device_uri is None and printer_name:
    log.error("Printer '%s' not found." % printer_name)
    sys.exit(0)

if d.device_uri is None and device_uri:
    log.error("Malformed/invalid device-uri: %s" % device_uri)
    sys.exit(0)


try:
    try:
        d.open()
    except Error:
        log.error("Unable to print to printer. Please check device and try again.")
        sys.exit(1)
    
    if d.isIdleAndNoError():
        clean_type = d.mq.get('clean-type', 0)
        log.info("Performing type %d, level %d cleaning..." % (clean_type, level))
        
        if clean_type in (CLEAN_TYPE_PCL,CLEAN_TYPE_PCL_WITH_PRINTOUT):
            if level == 3:
                maint.wipeAndSpitType1(d)
            elif level == 2:
                maint.primeType1(d)
            else:
                maint.cleanType1(d)
        
        elif clean_type == CLEAN_TYPE_LIDIL:
            if level == 3:
                maint.wipeAndSpitType2(d)
            elif level == 2:
                maint.primeType2(d)
            else:
                maint.cleanType2(d)
    
        else:
            log.error("Cleaning not needed or supported on this device.")
    
    else:
        log.error("Device is busy or in an error state. Please check device and try again.")
        sys.exit(1)
finally:
    d.close()
    
log.info("")
log.info("Done.")

