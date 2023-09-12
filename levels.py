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

__version__ = '1.0'
__title__ = 'Supply Levels Utility'
__doc__ = "Display bar graphs of current supply levels for supported HPLIP printers."

# Std Lib
import sys, getopt, time

# Local
from base.g import *
from base import device, status, utils
from prnt import cups

DEFAULT_BAR_GRAPH_SIZE = 100



USAGE = [(__doc__, "", "name", True),
         ("Usage: hp-levels [PRINTER|DEVICE-URI] [OPTIONS]", "", "summary", True),
         utils.USAGE_ARGS,
         utils.USAGE_DEVICE,
         utils.USAGE_PRINTER,
         utils.USAGE_SPACE,
         utils.USAGE_OPTIONS,
         utils.USAGE_BUS1, utils.USAGE_BUS2,
        ("Bar graph size:", "-s<size> or --size=<size> (default=%d)", "option", False),
        ("Use colored bar graphs:", "-c or --color (default is colorized)", "option", False),
        ("Bar graph character:", "-a<char> or --char=<char> (default is '/')", "option", False),
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
         utils.USAGE_HELP,
         utils.USAGE_SPACE,
         utils.USAGE_NOTES,
         utils.USAGE_STD_NOTES1, utils.USAGE_STD_NOTES2, 
         ]
         
def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)
        
    utils.format_text(USAGE, typ, __title__, 'hp-levels', __version__)
    sys.exit(0)


def logBarGraph(agent_level, agent_type, size=DEFAULT_BAR_GRAPH_SIZE, use_colors=True, bar_char='/'):
    if size == 0: size = 100
    adj = 100.0/size
    if adj==0.0: adj=100.0
    bar = int(agent_level/adj)
    if bar > (size-2): bar = size-2

    if use_colors:
        if agent_type in (AGENT_TYPE_CMY, AGENT_TYPE_KCM, AGENT_TYPE_CYAN, AGENT_TYPE_CYAN_LOW):
            log.info(utils.codes['teal'])
        elif agent_type in (AGENT_TYPE_MAGENTA, AGENT_TYPE_MAGENTA_LOW):
            log.info(utils.codes['fuscia'])
        elif agent_type in (AGENT_TYPE_YELLOW, AGENT_TYPE_YELLOW_LOW):
            log.info(utils.codes['yellow'])
        elif agent_type == AGENT_TYPE_BLUE:
            log.info(utils.codes['blue'])
        elif agent_type == AGENT_TYPE_BLACK:
            log.info(utils.codes['bold'])
        elif agent_type in (AGENT_TYPE_LG, AGENT_TYPE_G, AGENT_TYPE_PG):
            pass

    color = ''
    if use_colors:
        if agent_type in (AGENT_TYPE_CMY, AGENT_TYPE_KCM):
            color = utils.codes['fuscia']

    log.info(("-"*size)+color)

    color = ''
    if use_colors:
        if agent_type in (AGENT_TYPE_CMY, AGENT_TYPE_KCM):
            color = utils.codes['yellow']

    log.info("%s%s%s%s (approx. %d%%)%s" % ("|", bar_char*bar, 
             " "*(size-bar-2), "|", agent_level, color))

    color = ''
    if use_colors:
        color = utils.codes['reset']

    log.info(("-"*size)+color)


    
    
log.set_module('hp-levels')

    
try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:d:hl:b:s:ca:g',
        ['printer=', 'device=', 'help', 'help-rest', 'help-man', 
         'help-desc', 'logging=', 'size=', 'color', 'char='])
         
except getopt.GetoptError:
    usage()

printer_name = None
device_uri = None
log_level = logger.DEFAULT_LOG_LEVEL
bus = device.DEFAULT_PROBE_BUS
size = 100
color = True
bar_char = '/'

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
            log.info("Using CUPS default printer: %s" % printer_name)
            log.debug(printer_name)
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

    elif o in ('-s', '--size'):
        try:
            size = int(a.strip())
        except:
            size = DEFAULT_BAR_GRAPH_SIZE

        if size < 0 or size > 200:
            size = DEFAULT_BAR_GRAPH_SIZE

    elif o in ('-c', '--color'):
        color = True

    elif o in ('-a', '--char'):
        try:
            bar_char = a[0]
        except:
            bar_char = '/'

    elif o == '-g':
        log.set_level('debug')


if device_uri and printer_name:
    log.error("You may not specify both a printer (-p) and a device (-d).")
    usage()

utils.log_title(__title__, __version__)

if not device_uri and not printer_name:
    try:
        device_uri = device.getInteractiveDeviceURI(bus)
        if device_uri is None:
            sys.exit(1)
    except Error:
        log.error("Error occured during interactive mode. Exiting.")
        sys.exit(1)

try:
    d = device.Device(device_uri, printer_name)
except Error:
    log.error("Error opening device. Exiting.")
    sys.exit(1)

if d.device_uri is None and printer_name:
    log.error("Printer '%s' not found." % printer_name)
    sys.exit(1)

if d.device_uri is None and device_uri:
    log.error("Malformed/invalid device-uri: %s" % device_uri)
    sys.exit(1)


try:
    d.open()
    d.queryDevice()
except Error, e:
    log.error("Error opening device (%s). Exiting." % e.msg)
    sys.exit(1)

if d.mq['status-type'] != STATUS_TYPE_NONE:

    log.info("")

    sorted_supplies = []
    a = 1
    while True:
        try:
            agent_type = int(d.dq['agent%d-type' % a])
            agent_kind = int(d.dq['agent%d-kind' % a])
        except KeyError:
            break
        else:
            sorted_supplies.append((a, agent_kind, agent_type))
            
        a += 1
        
    sorted_supplies.sort(lambda x, y: cmp(x[2], y[2]) or cmp(x[1], y[1]))

    for x in sorted_supplies:
        a, agent_kind, agent_type = x
        agent_health = d.dq['agent%d-health' % a]
        agent_level = d.dq['agent%d-level' % a]
        agent_sku = str(d.dq['agent%d-sku' % a])
        agent_desc = d.dq['agent%d-desc' % a]
        agent_health_desc = d.dq['agent%d-health-desc' % a]

        if agent_health == AGENT_HEALTH_OK and \
            agent_kind in (AGENT_KIND_SUPPLY,
                            AGENT_KIND_HEAD_AND_SUPPLY,
                            AGENT_KIND_TONER_CARTRIDGE,
                            AGENT_KIND_MAINT_KIT,
                            AGENT_KIND_ADF_KIT,
                            AGENT_KIND_INT_BATTERY,
                            AGENT_KIND_DRUM_KIT,):

            log.info(utils.bold(agent_desc))
            log.info("Part No.: %s" % agent_sku)
            log.info("Health: %s" % agent_health_desc)
            logBarGraph(agent_level, agent_type, size, color, bar_char)
            log.info("")

        else:
            log.info(utils.bold(agent_desc))
            log.info("Part No.: %s" % agent_sku)
            log.info("Health: %s" % agent_health_desc)
            log.info("")


else:
    log.error("Status not supported for selected device.")
    sys.exit(1)

d.close()
sys.exit(0)

