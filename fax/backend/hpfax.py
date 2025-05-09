#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) Copyright 2003-2015 HP Development Company, L.P.
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

__version__ = '4.1'
__title__ = 'CUPS Fax Backend (hpfax:)'
__doc__ = "CUPS backend for PC send fax. Generally this backend is run by CUPS, not directly by a user. To send a fax as a user, run hp-sendfax or print to the device's CUPS fax queue."

# StdLib
import sys
import getopt
import os.path, os
import syslog
import time
import operator
import tempfile

if sys.version_info[0] == 3:
    import configparser
else:
    import ConfigParser as configparser

CUPS_BACKEND_OK = 0 # Job completed successfully
CUPS_BACKEND_FAILED = 1 # Job failed, use error-policy
CUPS_BACKEND_AUTH_REQUIRED = 2 # Job failed, authentication required
CUPS_BACKEND_HOLD = 3 # Job failed, hold job
CUPS_BACKEND_STOP = 4 #  Job failed, stop queue
CUPS_BACKEND_CANCEL = 5 # Job failed, cancel job

PIPE_BUF = 4096

job_id = 0
pid = os.getpid()
config_file = '/etc/hp/hplip.conf'
home_dir = ''


def bug(msg):
    syslog.syslog("hpfax[%d]: error: %s\n" % (pid, msg))
    log.stderr("ERROR: %s\n" % msg)


if os.path.exists(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    try:
        home_dir = config.get('dirs', 'home')
    except:
        bug("Error setting home directory: home= under [dirs] not found.")
        sys.exit(1)
else:
    bug("Error setting home directory: /etc/hp/hplip.conf not found")
    sys.exit(1)

if not home_dir or not os.path.exists(home_dir):
    bug("Error setting home directory: Home directory %s not found." % home_dir)
    sys.exit(1)

sys.path.insert(0, home_dir)
os.chdir(home_dir)

# HPLIP
try:
    from base.g import *
    #from base.codes import *
    from base import device
    from base import utils
    #from prnt import cups
except ImportError as e:
    bug("Error importing HPLIP modules: %s\n" % (pid, e))
    sys.exit(1)

def handle_sigpipe():
    syslog.syslog("SIGPIPE!")


USAGE = [(__doc__, "", "para", True),
         ("Usage: hpfax [job_id] [username] [title] [copies] [options]", "", "summary", True),
         utils.USAGE_OPTIONS,
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
         utils.USAGE_HELP,
        ]

def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)

    utils.format_text(USAGE, typ, title=__title__, crumb='hpfax:')
    sys.exit(CUPS_BACKEND_OK)

# Send dbus event to hpssd on dbus system bus
def send_message(device_uri, printer_name, event_code, username, job_id, title, pipe_name=''):
    args = [device_uri, printer_name, event_code, username, job_id, title, pipe_name]
    msg = lowlevel.SignalMessage('/', 'com.hplip.StatusService', 'Event')
    msg.append(signature='ssisiss', *args)

    SystemBus().send_message(msg)


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
    cups11 = utils.to_bool(sys_conf.get('configure', 'cups11', '0'))

    try:
        probed_devices = device.probeDevices(['usb', 'par'], filter={'fax-type': (operator.gt, 0)})
    except Error:
        sys.exit(CUPS_BACKEND_FAILED)

    good_devices = 0
    for uri in probed_devices:
        try:
            back_end, is_hp, bus, model, serial, dev_file, host, zc, port = \
                device.parseDeviceURI(uri)
        except Error:
            continue

        mq = device.queryModelByModel(model)

        if mq.get('fax-type', FAX_TYPE_NONE) in (FAX_TYPE_MARVELL,):
            # HP Fax 3
            if bus == 'usb':
                print('direct %s "HP Fax 3" "%s USB %s HP Fax HPLIP" "MFG:HP;MDL:Fax 3;DES:HP Fax 3;"' % \
                    (uri.replace("hp:", "hpfax:"), model.replace('_', ' '), serial))

            else: # par
                print('direct %s "HP Fax 3" "%s LPT HP Fax HPLIP" "MFG:HP;MDL:Fax 3;DES:HP Fax 3;"' % \
                    (uri.replace("hp:", "hpfax:"), model.replace('_', ' ')))

        elif mq.get('fax-type', FAX_TYPE_NONE) in (FAX_TYPE_SOAP,) or mq.get('fax-type', FAX_TYPE_NONE) in (FAX_TYPE_LEDMSOAP,):
            # HP Fax 2
            if bus == 'usb':
                print('direct %s "HP Fax 2" "%s USB %s HP Fax HPLIP" "MFG:HP;MDL:Fax 2;DES:HP Fax 2;"' % \
                    (uri.replace("hp:", "hpfax:"), model.replace('_', ' '), serial))

            else: # par
                print('direct %s "HP Fax 2" "%s LPT HP Fax HPLIP" "MFG:HP;MDL:Fax 2;DES:HP Fax 2;"' % \
                    (uri.replace("hp:", "hpfax:"), model.replace('_', ' ')))
        elif mq.get('fax-type', FAX_TYPE_NONE) in (FAX_TYPE_LEDM,):
            # HP Fax 4
            if bus == 'usb':
                print('direct %s "HP Fax 4" "%s USB %s HP Fax HPLIP" "MFG:HP;MDL:Fax 4;DES:HP Fax 4;"' % \
                    (uri.replace("hp:", "hpfax:"), model.replace('_', ' '), serial))

            else: # par
                print('direct %s "HP Fax 4" "%s LPT HP Fax HPLIP" "MFG:HP;MDL:Fax 4;DES:HP Fax 4;"' % \
                    (uri.replace("hp:", "hpfax:"), model.replace('_', ' ')))

        else:
            # HP Fax
            if bus == 'usb':
                print('direct %s "HP Fax" "%s USB %s HP Fax HPLIP" "MFG:HP;MDL:Fax;DES:HP Fax;"' % \
                    (uri.replace("hp:", "hpfax:"),  model.replace('_', ' '), serial))

            else: # par
                print('direct %s "HP Fax" "%s LPT HP Fax HPLIP" "MFG:HP;MDL:Fax;DES:HP Fax;"' % \
                    (uri.replace("hp:", "hpfax:"),  model.replace('_', ' ')))

        good_devices += 1

    if good_devices == 0:
        if cups11:
            print('direct hpfax:/no_device_found "HP Fax" "no_device_found" ""')
        else:
            print('direct hpfax "Unknown" "HP Fax (HPLIP)" ""')

    sys.exit(CUPS_BACKEND_OK)

