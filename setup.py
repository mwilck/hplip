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


__version__ = '3.1'
__title__ = 'Printer/Fax Setup Utility'
__doc__ = "Installs HPLIP printers and faxes in the CUPS spooler. Tries to automatically determine the correct PPD file to use. Allows the printing of a testpage. Performs basic fax parameter setup."

# Std Lib
import sys, getopt, time
import socket, os.path, re
import readline, gzip

# Local
from base.g import *
from base import device, utils, msg, service
from prnt import cups

#number_pat = re.compile(r""".*?(\d+)""", re.IGNORECASE)
nickname_pat = re.compile(r'''\*NickName:\s*\"(.*)"''', re.MULTILINE)

USAGE = [ (__doc__, "", "name", True),
          ("Usage: hp-setup [MODE] [OPTIONS] [SERIAL NO.|USB bus:device|IP|DEVNODE]", "", "summary", True),
          ("[MODE]", "", "header", False),
          ("Enter graphical UI mode:", "-u or --gui (Default)", "option", False),
          ("Run in interactive mode:", "-i or --interactive", "option", False),
          utils.USAGE_SPACE,
          utils.USAGE_OPTIONS,
          ("Automatic mode:", "-a or --auto (-i mode only)", "option", False),
          ("To specify the port on a multi-port JetDirect:", "-p<port> or --port=<port> (Valid values are 1\*, 2, and 3. \*default) (-i mode only)", "option", False),
          ("No testpage in automatic mode:", "-x (-i mode only)", "option", False),
          ("To specify a CUPS printer queue name:", "-n<printer> or --printer=<printer> (-i mode only)", "option", False),
          ("To specify a CUPS fax queue name:", "-f<fax> or --fax=<fax> (-i mode only)", "option", False),
          ("Type of queue(s) to install:", "-t<typelist> or --type=<typelist>. <typelist>: print*, fax\* (\*default) (-i mode only)", "option", False),
          ("Bus to probe (if device not specified):", "-b<bus> or --bus=<bus> (-i mode only)", "option", False),
          utils.USAGE_BUS2,
          utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
          utils.USAGE_HELP,
          ("[SERIAL NO.|USB ID|IP|DEVNODE] (-i mode only)", "", "heading", False),
          ("USB bus:device (usb only):", """"xxx:yyy" where 'xxx' is the USB bus and 'yyy' is the USB device. (Note: The ':' and all leading zeros must be present.)""", 'option', False),
          ("", "Use the 'lsusb' command to obtain this information.", "option", False),
          ("IPs (network only):", 'IPv4 address "a.b.c.d" or "hostname"', "option", False),
          ("DEVNODE (parallel only):", '"/dev/parportX", X=0,1,2,...', "option", False),
          ("SERIAL NO. (usb and parallel only):", '"serial no."', "option", True),
          utils.USAGE_EXAMPLES,
          ("One USB printer attached, automatic:", "$ hp-setup -a", "example", False),
          ("USB, IDs specified:", "$ hp-setup 001:002", "example", False),
          ("Network:", "$ hp-setup 66.35.250.209", "example", False),
          ("Network, Jetdirect port 2:", "$ hp-setup --port=2 66.35.250.209", "example", False),
          ("Parallel:", "$ hp-setup /dev/parport0", "example", False),
          ("USB or parallel, using serial number:", "$ hp-setup US12345678A", "example", False),
          ("USB, automatic:", "$ hp-setup --auto 001:002", "example", False),
          ("Parallel, automatic, no testpage:", "$ hp-setup -a -x /dev/parport0", "example", False),
          ("Parallel, choose device:", "$ hp-setup -b par", "example", False),
          ("Setup using GUI mode:", "$ hp-setup -u", "example", False),
          utils.USAGE_SPACE,
          utils.USAGE_NOTES,
          ("1. If no serial number, USB ID, IP, or device node is specified, the USB and parallel busses will be probed for devices.", "", 'note', False),
          ("2. Using 'lsusb' to obtain USB IDs: (example)", "", 'note', False),
          ("   $ lsusb", "", 'note', False),
          ("         Bus 003 Device 011: ID 03f0:c202 Hewlett-Packard", "", 'note', False),
          ("   $ hp-setup --auto 003:011", "", 'note', False),
          ("   (Note: You may have to run 'lsusb' from /sbin or another location. Use '$ locate lsusb' to determine this.)", "", 'note', True),
          ("3. None of the parameters -a, -p, -n, -f, -t, -b, or \[SERIAL NO.|USB ID|IP|DEVNODE\] are valid in GUI (-u) mode.", "", 'note', True),
          utils.USAGE_SPACE,
          utils.USAGE_SEEALSO,
          ("hp-makeuri", "", "seealso", False),
          ("hp-probe", "", "seealso", False),
        ]

