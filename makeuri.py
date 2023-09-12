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
# Author: Don Welch, Smith Kennedy
#

__version__ = '4.1'
__title__ = 'Device URI Creation Utility'
__doc__ = "Creates device URIs for local and network connected printers for use with CUPS."

# Std Lib
import sys
import re
import getopt
import socket


# Local
from base.g import *
from base.codes import *
from base import device, utils


USAGE = [ (__doc__, "", "name", True),
          ("Usage: hp-makeuri [OPTIONS] [SERIAL NO.|USB ID|IP|DEVNODE]", "", "summary", True),
          ("[SERIAL NO.|USB ID|IP|DEVNODE]", "", "heading", False),
          ("USB IDs (usb only):", """"xxx:yyy" where xxx is the USB bus ID and yyy is the USB device ID. The ':' must be present.""", 'option', False),
          ("", """Use the 'lsusb' command to obtain this information.""", "option", False),
          ("IPs (network only):", 'IPv4 address "a.b.c.d" or "hostname"', "option", False),
          ("DEVNODE (parallel only):", '"/dev/parportX", X=0,1,2,...', "option", False),
          ("SERIAL NO. (usb and parallel only):", '"serial no."', "option", True),
          utils.USAGE_OPTIONS,
          ("To specify the port on a multi-port JetDirect:", "-p<port> or --port=<port> (Valid values are 1\*, 2, and 3. \*default)", "option", False),
          ("Show the CUPS URI only (quiet mode)(Note 1):", "-c or --cups", "option", False),
          ("Show the SANE URI only (quiet mode)(Note 1):", "-s or --sane", "option", False),
          ("Show the HP Fax URI only (quiet mode)(Note 1):", "-f or --fax", "option", False),
          utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
          utils.USAGE_HELP,
          utils.USAGE_EXAMPLES,
          ("USB:", "$ hp-makeuri 001:002", "example", False),
          ("Network:", "$ hp-makeuri 66.35.250.209", "example", False),
          ("Parallel:", "$ hp-makeuri /dev/parport0", "example", False),
          ("USB or parallel:", "$ hp-makeuri US12345678A", "example", False),
          ("USB, automatic:", "$ hp-makeuri --auto 001:002", "example", False),
          ("Parallel, automatic, no testpage:", "$ hp-makeuri /dev/parport0", "example", False),
          ("Parallel, choose device:", "$ hp-makeuri -b par", "example", False),
          utils.USAGE_SPACE,
          utils.USAGE_NOTES,
          ("1. If no serial number, USB ID, IP, or device node is specified, the USB and parallel busses will be probed for devices.", "", 'note', False),
          ("2. Using 'lsusb' to obtain USB IDs: (example)", "", 'note', False),
          ("   $ lsusb", "", 'note', False),
          ("   Bus 003 Device 011: ID 03f0:c202 Hewlett-Packard", "", 'note', False),
          ("   $ hp-makeuri 003:011", "", 'note', False),
          ("   (Note: You may have to run 'lsusb' from /sbin or another location. Use '$ locate lsusb' to determine this.)", "", 'note', False),
          utils.USAGE_SEEALSO,
          ("hp-setup", "", "seealso", False),
        ]

def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)
        
    utils.format_text(USAGE, typ, __title__, 'hp-makeuri', __version__)
    sys.exit(0)



try:
    opts, args = getopt.getopt(sys.argv[1:], 
                                'hl:csfp:g', 
                                ['help', 'help-rest', 'help-man',
                                  'logging=',
                                  'cups',
                                  'sane',
                                  'fax=',
                                  'port=',
                                ] 
                              ) 
except getopt.GetoptError:
    usage()
    sys.exit(1)

if os.getenv("HPLIP_DEBUG"):
    log.set_level('debug')

log_level = 'info'
cups_quiet_mode = False
sane_quiet_mode = False
fax_quiet_mode = False
bus = 'usb,par'
jd_port = 1

for o, a in opts:

    if o in ('-h', '--help'):
        usage()
        
    elif o == '--help-rest':
        usage('rest')
        
    elif o == '--help-man':
        usage('man')

    elif o in ('-l', '--logging'):
        log_level = a.lower().strip()
        if not log.set_level(log_level):
            usage()
        
    elif o in ('-c', '--cups'):
        cups_quiet_mode = True
        
    elif o in ('-s', '--sane'):
        sane_quiet_mode = True
        
    elif o in ('-f', '--fax'):
        fax_quiet_mode = True

    elif o in ('-p', '--port'):
        try:
            jd_port = int(a)
        except ValueError:
            log.error("Invalid port number. Must be between 1 and 3 inclusive.")
            usage()
            
    elif o == '-g':
        log.set_level('debug')
        

quiet_mode = cups_quiet_mode or sane_quiet_mode or fax_quiet_mode

if quiet_mode:
    log.set_level('warn')
    
utils.log_title(__title__, __version__)    

if len(args) != 1:
    log.error("You must specify one SERIAL NO., IP, USB ID or DEVNODE on the command line.")
    usage()
    
param = args[0]

if 'localhost' in param.lower():
    log.error("Invalid hostname")
    usage()

hpiod_sock = None
try:
    hpiod_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hpiod_sock.connect((prop.hpiod_host, prop.hpiod_port))
except socket.error:
    log.error("Unable to connect to hpiod.")
    sys.exit(1)

hpssd_sock = None
try:
    hpssd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hpssd_sock.connect((prop.hpssd_host, prop.hpssd_port))
except socket.error:
    log.error("Unable to connect to hpssd.")
    sys.exit(1)
    
cups_uri, sane_uri, fax_uri = device.makeuri(hpiod_sock, hpssd_sock, param, jd_port)

if not cups_uri:
    log.error("Device not found")
    sys.exit(1)

if cups_quiet_mode:
    print cups_uri
elif not quiet_mode:    
    print "CUPS URI:", cups_uri

if sane_uri:
    if sane_quiet_mode:
        print sane_uri
    elif not quiet_mode:
        print "SANE URI:", sane_uri
elif not sane_uri and sane_quiet_mode:
    log.error("Device does not support scan.")
    
if fax_uri:
    if fax_quiet_mode:
        print fax_uri
    elif not quiet_mode:
        print "HP Fax URI:", fax_uri
elif not fax_uri and fax_quiet_mode:
    log.error("Device does not support fax.")

hpiod_sock.close()
hpssd_sock.close()

sys.exit(0)
