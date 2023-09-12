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

__version__ = '2.5'
__title__ = 'CUPS Fax Backend (hpfax:)'
__doc__ = "CUPS backend for PC send fax. Generally this backend is run by CUPS, not directly by a user. To send a fax as a user, run hp-sendfax."

import sys
import getopt
import ConfigParser
import os.path, os
import socket
import syslog
import time
import re

pid = os.getpid()
config_file = '/etc/hp/hplip.conf'
home_dir = ''

if os.path.exists(config_file):
    config = ConfigParser.ConfigParser()
    config.read(config_file)

    try:
        home_dir = config.get('dirs', 'home')
    except:
        syslog.syslog(syslog.LOG_CRIT, "hpfax[%d]: error: Error setting home directory: home= under [dirs] not found." % pid)
        sys.exit(1)
else:
    syslog.syslog(syslog.LOG_CRIT, "hpfax[%d]: error: Error setting home directory: /etc/hp/hplip.conf not found." % pid)
    sys.exit(1)

if not home_dir or not os.path.exists(home_dir):
    syslog.syslog(syslog.LOG_CRIT, "hpfax[%d]: error: Error setting home directory: Home directory %s not found." % (pid, home_dir))
    sys.exit(1)

sys.path.insert( 0, home_dir )

try:
    from base.g import *
    from base.codes import *
    from base import device, utils, msg
    from base.service import sendEvent
    from prnt import cups
except ImportError:
    syslog.syslog(syslog.LOG_CRIT, "hpfax[%d]: error: Error importing HPLIP modules." % pid)
    sys.exit(1)

log.set_module("hpfax")

USAGE = [(__doc__, "", "para", True),
         ("Usage: hpfax [OPTIONS] [job_id] [username] [title] [copies] [options]", "", "summary", True),
         utils.USAGE_OPTIONS,
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
         utils.USAGE_HELP,
        ]

def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)
        
    utils.format_text(USAGE, typ, title=__title__, crumb='hpfax:')
    sys.exit(0)        





try:
    opts, args = getopt.getopt(sys.argv[1:], 'l:hg', ['level=', 'help', 'help-rest', 'help-man'])

except getopt.GetoptError:
    usage()

for o, a in opts:

    if o in ('-l', '--logging'):
        log_level = a.lower().strip()
        log.set_level(log_level)

    elif o == '-g':
        log.set_level('debug')
    
    elif o in ('-h', '--help'):
        usage()
        
    elif o == '--help-rest':
        usage('rest')
    
    elif o == '--help-man':
        usage('man')
        

if len( args ) == 0:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((prop.hpssd_host, prop.hpssd_port))
    except socket.error:
        log.stderr("hpfax[%d]: error: Unable to contact HPLIP I/O (hpssd)." % pid)
        sys.exit(1)

    fields, data, result_code = \
        msg.xmitMessage(sock,
                         "ProbeDevicesFiltered",
                         None,
                         {
                           'bus' : 'usb,par',
                           'timeout' : 5,
                           'ttl' : 4,
                           'filter' : 'fax',
                           'format' : 'cups',
                          }
                       )

    sock.close()

    if not fields.get('num-devices', 0) or result_code > ERROR_SUCCESS:
        cups_ver_major, cups_ver_minor, cups_ver_patch = cups.getVersionTuple()
        
        if cups_ver_major == 1 and cups_ver_minor < 2:
            print 'direct hpfax:/no_device_found "HP Fax" "no_device_found" ""' 
            
        sys.exit(0)

    direct_pat = re.compile(r'(.*?) "(.*?)" "(.*?)" "(.*?)"', re.IGNORECASE)
    
    good_devices = 0
    for d in data.splitlines():
        m = direct_pat.match(d)
        
        try:
            uri = m.group(1) or ''
            uri = uri.replace('hp:/', 'hpfax:/')
            mdl = m.group(2) or ''
            desc = m.group(3) or ''
            devid = m.group(4) or ''
        except AttributeError:
            continue
        
        try:
            back_end, is_hp, bus, model, serial, dev_file, host, port = \
                device.parseDeviceURI(uri)
        except Error:
            continue
        
        print 'direct %s "HP Fax" "%s HP Fax" "MFG:HP;MDL:Fax;DES:HP Fax;"' % (uri, desc)
        good_devices += 1
        
    if not good_devices:
        print 'direct hpfax:/no_device_found "HP Fax" "no_device_found" ""' 

    sys.exit(0)