def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)

    utils.format_text(USAGE, typ, __title__, 'hp-setup', __version__)
    sys.exit(0)


log.set_module('hp-setup')

try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:n:d:hl:b:t:f:axgui',
        ['printer=', 'fax=', 'device=', 'help', 'help-rest', 'help-man',
         'logging=', 'bus=', 'type=', 'auto', 'port=', 'gui', 'interactive',
         'help-desc'])
except getopt.GetoptError:
    usage()

printer_name = None
fax_name = None
device_uri = None
log_level = logger.DEFAULT_LOG_LEVEL
bus = device.DEFAULT_PROBE_BUS
setup_print = True
setup_fax = True
makeuri = None
bus = "par,usb"
auto = False
testpage_in_auto_mode = True
jd_port = 1
mode = GUI_MODE
mode_specified = False

if os.getenv("HPLIP_DEBUG"):
    log.set_level('debug')

for o, a in opts:
    if o in ('-h', '--help'):
        usage('text')

    elif o == '--help-rest':
        usage('rest')

    elif o == '--help-man':
        usage('man')

    elif o == '--help-desc':
        print __doc__,
        sys.exit(0)
    
    elif o == '-x':
        testpage_in_auto_mode = False

    elif o in ('-n', '--printer'):
        printer_name = a

    elif o in ('-f', '--fax'):
        fax_name = a

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

    elif o == '-g':
        log.set_level('debug')

    elif o in ('-t', '--type'):
        setup_fax, setup_print = False, False
        a = a.strip().lower()
        for aa in a.split(','):
            if aa.strip() not in ('print', 'fax'):
                usage()
            if aa.strip() == 'print':
                setup_print = True
            elif aa.strip() == 'fax':
                setup_fax = True

    elif o in ('-p', '--port'):
        try:
            jd_port = int(a)
        except ValueError:
            log.error("Invalid port number. Must be between 1 and 3 inclusive.")
            usage()

    elif o in ('-a', '--auto'):
        auto = True
        
    elif o in ('-u', '--gui'):
        if mode_specified:
            log.error("You may only specify a single mode as a parameter (-i or -u).")
            sys.exit(1)
        
        mode = GUI_MODE
        mode_specified = True
        
    elif o in ('-i', '--interactive'):
        if mode_specified:
            log.error("You may only specify a single mode as a parameter (-i or -u).")
            sys.exit(1)

        mode = INTERACTIVE_MODE
        mode_specified = True


utils.log_title(__title__, __version__)

print os.geteuid()

if mode == GUI_MODE:
    if not os.getenv('DISPLAY'):
        log.error("No display found. Reverting to interactive mode.")
        mode = INTERACTIVE_MODE
    
    elif not utils.checkPyQtImport():
        log.error("PyQt init failed. Reverting to interactive mode.")
        mode = INTERACTIVE_MODE


if mode == GUI_MODE:
    from qt import *
    from ui import setupform

    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))

    if not os.geteuid() == 0:
        log.error("You must be root to run this utility.")
    
        QMessageBox.critical(None, 
                             "HP Device Manager - Printer Setup Wizard",
                             "You must be root to run hp-setup.",
                              QMessageBox.Ok,
                              QMessageBox.NoButton,
                              QMessageBox.NoButton)
                              
        sys.exit(1)
        
    try:
        w = setupform.SetupForm()
    except Error:
        log.error("Unable to connect to HPLIP I/O. Please (re)start HPLIP and try again.")
        sys.exit(1)
        
    a.setMainWidget(w)
    w.show()

    a.exec_loop()
    
