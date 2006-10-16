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


__version__ = '2.2'
__title__ = 'Printer Discovery Utility'
__doc__ = "Discover USB, parallel, and network printers."


# Std Lib
import sys, getopt, re, socket

# Local
from base.g import *
from base import device, utils, slp, msg


USAGE = [(__doc__, "", "name", True),
         ("Usage: hp-probe [OPTIONS]", "", "summary", True),
         utils.USAGE_OPTIONS,
         ("Bus to probe:", "-b<bus> or --bus=<bus>", "option", False),
         ("", "<bus>: cups, usb\*, net, bt, fw, par (\*default) (Note: bt and fw not supported in this release.)", "option", False),
         ("Set Time to Live (TTL):", "-t<ttl> or --ttl=<ttl> (Default is 4).", "option", False),
         ("Set timeout:", "-o<timeout in secs.> or --timeout=<timeout is secs.>", "option", False),
         ("Filter by functionality:", "-e<filter list> or --filter=<filter list>", "option", False),
         ("", "<filter list>: comma separated list of one or more of: scan, pcard, fax, copy, or none\*. (\*none is the default)", "option", False),
         ("Search:", "-s<search re> or --search=<search re>", "option", False),
         ("", "<search re> must be a valid regular expression (not case sensitive)", "option", False),
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
         utils.USAGE_HELP,
         utils.USAGE_SPACE,
         utils.USAGE_EXAMPLES,
         ("Find all devices on the network:", "hp-probe -bnet", "example", False),
         ("Find all devices on USB that support scanning:", "hp-probe -busb -escan", "example", False),
         ("Find all networked devices that contain the name 'lnx' and that support photo cards or scanning:", "hp-probe -bnet -slnx -escan,pcard", "example", False),
         ("Find all devices that have queues installed in CUPS:", "hp-probe -bcups", "example", False),
         ("Find all devices on the USB bus:", "hp-probe", "example", False),
         ]
         
def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)
        
    utils.format_text(USAGE, typ, __title__, 'hp-probe', __version__)
    sys.exit(0)

         
log.set_module('hp-probe')



try:
    opts, args = getopt.getopt(sys.argv[1:],
                                'hl:b:t:o:e:s:g',
                                ['help', 'help-rest', 'help-man',
                                  'help-desc',
                                  'logging=',
                                  'bus=',
                                  'event=',
                                  'ttl=',
                                  'timeout=',
                                  'filter=',
                                  'search='
                                ]
                              )
except getopt.GetoptError:
    usage()

log_level = logger.DEFAULT_LOG_LEVEL
bus = "usb"
align_debug = False
format='cups'
timeout=5
ttl=4
filter = 'none'
search = ''

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
    
    elif o == '-g':
        log.set_level('debug')

    elif o in ('-b', '--bus'):
        try:
            bus = a.lower().strip().split(',')[0]
        except:
            bus = 'cups'
            
        if not device.validateBusList(bus):
            usage()

    elif o in ('-l', '--logging'):
        log_level = a.lower().strip()
        if not log.set_level(log_level):
            usage()

    elif o in ('-t', '--ttl'):
        try:
            ttl = int(a)
        except ValueError:
            ttl = 4
            log.note("TTL value error. TTL set to default of 4 hops.")

    elif o in ('-o', '--timeout'):
        try:
            timeout = int(a)
            if timeout > 45:
                log.note("Timeout > 45secs. Setting to 45secs.")
                timeout = 45
        except ValueError:
            timeout = 5
            log.note("Timeout value error. Timeout set to default of 5secs.")

        if timeout < 0:
            log.error("You must specify a positive timeout in seconds.")
            usage()

    elif o in ('-f', '--format'):
        format = a.lower().strip()

    elif o in ('-e', '--filter'):
        filter = a.lower().strip()
        if not device.validateFilterList(filter):
            usage()

    elif o in ('-s', '--search'):
        search = a.lower().strip()

utils.log_title(__title__, __version__)

if bus == 'net':
    log.info(utils.bold("Probing network for printers. Please wait, this will take approx. %d seconds...\n" % timeout))
        
hpssd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hpssd_sock.connect((prop.hpssd_host, prop.hpssd_port))

fields, data, result_code = \
    msg.xmitMessage(hpssd_sock,
                     "ProbeDevicesFiltered",
                      None,
                      {
                            'bus' : bus,
                            'timeout' : timeout,
                            'ttl' : ttl,
                            'format' : 'cups',
                            'filter' : filter,
                            'search': search,

                      }
                    )

hpssd_sock.close()

pat = re.compile(r'(.*?)\s"(.*?)"\s"(.*?)"\s"(.*?)"', re.IGNORECASE)

max_c1, max_c2, max_c3, max_c4 = 0, 0, 0, 0
dd = data.splitlines()

if dd:
    for d in dd:
        x = pat.search(d)
        
        c1 = x.group(1) # uri
        max_c1 = max(len(c1), max_c1)
        
        c2 = x.group(2) # model
        max_c2 = max(len(c2), max_c1)

        c3 = x.group(3) # ex. model
        max_c3 = max(len(c3), max_c3)
        
        c4 = x.group(4) # name
        max_c4 = max(len(c4), max_c4)
        


    if bus == 'net':
        formatter = utils.TextFormatter(
                    (
                        {'width': max_c1, 'margin' : 2},
                        {'width': max_c3, 'margin' : 2},
                        {'width': max_c4, 'margin' : 2},
                    )
                )
                
        log.info(formatter.compose(("Device URI", "Model", "Name")))
        log.info(formatter.compose(('-'*max_c1, '-'*max_c3, '-'*max_c4)))
        for d in dd:
            x = pat.search(d)
            uri = x.group(1)
            name = x.group(3)
            model = x.group(4)
            log.info(formatter.compose((uri, name, model)))
    else:
        formatter = utils.TextFormatter(
                    (
                        {'width': max_c1, 'margin' : 2},
                        {'width': max_c2, 'margin' : 2},
                        #{'width': max_c4, 'margin' : 2},
                    )
                )
                
        log.info(formatter.compose(("Device URI", "Model")))
        log.info(formatter.compose(('-'*max_c1, '-'*max_c2)))
        for d in dd:
            x = pat.search(d)
            uri = x.group(1)
            model = x.group(2)
            log.info(formatter.compose((uri, model)))

    log.info("\nFound %d printer(s) on the '%s' bus.\n" % (len(dd), bus))
            
else:
    log.warn("No devices found. If this isn't the result you are expecting,")

    if bus == 'net':
        log.warn("check your network connections and make sure your internet")
        log.warn("firewall software is disabled.")
    else:
        log.warn("check to make sure your devices are properly connected.")