else:
    try:
        # dBus
        import dbus
        from dbus import SystemBus, lowlevel
    except ImportError:
        bug("HPLIP pc send fax requires dbus and python-dbus")
        sys.exit(CUPS_BACKEND_FAILED)

    import warnings
    # Ignore: .../dbus/connection.py:242: DeprecationWarning: object.__init__() takes no parameters
    # (occurring on Python 2.6/dBus 0.83/Ubuntu 9.04)
    warnings.simplefilter("ignore", DeprecationWarning)

    # CUPS provided environment
    try:
        device_uri = os.environ['DEVICE_URI']
        printer_name = os.environ['PRINTER']
    except KeyError:
        bug("Improper environment: Must be run by CUPS.")
        sys.exit(CUPS_BACKEND_FAILED)

    log.debug(args)

    try:
        job_id, username, title, copies, options = args[0:5]
        job_id = int(job_id)
    except IndexError:
        bug("Invalid command line: invalid arguments.")
        sys.exit(CUPS_BACKEND_FAILED)

    send_message(device_uri, printer_name, EVENT_START_FAX_PRINT_JOB, username, job_id, title)

    try:
        input_fd = open(utils.sanitize_filename(args[5]), 'r')
    except IndexError:
        input_fd = 0

    if os.path.exists("/home/%s/.hplip"%username):
        tmp_dir = "/home/%s/.hplip"%username
    else:
        tmp_dir = "/tmp"

    pipe_name = os.path.join(tmp_dir, "hp_fax-pipe-%d" % job_id)

    # Create the named pipe. Make sure it exists before sending
    # message to hppsd.
    os.umask(0o111)
    try:
        os.mkfifo(pipe_name)
    except OSError:
        os.unlink(pipe_name)
        os.mkfifo(pipe_name)

    # Send dbus event to hpssd
    send_message(device_uri, printer_name, EVENT_FAX_RENDER_COMPLETE, username, job_id, title, pipe_name)

    # REVISIT:
    pipe = os.open(pipe_name, os.O_WRONLY)

    bytes_read = 0
    while True:
        data = os.read(input_fd, PIPE_BUF)

        if not data:
            break

        os.write(pipe, data)
        #syslog.syslog("Writing %d to pipe..." % len(data))
        bytes_read += len(data)

    if not bytes_read:
        bug("No data on input file descriptor.")
        sys.exit(CUPS_BACKEND_FAILED)

    os.close(input_fd)
    os.close(pipe)
    os.unlink(pipe_name)

    send_message(device_uri, printer_name, EVENT_END_FAX_PRINT_JOB, username, job_id, title)

    sys.exit(CUPS_BACKEND_OK)