else: # INTERACTIVE_MODE
            
    if not os.geteuid() == 0:
        log.error("You must be root to run this utility.")
        sys.exit(1)
    
    hpiod_sock = None
    try:
        hpiod_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hpiod_sock.connect((prop.hpiod_host, prop.hpiod_port))
    except socket.error:
        log.error("Unable to connect to hpiod.")
        sys.exit(1)
    
    
    hpssd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        hpssd_sock.connect((prop.hpssd_host, prop.hpssd_port))
    except socket.error:
        print "Unable to connect to HPLIP I/O (hpssd)."
        sys.exit(1)
    
    # ******************************* MAKEURI
    
    if len(args):
        param = args[0]
        device_uri, sane_uri, fax_uri = device.makeuri(hpiod_sock, hpssd_sock, param, jd_port)
    
    # ******************************* DEVICE CHOOSER
    if not device_uri: 
        try:
            device_uri = device.getInteractiveDeviceURI(bus)
            if device_uri is None:
                sys.exit(1)
        except Error:
            log.error("Error occured during interactive mode. Exiting.")
            sys.exit(1)
    
    # ******************************* QUERY MODEL AND COLLECT PPDS
    
    log.info(utils.bold("\nSetting up device: %s\n" % device_uri))
    
    if not auto:
        log.info("(Note: Defaults for each question are maked with a '*'. Press <enter> to accept the default.)")
    
    log.info("")
    
    print_uri = device_uri.replace("hpfax:", "hp:")
    fax_uri = device_uri.replace("hp:", "hpfax:")
    
    back_end, is_hp, bus, model, \
        serial, dev_file, host, port = \
        device.parseDeviceURI(device_uri)
    
    log.debug("Model=%s" % model)
    
    mq, data, result_code = msg.xmitMessage(hpssd_sock, "QueryModel", payload=None,
                                            other_fields={"device-uri": device_uri},
                                            timeout=prop.read_timeout)
    
    
    if result_code == ERROR_UNSUPPORTED_MODEL or \
        mq.get('support-type', SUPPORT_TYPE_NONE) == SUPPORT_TYPE_NONE:
    
        log.error("Unsupported printer model.")
        sys.exit(1)
    
    if not mq.get('fax-type', 0) and setup_fax:
        log.warning("Cannot setup fax - device does not have fax feature.")
        setup_fax = False
    
    log.debug("Searching for PPDs in: %s" % sys_cfg.dirs.ppd)
    ppds = []
    
    for f in utils.walkFiles(sys_cfg.dirs.ppd, pattern="HP*ppd*;hp*ppd*", abs_paths=True):
        ppds.append(f)
    
    default_model = utils.xstrip(model.replace('series', '').replace('Series', ''), '_')
    stripped_model = default_model.lower().replace('hp-', '').replace('hp_', '')
    
    # ******************************* PRINT QUEUE SETUP
    
    if setup_print:
        installed_print_devices = device.getSupportedCUPSDevices(['hp'])  
        log.debug(installed_print_devices)
    
        if not auto and print_uri in installed_print_devices:
            log.warning("One or more print queues already exist for this device: %s." % ', '.join(installed_print_devices[print_uri]))
    
            while True:
                user_input = raw_input(utils.bold("\nWould you like to install another print queue for this device? (y=yes, n=no*, q=quit) ?" ))
                user_input = user_input.lower().strip()
    
                if not user_input:
                    user_input = 'n'
    
                setup_print = (user_input == 'y')
    
                if user_input in ('q', 'y', 'n'):
                    break
    
                log.error("Please enter 'y', 'n' or 'q'")
    
            if user_input == 'q':
                log.info("OK, done.")
                sys.exit(0)
    
    
    
    if setup_print:
        log.info(utils.bold("\nPRINT QUEUE SETUP"))
    
        if auto:
            printer_name = default_model
    
        printer_default_model = default_model
    
        # Check for duplicate names
        if device_uri in installed_print_devices and \
            printer_default_model in installed_print_devices[device_uri]:
                i = 2
                while True:
                    t = printer_default_model + "_%d" % i
                    if t not in installed_print_devices[device_uri]:
                        printer_default_model += "_%d" % i
                        break
                    i += 1
    
        if not auto:
            if printer_name is None:
                while True:
                    printer_name = raw_input(utils.bold("\nPlease enter a name for this print queue (m=use model name:'%s'*, q=quit) ?" % printer_default_model))
    
                    if printer_name.lower().strip() == 'q':
                        log.info("OK, done.")
                        sys.exit(0)
    
                    if not printer_name or printer_name.lower().strip() == 'm':
                        printer_name = printer_default_model
    
                    name_ok = True
    
                    if print_uri in installed_print_devices:
                        for d in installed_print_devices[print_uri]:
                            #print d, printer_name
                            if printer_name in d:
                                log.error("A print queue with that name already exists. Please enter a different name.")
                                name_ok = False
                                break
    
                    # TODO: Validate chars in name
    
                    if name_ok:
                        break
        else:
            printer_name = printer_default_model
    
        log.info("Using queue name: %s" % printer_name)
        
        default_model = utils.xstrip(model.replace('series', '').replace('Series', ''), '_')
        stripped_model = default_model.lower().replace('hp-', '').replace('hp_', '')
    
        mins = cups.getPPDFile(stripped_model, ppds)
        x = len(mins)
    
        enter_ppd = False
    
        if x == 0:
            enter_ppd = True
    
        elif x == 1:
            print_ppd = mins[0]
            log.info("\nFound a possible PPD file: %s" % print_ppd)
    
            if not auto:
                while True:
                    log.info("Note: The model number may vary slightly from the actual model number on the device.")
                    user_input = raw_input(utils.bold("\nDoes this PPD file appear to be the correct one (y=yes*, n=no, q=quit) ?"))
                    user_input = user_input.strip().lower()
    
                    if user_input == 'q':
                        log.info("OK, done.")
                        sys.exit(0)
    
                    if not user_input or user_input == 'y':
                        break
    
                    if user_input == 'n':
                        enter_ppd = True
                        break
    
                    log.error("Please enter 'y' or 'n'")
    
        else:
            log.info("")
            log.warn("Found multiple possible PPD files")
    
            max_ppd_filename_size = 0
            for p in mins:
                max_ppd_filename_size = max(len(p), max_ppd_filename_size)
    
            log.info(utils.bold("\nChoose a PPD file that most closely matches your device:"))
            log.info("(Note: The model number may vary slightly from the actual model number on the device.)\n")
    
            formatter = utils.TextFormatter(
                    (
                        {'width': 4},
                        {'width': max_ppd_filename_size, 'margin': 2},
                        {'width': 40, 'margin': 2},
                    )
                )
    
            log.info(formatter.compose(("Num.", "PPD Filename", "Description")))
            log.info(formatter.compose(('-'*4, '-'*(max_ppd_filename_size), '-'*40 )))
    
            for y in range(x):
                if mins[y].endswith('.gz'):
                    nickname = gzip.GzipFile(mins[y], 'r').read(4096)
                else:
                    nickname = file(mins[y], 'r').read(4096)
    
                try:
                    desc = nickname_pat.search(nickname).group(1)
                except AttributeError:
                    desc = ''
    
                log.info(formatter.compose((str(y), mins[y], desc)))
    
            x += 1
            none_of_the_above = y+1
            log.info(formatter.compose((str(none_of_the_above), "(None of the above match)", '')))
    
            while 1:
                user_input = raw_input(utils.bold("\nEnter number 0...%d for PPD file (q=quit) ?" % (x-1)))
                user_input = user_input.strip().lower()
    
                if user_input == '':
                    log.warn("Invalid input - enter a numeric value or 'q' to quit.")
                    continue
    
                if user_input == 'q':
                    log.info("OK, done.")
                    sys.exit(0)
    
                try:
                    i = int(user_input)
                except ValueError:
                    log.warn("Invalid input - enter a numeric value or 'q' to quit.")
                    continue
    
                if i == none_of_the_above:
                    enter_ppd = True
                    break
    
                if i < 0 or i > (x-1):
                    log.warn("Invalid input - enter a value between 0 and %d or 'q' to quit." % (x-1))
                    continue
    
                break
    
            if not enter_ppd:
                print_ppd = mins[i]
    
        if enter_ppd:
            log.error("Unable to find an appropriate PPD file.")
            enter_ppd = False
    
            while True:
                user_input = raw_input(utils.bold("\nWould you like to specify the path to the correct PPD file to use (y=yes, n=no*, q=quit) ?"))
                user_input = user_input.strip().lower()
    
                if not user_input or user_input in ('q', 'n'):
                    log.info("OK, done.")
                    sys.exit(0)
    
                if user_input == 'y':
                    enter_ppd = True
                    break
    
                log.error("Please enter 'y' or 'n'")
    
            if enter_ppd:
                ok = False
    
                while True:
                    user_input = raw_input(utils.bold("\nPlease enter the full filesystem path to the PPD file to use (q=quit) :"))
    
                    if user_input.lower().strip() == 'q':
                        log.info("OK, done.")
                        sys.exit(0)
    
                    file_path = user_input
    
                    if os.path.exists(file_path) and os.path.isfile(file_path):
    
                        if file_path.endswith('.gz'):
                            nickname = gzip.GzipFile(file_path, 'r').read(4096)
                        else:
                            nickname = file(file_path, 'r').read(4096)
    
                        try:
                            desc = nickname_pat.search(nickname).group(1)
                        except AttributeError:
                            desc = ''
    
                        if desc:
                            log.info("Description for the file: %s" % desc)
                        else:
                            log.error("No PPD 'NickName' found. This file may not be a valid PPD file.")
    
                        while True:
                            user_input = raw_input(utils.bold("\nUse this file (y=yes*, n=no, q=quit) ?"))
                            user_input = user_input.strip().lower()
    
                            if not user_input or user_input == 'y':
                                print_ppd = file_path
                                ok = True
                                break
    
                            elif user_input == 'q':
                                log.info("OK, done.")
                                sys.exit(0)
    
                            elif user_input == 'n':
                                break
    
                    else:
                        log.error("File not found or not an appropriate (PPD) file.")
    
    
                    if ok:
                        break
    
        if auto:
            location, info = '', 'Automatically setup by HPLIP'
        else:
            while True:
                location = raw_input(utils.bold("Enter a location description for this printer (q=quit) ?"))
    
                if location.strip().lower() == 'q':
                    log.info("OK, done.")
                    sys.exit(0)
    
                # TODO: Validate chars
    
                break
    
            while True:
                info = raw_input(utils.bold("Enter additonal information or notes for this printer (q=quit) ?"))
    
                if info.strip().lower() == 'q':
                    log.info("OK, done.")
                    sys.exit(0)
    
                # TODO: Validate chars
    
                break
    
        log.info(utils.bold("\nAdding print queue to CUPS:"))
        log.info("Device URI: %s" % print_uri)
        log.info("Queue name: %s" % printer_name)
        log.info("PPD file: %s" % print_ppd)
        log.info("Location: %s" % location)
        log.info("Information: %s" % info)
    
        cups.addPrinter(printer_name, print_uri, location, print_ppd, info)
    
        installed_print_devices = device.getSupportedCUPSDevices(['hp']) 
    
        log.debug(installed_print_devices)
    
        if print_uri not in installed_print_devices or \
            printer_name not in installed_print_devices[print_uri]:
    
            log.error("Printer queue setup failed. Please restart CUPS and try again.")
            sys.exit(1)
        else:
            service.sendEvent(hpssd_sock, EVENT_CUPS_QUEUES_CHANGED, device_uri=print_uri)
    
    
    
    # ******************************* FAX QUEUE SETUP
    
    if setup_fax:
        try:
            from fax import fax
        except ImportError:
            # This can fail on Python < 2.3 due to the datetime module
            setup_fax = False
            log.warning("Fax setup disabled - Python 2.3+ required.")
    
    log.info("")
    
    if setup_fax:
        log.info(utils.bold("\nFAX QUEUE SETUP"))
        installed_fax_devices = device.getSupportedCUPSDevices(['hpfax'])    
        log.debug(installed_fax_devices)
    
        if not auto and fax_uri in installed_fax_devices:
            log.warning("One or more fax queues already exist for this device: %s." % ', '.join(installed_fax_devices[fax_uri]))
            while True:
                user_input = raw_input(utils.bold("\nWould you like to install another fax queue for this device? (y=yes, n=no*, q=quit) ?"))
                user_input = user_input.lower().strip()
    
                if not user_input:
                    user_input = 'n'
    
                setup_fax = (user_input == 'y')                
    
                if user_input in ('q', 'y', 'n'):
                    break
    
                log.error("Please enter 'y', 'n' or 'q'")
    
            if user_input == 'q':
                log.info("OK, done.")
                sys.exit(0)
    
    
    if setup_fax:
        #log.info(utils.bold("\nSetting up fax queue..."))
    
        if auto: # or fax_name is None:
            fax_name = default_model + '_fax'
    
        fax_default_model = default_model + '_fax'
    
        # Check for duplicate names
        if fax_uri in installed_fax_devices and \
            fax_default_model in installed_fax_devices[fax_uri]:
                i = 2
                while True:
                    t = fax_default_model + "_%d" % i
                    if t not in installed_fax_devices[fax_uri]:
                        fax_default_model += "_%d" % i
                        break
                    i += 1
    
        if not auto:
            if fax_name is None:
                while True:
                    fax_name = raw_input(utils.bold("\nPlease enter a name for this fax queue (m=use model name:'%s'*, q=quit) ?" % fax_default_model))
    
                    if fax_name.lower().strip() == 'q':
                        log.info("OK, done.")
                        sys.exit(0)
    
                    if not fax_name or fax_name.lower().strip() == 'm':
                        fax_name = fax_default_model
    
                    name_ok = True
    
                    if fax_uri in installed_fax_devices:
                        for d in installed_fax_devices[fax_uri]:
                            if fax_name in d:
                                log.error("A fax queue with that name already exists. Please enter a different name.")
                                name_ok = False
                                break
    
                    # TODO: Validate chars in name
    
                    if name_ok:
                        break
    
        else:
            fax_name = fax_default_model
    
        log.info("Using queue name: %s" % fax_name)
    
        for f in ppds:
            if f.find('HP-Fax') >= 0:
                fax_ppd = f
                log.debug("Found PDD file: %s" % fax_ppd)
                break
        else:
            log.error("Unable to find HP fax PPD file! Please check you HPLIP installation and try again.")
            sys.exit(1)
    
    
        if auto:
            location, info = '', 'Automatically setup by HPLIP'
        else:
            while True:
                location = raw_input(utils.bold("Enter a location description for this printer (q=quit) ?"))
    
                if location.strip().lower() == 'q':
                    log.info("OK, done.")
                    sys.exit(0)
    
                # TODO: Validate chars
    
                break
    
            while True:
                info = raw_input(utils.bold("Enter additonal information or notes for this printer (q=quit) ?"))
    
                if info.strip().lower() == 'q':
                    log.info("OK, done.")
                    sys.exit(0)
    
                # TODO: Validate chars
    
                break
    
    
        log.info(utils.bold("\nAdding fax queue to CUPS:"))
        log.info("Device URI: %s" % fax_uri)
        log.info("Queue name: %s" % fax_name)
        log.info("PPD file: %s" % fax_ppd)
        log.info("Location: %s" % location)
        log.info("Information: %s" % info)
    
        cups.addPrinter(fax_name, fax_uri, location, fax_ppd, info)
    
        installed_fax_devices = device.getSupportedCUPSDevices(['hpfax']) 
    
        log.debug(installed_fax_devices) 
    
        if fax_uri not in installed_fax_devices or \
            fax_name not in installed_fax_devices[fax_uri]:
    
            log.error("Fax queue setup failed. Please restart CUPS and try again.")
            sys.exit(1)
        else:
            service.sendEvent(hpssd_sock, EVENT_CUPS_QUEUES_CHANGED, device_uri=fax_uri)
    
    
    # ******************************* FAX HEADER SETUP
    
        if auto:
            setup_fax = False
        else:
            while True:
                user_input = raw_input(utils.bold("\nWould you like to perform fax header setup (y=yes*, n=no, q=quit) ?"))
                user_input = user_input.strip().lower()
    
                if user_input == 'q':
                    log.info("OK, done.")
                    sys.exit(0)
    
                if not user_input:
                    user_input = 'y'
    
                setup_fax = (user_input == 'y')
    
                if user_input in ('y', 'n', 'q'):
                    break
    
                log.error("Please enter 'y' or 'n'")
    
        if setup_fax:
            d = fax.FaxDevice(fax_uri)
    
            try:
                d.open()
            except Error:
                log.error("Unable to communicate with the device. Please check the device and try again.")
            else:
                try:
                    tries = 0
                    ok = True
    
                    while True:
                        tries += 1
    
                        try:
                            current_phone_num = d.getPhoneNum()
                            current_station_name = d.getStationName()
                        except Error:
                            log.error("Could not communicate with device. Device may be busy. Please wait for retry...")
                            time.sleep(5)
                            ok = False
    
                            if tries > 12:
                                break
    
                        else:
                            ok = True
                            break
    
                    if ok:
                        while True:
                            if current_phone_num:
                                phone_num = raw_input(utils.bold("\nEnter the fax phone number for this device (c=use current:'%s'*, q=quit) ?" % current_phone_num))
                            else:
                                phone_num = raw_input(utils.bold("\nEnter the fax phone number for this device (q=quit) ?"))
    
                            if current_phone_num and (not phone_num or phone_num.strip().lower() == 'c'):
                                phone_num = current_phone_num
    
                            if phone_num.strip().lower() == 'q':
                                log.info("OK, done.")
                                sys.exit(0)
    
                            if len(phone_num) > 50:
                                log.error("Phone number length is too long (>50 characters). Please enter a shorter number.")
                                continue
    
                            ok = True
                            for x in phone_num:
                                if x not in '0123456789-(+) ':
                                    log.error("Invalid characters in phone number. Please only use 0-9, -, (, +, and )")
                                    ok = False
                                    break
    
                            if not ok:
                                continue
    
                            break
    
                        while True:
                            if current_station_name:
                                station_name = raw_input(utils.bold("\nEnter the name and/or company for this device (c=use current:'%s'*, q=quit) ?" % current_station_name))
                            else:
                                station_name = raw_input(utils.bold("\nEnter the name and/or company for this device (q=quit) ?"))
    
                            if current_station_name and (not station_name or station_name.strip().lower() == 'c'):
                                station_name = current_station_name
    
                            if station_name.strip().lower() == 'q':
                                log.info("OK, done.")
                                sys.exit(0)
    
                            if len(station_name) > 50:
                                log.error("Name/company length is too long (>50 characters). Please enter a shorter name/company.")
                                continue
    
                            break
    
    
                        try:
                            d.setStationName(station_name)
                            d.setPhoneNum(phone_num)
                        except Error:
                            log.error("Could not communicate with device. Device may be busy.")
                        else:
                            log.info("\nParameters sent to device.")
    
                finally:
                    d.close()
    
    
    # ******************************* TEST PAGE
    
    if setup_print:
        print_test_page = False
    
        if auto:
            if testpage_in_auto_mode:
                print_test_page = True
        else:
            while True:
                user_input = raw_input(utils.bold("\nWould you like to print a test page (y=yes*, n=no, q=quit) ?"))
                user_input = user_input.strip().lower()
    
                if not user_input:
                    user_input = 'y'
    
                if user_input == 'q':
                    log.info("OK, done.")
                    sys.exit(0)
    
                print_test_page = (user_input == 'y')
    
                if user_input in ('y', 'n', 'q'):
                    break
    
                log.error("Please enter 'y' or 'n'")
    
        if print_test_page:
            path = utils.which('hp-testpage')
    
            if len(path) > 0:
                cmd = 'hp-testpage -d%s' % print_uri
            else:
                cmd = 'python ./testpage.py -d%s' % print_uri
    
            os.system(cmd)
    
log.info("Done.")
sys.exit(0)