else:
    # CUPS provided environment
    try:
        device_uri = os.environ['DEVICE_URI']
        printer_name = os.environ['PRINTER']
    except KeyError:
        log.stderr("hpfax[%d]: error: Improper environment: Must be run by CUPS." % pid)
        sys.exit(1)
        
    log.debug(args)
    
    try:
        job_id, username, title, copies, options = args[0:5]
    except IndexError:
        log.stderr("hpfax[%d]: error: Invalid command line: Invalid arguments." % pid)
        sys.exit(1)
        
    try:
        input_fd = file(args[5], 'r')
    except IndexError:
        input_fd = 0
        
    pdb = pwd.getpwnam(username)
    home_folder, uid, gid = pdb[5], pdb[2], pdb[3]
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((prop.hpssd_host, prop.hpssd_port))
    except socket.error:
        log.stderr("hpfax[%d]: error: Unable to contact HPLIP I/O (hpssd)." % pid)
        sys.exit(1)

    fax_data = os.read(input_fd, prop.max_message_len)

    if not len(fax_data):
        log.stderr("hpfax[%d]: error: No data!" % pid)
        
        sendEvent(sock, EVENT_ERROR_NO_DATA_AVAILABLE, 'error',
                  job_id, username, device_uri)
        
        sock.close()
        sys.exit(1)
        

    sendEvent(sock, EVENT_START_FAX_PRINT_JOB, 'event',
              job_id, username, device_uri)
    
    while True:
        try:
            fields, data, result_code = \
                msg.xmitMessage(sock, "HPFaxBegin", 
                                     None,
                                     {"username": username,
                                      "job-id": job_id,
                                      "device-uri": device_uri,
                                      "printer": printer_name,
                                      "title": title,
                                     })
                               
        except Error:
            log.stderr("hpfax[%d]: error: Unable to send event to HPLIP I/O (hpssd)." % pid)
            sys.exit(1) 
       
        if result_code == ERROR_GUI_NOT_AVAILABLE:
            # New behavior in 1.6.6a (10sec retry)
            log.stderr("hpfax[%d]: error: You must run hp-sendfax first. Run hp-sendfax now to continue. Fax will resume within 10 seconds." % pid)
            
            sendEvent(sock, EVENT_ERROR_FAX_MUST_RUN_SENDFAX_FIRST, 'event',
                      job_id, username, device_uri)
            
        else: # ERROR_SUCCESS
            break
        
        time.sleep(10)
    

    bytes_read = 0
    while True:
        if not len(fax_data):
            fields, data, result_code = \
                msg.xmitMessage(sock, "HPFaxEnd", 
                                     None,
                                     {"username": username,
                                      "job-id": job_id,
                                      "printer": printer_name,
                                      "title": title,
                                      "options": options,
                                      "device-uri": device_uri,
                                      "job-size": bytes_read,
                                     })
            
            break
                                   
            
        bytes_read += len(fax_data) 
        
        fields, data, result_code = \
            msg.xmitMessage(sock, "HPFaxData", 
                                 fax_data,
                                 {"username": username,
                                  "job-id": job_id,
                                 })

        fax_data = os.read(input_fd, prop.max_message_len)
    
    os.close(input_fd)
    
    #sendEvent(sock, EVENT_END_FAX_PRINT_JOB, 'event',
    #          job_id, username, device_uri)
    
    sock.close()
    sys.exit(0)
    
    
