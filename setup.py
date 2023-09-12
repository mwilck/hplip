#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) Copyright 2003-2008 Hewlett-Packard Development Company, L.P.
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


__version__ = '7.2'
__title__ = 'Printer/Fax Setup Utility'
__doc__ = "Installs HPLIP printers and faxes in the CUPS spooler. Tries to automatically determine the correct PPD file to use. Allows the printing of a testpage. Performs basic fax parameter setup."

# Std Lib
import sys
import getopt
import time
import os.path
import re
import os
import gzip

try:
    import readline
except ImportError:
    pass

# Local
from base.g import *
from base import device, utils, tui, models
from prnt import cups

pm = None

def plugin_download_callback(c, s, t):
    pm.update(int(100*c*s/t), 
             utils.format_bytes(c*s))


nickname_pat = re.compile(r'''\*NickName:\s*\"(.*)"''', re.MULTILINE)

USAGE = [ (__doc__, "", "name", True),
          ("Usage: hp-setup [MODE] [OPTIONS] [SERIAL NO.|USB bus:device|IP|DEVNODE]", "", "summary", True),
          ("[MODE]", "", "header", False),
          ("Enter graphical UI mode:", "-u or --gui (Default)", "option", False),
          ("Run in interactive mode:", "-i or --interactive", "option", False),
          utils.USAGE_SPACE,
          utils.USAGE_OPTIONS,
          ("Automatic mode:", "-a or --auto (-i mode only)", "option", False),
          ("To specify the port on a multi-port JetDirect:", "-p<port> or --port=<port> (Valid values are 1\*, 2, and 3. \*default)", "option", False),
          ("No testpage in automatic mode:", "-x (-i mode only)", "option", False),
          ("To specify a CUPS printer queue name:", "-n<printer> or --printer=<printer> (-i mode only)", "option", False),
          ("To specify a CUPS fax queue name:", "-f<fax> or --fax=<fax> (-i mode only)", "option", False),
          ("Type of queue(s) to install:", "-t<typelist> or --type=<typelist>. <typelist>: print*, fax\* (\*default) (-i mode only)", "option", False),
          ("Bus to probe (if device not specified):", "-b<bus> or --bus=<bus>", "option", False),
          #utils.USAGE_BUS2,
          ("", "<bus>: usb\*, net, par (\*default)", 'option', False),
          utils.USAGE_LANGUAGE,
          utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
          utils.USAGE_HELP,
          ("[SERIAL NO.|USB ID|IP|DEVNODE]", "", "heading", False),
          ("USB bus:device (usb only):", """"xxx:yyy" where 'xxx' is the USB bus and 'yyy' is the USB device. (Note: The ':' and all leading zeros must be present.)""", 'option', False),
          ("", "Use the 'lsusb' command to obtain this information.", "option", False),
          ("IPs (network only):", 'IPv4 address "a.b.c.d" or "hostname"', "option", False),
          ("DEVNODE (parallel only):", '"/dev/parportX", X=0,1,2,...', "option", False),
          ("SERIAL NO. (usb and parallel only):", '"serial no."', "option", True),
          utils.USAGE_EXAMPLES,
          ("Setup using GUI mode:", "$ hp-setup", "example", False),
          ("Setup using GUI mode, specifying usb:", "$ hp-setup -b usb", "example", False),
          ("Setup using GUI mode, specifying an IP:", "$ hp-setup 192.168.0.101", "example", False),          
          ("One USB printer attached, automatic:", "$ hp-setup -i -a", "example", False),
          ("USB, IDs specified:", "$ hp-setup -i 001:002", "example", False),
          ("Network:", "$ hp-setup -i 66.35.250.209", "example", False),
          ("Network, Jetdirect port 2:", "$ hp-setup -i --port=2 66.35.250.209", "example", False),
          ("Parallel:", "$ hp-setup -i /dev/parport0", "example", False),
          ("USB or parallel, using serial number:", "$ hp-setup -i US12345678A", "example", False),
          ("USB, automatic:", "$ hp-setup -i --auto 001:002", "example", False),
          ("Parallel, automatic, no testpage:", "$ hp-setup -i -a -x /dev/parport0", "example", False),
          ("Parallel, choose device:", "$ hp-setup -i -b par", "example", False),
          utils.USAGE_SPACE,
          utils.USAGE_NOTES,
          ("1. If no serial number, USB ID, IP, or device node is specified, the USB and parallel busses will be probed for devices.", "", 'note', False),
          ("2. Using 'lsusb' to obtain USB IDs: (example)", "", 'note', False),
          ("   $ lsusb", "", 'note', False),
          ("         Bus 003 Device 011: ID 03f0:c202 Hewlett-Packard", "", 'note', False),
          ("   $ hp-setup --auto 003:011", "", 'note', False),
          ("   (Note: You may have to run 'lsusb' from /sbin or another location. Use '$ locate lsusb' to determine this.)", "", 'note', True),
          ("3. Parameters -a, -n, -f, or -t are not valid in GUI (-u) mode.", "", 'note', True),
          utils.USAGE_SPACE,
          utils.USAGE_SEEALSO,
          ("hp-makeuri", "", "seealso", False),
          ("hp-probe", "", "seealso", False),
        ]


##plugin_eula = """LICENSE TERMS FOR HP Linux Imaging and Printing (HPLIP) Driver Plug-in
##
##These License Terms govern your Use of the HPLIP Driver Plug-in Software (the "Software"). USE OF THE SOFTWARE INCLUDING, WITHOUT LIMITATION, ANY DOCUMENTATION, IS SUBJECT TO THESE LICENSE TERMS AND THE APPLICABLE AS-IS WARRANTY STATEMENT.  BY DOWNLOADING AND INSTALLING THE SOFTWARE, YOU ARE AGREEING TO BE BOUND BY THESE TERMS. IF YOU DO NOT AGREE TO ALL OF THESE TERMS, DO NOT DOWNLOAD AND INSTALL THE SOFTWARE ON YOUR SYSTEM.
##
##1. License Grant.    HP grants you a license to Use one copy of the Software with HP printing products only.  "Use" includes using, storing, loading, installing, executing, and displaying the Software.  You may not modify the Software or disable any licensing or control features of the Software.
##
##2. Ownership.   The Software is owned and copyrighted by HP or its third party suppliers.  Your license confers no title to, or ownership in, the Software and is not a sale of any rights in the Software.  HP's third party suppliers may protect their rights in the Software in the event of any violation of these license terms.
##
##3. Copies and Adaptations.   You may only make copies or adaptations of the Software for archival purposes or when copying or adaptation is an essential step in the authorized Use of the Software. You must reproduce all copyright notices in the original Software on all copies or adaptations.  You may not copy the Software onto any public network.
##
##4. No Disassembly.   You may not Disassemble the Software unless HP's prior written consent is obtained.  "Disassemble" includes disassembling, decompiling, decrypting, and reverse engineering.   In some jurisdictions, HP's consent may not be required for limited Disassembly.  Upon request, you will provide HP with reasonably detailed information regarding any Disassembly.
##
##5. No Transfer.   You may not assign, sublicense or otherwise transfer all or any part of these License Terms or the Software.
##
##6. Termination.   HP may terminate your license, upon notice, for failure to comply with any of these License Terms.  Upon termination, you must immediately destroy the Software, together with all copies, adaptations and merged portions in any form.
##
##7. Export Requirements.   You may not export or re-export the Software or any copy or adaptation in violation of any applicable laws or regulations.
##
##8. U.S. Government Restricted Rights.   The Software has been developed entirely at private expense.  It is delivered and licensed, as defined in any applicable DFARS, FARS, or other equivalent federal agency regulation or contract clause, as either "commercial computer software" or "restricted computer software", whichever is applicable.  You have only those rights provided for such Software by the applicable clause or regulation or by these License Terms.
##
##9. DISCLAIMER OF WARRANTIES.   TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, HP AND ITS SUPPLIERS PROVIDE THE SOFTWARE "AS IS" AND WITH ALL FAULTS, AND HEREBY DISCLAIM ALL OTHER WARRANTIES AND CONDITIONS, EITHER EXPRESS, IMPLIED, OR STATUTORY, INCLUDING, BUT NOT LIMITED TO, WARRANTIES OF TITLE AND NON-INFRINGEMENT, ANY IMPLIED WARRANTIES, DUTIES OR CONDITIONS OF MERCHANTABILITY, OF FITNESS FOR A PARTICULAR PURPOSE, AND OF LACK OF VIRUSES ALL WITH REGARD TO THE SOFTWARE.  Some states/jurisdictions do not allow exclusion of implied warranties or limitations on the duration of implied warranties, so the above disclaimer may not apply to you in its entirety.
##
##10. LIMITATION OF LIABILITY.  Notwithstanding any damages that you might incur, the entire liability of HP and any of its suppliers under any provision of this agreement and your exclusive remedy for all of the foregoing shall be limited to the greater of the amount actually paid by you separately for the Software or U.S. $5.00.  TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL HP OR ITS SUPPLIERS BE LIABLE FOR ANY SPECIAL, INCIDENTAL, INDIRECT, OR CONSEQUENTIAL DAMAGES WHATSOEVER (INCLUDING, BUT NOT LIMITED TO, DAMAGES FOR LOSS OF PROFITS OR CONFIDENTIAL OR OTHER INFORMATION, FOR BUSINESS INTERRUPTION, FOR PERSONAL INJURY, FOR LOSS OF PRIVACY ARISING OUT OF OR IN ANY WAY RELATED TO THE USE OF OR INABILITY TO USE THE SOFTWARE, OR OTHERWISE IN CONNECTION WITH ANY PROVISION OF THIS AGREEMENT, EVEN IF HP OR ANY SUPPLIER HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES AND EVEN IF THE REMEDY FAILS OF ITS ESSENTIAL PURPOSE.  Some states/jurisdictions do not allow the exclusion or limitation of incidental or consequential damages, so the above limitation or exclusion may not apply to you."""

def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)

    utils.format_text(USAGE, typ, __title__, 'hp-setup', __version__)
    sys.exit(0)


def restart_cups():
    if os.path.exists('/etc/init.d/cups'):
        return '/etc/init.d/cups restart'

    elif os.path.exists('/etc/init.d/cupsys'):
        return '/etc/init.d/cupsys restart'

    else:
        return 'killall -HUP cupsd'


log.set_module('hp-setup')

try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:n:d:hl:b:t:f:axguiq:',
        ['printer=', 'fax=', 'device=', 'help', 'help-rest', 'help-man',
         'logging=', 'bus=', 'type=', 'auto', 'port=', 'gui', 'interactive',
         'help-desc', 'username=', 'lang='])
except getopt.GetoptError, e:
    log.error(e.msg)
    usage()

printer_name = None
fax_name = None
device_uri = None
log_level = logger.DEFAULT_LOG_LEVEL
bus = None
setup_print = True
setup_fax = True
makeuri = None
auto = False
testpage_in_auto_mode = True
jd_port = 1
mode = GUI_MODE
mode_specified = False
username = ''
loc = None

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
        bus = [x.lower().strip() for x in a.split(',')]
        if not device.validateBusList(bus, False):
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
                if not prop.fax_build:
                    log.error("Cannot enable fax setup - HPLIP not built with fax enabled.")
                else:
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

    elif o == '--username':
        username = a

    elif o in ('-q', '--lang'):
        if a.strip() == '?':
            tui.show_languages()
            sys.exit(0)

        loc = utils.validate_language(a.lower())

try:
    param = args[0]
except IndexError:
    param = ''

log.debug("param=%s" % param)

utils.log_title(__title__, __version__)

if mode == GUI_MODE:
    if not prop.gui_build:
        log.warn("GUI mode disabled in build. Reverting to interactive mode.")
        mode = INTERACTIVE_MODE

    elif not os.getenv('DISPLAY'):
        log.warn("No display found. Reverting to interactive mode.")
        mode = INTERACTIVE_MODE

    elif not utils.checkPyQtImport():
        log.warn("PyQt init failed. Reverting to interactive mode.")
        mode = INTERACTIVE_MODE

        
if mode == GUI_MODE:
    from qt import *
    from ui import setupform

    app = QApplication(sys.argv)
    QObject.connect(app, SIGNAL("lastWindowClosed()"), app, SLOT("quit()"))

    if loc is None:
        loc = user_cfg.ui.get("loc", "system")
        if loc.lower() == 'system':
            loc = str(QTextCodec.locale())
            log.debug("Using system locale: %s" % loc)

    if loc.lower() != 'c':
        e = 'utf8'
        try:
            l, x = loc.split('.')
            loc = '.'.join([l, e])
        except ValueError:
            l = loc
            loc = '.'.join([loc, e])

        log.debug("Trying to load .qm file for %s locale." % loc)
        trans = QTranslator(None)

        qm_file = 'hplip_%s.qm' % l
        log.debug("Name of .qm file: %s" % qm_file)
        loaded = trans.load(qm_file, prop.localization_dir)

        if loaded:
            app.installTranslator(trans)
        else:
            loc = 'c'

    if loc == 'c':
        log.debug("Using default 'C' locale")
    else:
        log.debug("Using locale: %s" % loc)
        QLocale.setDefault(QLocale(loc))
        prop.locale = loc
        try:
            locale.setlocale(locale.LC_ALL, locale.normalize(loc))
        except locale.Error:
            pass

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
        w = setupform.SetupForm(bus, param, jd_port, username)
    except Error:
        log.error("Unable to connect to HPLIP I/O. Please (re)start HPLIP and try again.")
        sys.exit(1)

    app.setMainWidget(w)
    w.show()

    app.exec_loop()

    
    
else: # INTERACTIVE_MODE
    try:
        if not os.geteuid() == 0:
            log.error("You must be root to run this utility.")
            sys.exit(1)

        if not auto:
            log.info("(Note: Defaults for each question are maked with a '*'. Press <enter> to accept the default.)")
            log.info("")

        # ******************************* MAKEURI
        if param:
            device_uri, sane_uri, fax_uri = device.makeURI(param, jd_port)

        # ******************************* CONNECTION TYPE CHOOSER
        if not device_uri and bus is None:
            x = 1
            ios = {0: ('usb', "Universal Serial Bus (USB)") }
            if prop.net_build: 
                ios[x] = ('net', "Network/Ethernet/Wireless (direct connection or JetDirect)")
                x += 1
            if prop.par_build: 
                ios[x] = ('par', "Parallel Port (LPT:)")
                x += 1

            if len(ios) > 1:
                tui.header("CHOOSE CONNECTION TYPE")
                f = tui.Formatter()
                f.max_widths = (10, 10, 40)
                f.header = ("Num.", "Connection Type", "Connection Type Description")

                for x, data in ios.items():
                    if not x:
                        f.add((str(x) + "*", data[0], data[1]))
                    else:
                        f.add((str(x), data[0], data[1]))

                f.output()

                ok, val = tui.enter_range("\nEnter number 0...%d for connection type (q=quit, enter=usb*) ? " % x, 
                    0, x, 0)

                if not ok: sys.exit(0)

                bus = [ios[val][0]]
            else:
                bus = [ios[0][0]]

            log.info("\nUsing connection type: %s" % bus[0])

        # ******************************* DEVICE CHOOSER

        if not device_uri: 
            tui.header("DEVICE DISCOVERY")
            try:
                device_uri = device.getInteractiveDeviceURI(bus)
                if device_uri is None:
                    sys.exit(1)

            except Error:
                log.error("Error occured during interactive mode. Exiting.")
                sys.exit(1)

        # ******************************* QUERY MODEL AND COLLECT PPDS
        log.info(log.bold("\nSetting up device: %s\n" % device_uri))


        log.info("")
        print_uri = device_uri.replace("hpfax:", "hp:")
        fax_uri = device_uri.replace("hp:", "hpfax:")

        back_end, is_hp, bus, model, \
            serial, dev_file, host, port = \
            device.parseDeviceURI(device_uri)

        log.debug("Model=%s" % model)
        mq = device.queryModelByURI(device_uri)

        if not mq or mq.get('support-type', SUPPORT_TYPE_NONE) == SUPPORT_TYPE_NONE:
            log.error("Unsupported printer model.")
            sys.exit(1)

        if not mq.get('fax-type', FAX_TYPE_NONE) and setup_fax:
            #log.warning("Cannot setup fax - device does not have fax feature.")
            setup_fax = False

        # ******************************* PLUGIN

##        from installer import core_install
##        core = core_install.CoreInstall()
        norm_model = models.normalizeModelName(model).lower()
##
        plugin = mq.get('plugin', PLUGIN_NONE)
        #skip = False

        plugin_installed = utils.to_bool(sys_cfg.hplip.plugin)
        if plugin > PLUGIN_NONE and not plugin_installed: 
            tui.header("PLUG-IN INSTALLATION")
            
            hp_plugin = utils.which('hp-plugin')
            
            if hp_plugin:
                os.system("hp_plugin -i")
                
##
##
####            #plugin_lib = mq.get("plugin-library")
##            fw_download = mq.get("fw-download")
####
####            #log.debug("Plug-in library=%s" % plugin_lib)
####            log.debug("FW download=%s" % fw_download)
####
##            if plugin == PLUGIN_REQUIRED:
##                log.debug("Plug-in required and not installed for model %s" % norm_model)
##                log.info(log.bold("A plug-in is required for this printer."))
##                for line in tui.format_paragraph("""An additional software plug-in is required to operate this printer. You may download the plug-in directly from HP, or, if you already have a copy, you can specify a path to the file."""):
##                    log.info(line)
##
##                ok, ans = tui.enter_choice("\nDownload plug-in from HP (recomended) or specify a path to the plug-in (d=download*, p=specify path, q=quit) ? ", ['d', 'p'], 'd')
##
##                if not ok:
##                    sys.exit(0)
##
##            else:
##                log.debug("Plug-in optional and not installed for model %s" % norm_model)
##                log.info(log.bold("A plug-in is optional for this printer."))
##                for line in tui.format_paragraph("""An optional driver plug-in is available to enhance the operation of this printer. You may skip this installation, download the plug-in directly from an HP authorized server, or, if you already have a copy of the file, you can specify a path to the file."""):
##                    log.info(line)            
##
##                ok, ans = tui.enter_choice("\nDownload plug-in from HP (recomended), specify a path to the plug-in, or skip installation (d=download*, p=specify path, s=skip, q=quit) ? ", ['d', 'p', 's'], 'd')
##
##                if not ok:
##                    sys.exit(0)
##
##                if ans == 's':
##                    skip = True
##
##
##            if not skip:
##
##                from installer import core_install
##                core = core_install.CoreInstall()
##                core.set_plugin_version(sys_cfg.hplip.version)
##
##                if ans == 'd':
##                    plugin_conf_url = core.get_plugin_conf_url(version)
##                    
##                    ok = True
##                    if plugin_conf_url.startswith('http'):    
##                        log.info("\nChecking for network connection...")
##                    
##                        ok = core.check_network_connection()
##                        
##                    if ok:
##                            #def get_plugin_info(self, version, url, local_conf, callback):
####
##                        log.info("Downloading configuration...")
##                        pm = tui.ProgressMeter("Downloading configuration:")
##                        
##                        url, size, checksum, timestamp, ok = core.get_plugin_info(version,
##                            plugin_conf_url, plugin_download_callback)
##                        
##                        log.info("")
##
##                        log.debug("url= %s" % url)
##                        log.debug("size=%d" % size)
##                        log.debug("checksum=%s" % checksum)
##                        log.debug("timestamp=%f" % timestamp)
##
##                        if url and size and checksum and timestamp and ok:
##                            log.info("Downloading plug-in...")
##
##                            pm = tui.ProgressMeter("Downloading plugin:")
##                            ok, plugin_file = core.download_plugin(norm_model, url, size, 
##                                checksum, timestamp, plugin_download_callback)
##
##                            log.info("")
##
##                            if not ok:
##                                log.error("Plugin download failed.")
##                                sys.exit(1)
##
##                    else:
##                        log.error("Network connection not found.")
##                        sys.exit(1)
##
##
##                else: # "p": path
##                    while True:
##                        user_input = raw_input(log.bold("Enter the path to the %s.plugin file (q=quit) : " % norm_model)).strip()
##                        if user_input.strip().lower() == 'q':
##                            sys.exit(1)
##
##                        if not user_input.endswith('.plugin'):
##                            log.error("Plug-in filename must end with '.plugin' extension.")
##                            continue
##
##                        if os.path.exists(user_input):
##                            ok = core.copy_plugin(norm_model, user_input)
##
##                            if not ok:
##                                log.error("File copy failed.")
##
##                            else:
##                                break
##                        else:
##                            log.error("File not found.")
##
##                if ok:
##                    core.run_plugin()
##                    #pass
####                    log.info("Installing plug-in...")
####                    # TODO:
####                    #ok = core.install_plugin(norm_model, plugin_lib)
####                    ok = True
####                    if not ok:
####                        log.error("Plug-in install failed.")
####                        sys.exit(1)
####
####                    else:
####                        log.info("\nPlug-in installation complete.\n")
####
##                    # Download firmware if needed
##                    #if mq.get('fw-download', 0):
##                    if fw_download:
##                        log.info(log.bold("\nDownloading firmware..."))
##                        try:
##                            d = device.Device(print_uri)
##                        except Error:
##                            log.error("Error opening device. Exiting.")
##                            sys.exit(1)
##
##                        if d.downloadFirmware():
##                            log.info("Done.\n")
##
##                        d.close()


        ppds = cups.getSystemPPDs()

        default_model = utils.xstrip(model.replace('series', '').replace('Series', ''), '_')
        stripped_model = cups.stripModel(default_model)

        # ******************************* PRINT QUEUE SETUP
        if setup_print:
            tui.header("PRINT QUEUE SETUP")

            installed_print_devices = device.getSupportedCUPSDevices(['hp'])  
            log.debug(installed_print_devices)

            if not auto and print_uri in installed_print_devices:
                log.warning("One or more print queues already exist for this device: %s." % 
                    ', '.join(installed_print_devices[print_uri]))

                ok, setup_print = tui.enter_yes_no("\nWould you like to install another print queue for this device", 'n')
                if not ok: sys.exit(0)

        if setup_print:
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
                        printer_name = raw_input(log.bold("\nPlease enter a name for this print queue (m=use model name:'%s'*, q=quit) ?" % printer_default_model))

                        if printer_name.lower().strip() == 'q':
                            log.info("OK, done.")
                            sys.exit(0)

                        if not printer_name or printer_name.lower().strip() == 'm':
                            printer_name = printer_default_model

                        name_ok = True

                        if print_uri in installed_print_devices:
                            for d in installed_print_devices[print_uri]:
                                if printer_name in d:
                                    log.error("A print queue with that name already exists. Please enter a different name.")
                                    name_ok = False
                                    break

                        for c in printer_name:
                            if c in (' ', '#', '/', '%'):
                                log.error("Invalid character '%s' in printer name. Please enter a name that does not contain this character." % c)
                                name_ok = False

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
                print_ppd = mins.keys()[0]
                log.info("\nFound a possible PPD file: %s" % print_ppd)
                log.info("Desc: %s" % mins[print_ppd])

                if not auto:
                    log.info("\nNote: The model number may vary slightly from the actual model number on the device.")
                    ok, ans = tui.enter_yes_no("\nDoes this PPD file appear to be the correct one")
                    if not ok: sys.exit(0)
                    if not ans: enter_ppd = True

            else:
                log.info("")
                log.warn("Found multiple possible PPD files")

                max_ppd_filename_size = 0
                for p in mins:
                    max_ppd_filename_size = max(len(p), max_ppd_filename_size)

                log.info(log.bold("\nChoose a PPD file that most closely matches your device:"))
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

                mins_list = mins.keys()

                for y in range(x):
                    log.info(formatter.compose((str(y), mins_list[y], mins[mins_list[y]])))

                x += 1
                none_of_the_above = y+1
                log.info(formatter.compose((str(none_of_the_above), "(None of the above match)", '')))

                ok, i = tui.enter_range("\nEnter number 0...%d for printer (q=quit) ?" % (x-1), 0, (x-1))
                if not ok: sys.exit(0)

                if i == none_of_the_above:
                    enter_ppd = True
                else:
                    print_ppd = mins_list[i]

            if enter_ppd:
                log.error("Unable to find an appropriate PPD file.")
                enter_ppd = False

                ok, enter_ppd = tui.enter_yes_no("\nWould you like to specify the path to the correct PPD file to use", 'n')
                if not ok: sys.exit(0)
                
                if enter_ppd:
                    ok = False

                    while True:
                        user_input = raw_input(log.bold("\nPlease enter the full filesystem path to the PPD file to use (q=quit) :"))

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

                            ok, ans = tui.enter_yes_no("\nUse this file")
                            if not ok: sys.exit(0)
                            if ans: print_ppd = file_path

                        else:
                            log.error("File not found or not an appropriate (PPD) file.")

                        if ok:
                            break
                else:
                    log.error("PPD file required. Setup cannot continue. Exiting.")
                    sys.exit(1)
                    
            if auto:
                location, info = '', 'Automatically setup by HPLIP'
            else:
                while True:
                    location = raw_input(log.bold("Enter a location description for this printer (q=quit) ?"))

                    if location.strip().lower() == 'q':
                        log.info("OK, done.")
                        sys.exit(0)

                    # TODO: Validate chars
                    break

                while True:
                    info = raw_input(log.bold("Enter additonal information or notes for this printer (q=quit) ?"))

                    if info.strip().lower() == 'q':
                        log.info("OK, done.")
                        sys.exit(0)

                    # TODO: Validate chars
                    break

            log.info(log.bold("\nAdding print queue to CUPS:"))
            log.info("Device URI: %s" % print_uri)
            log.info("Queue name: %s" % printer_name)
            log.info("PPD file: %s" % print_ppd)
            log.info("Location: %s" % location)
            log.info("Information: %s" % info)

            log.debug("Restarting CUPS...")
            status, output = utils.run(restart_cups())
            log.debug("Restart CUPS returned: exit=%d output=%s" % (status, output))

            if not os.path.exists(print_ppd): # assume foomatic: or some such
                status, status_str = cups.addPrinter(printer_name.encode('utf8'), print_uri,
                    location, '', print_ppd, info)
            else:
                status, status_str = cups.addPrinter(printer_name.encode('utf8'), print_uri,
                    location, print_ppd, '', info)

            log.debug("addPrinter() returned (%d, %s)" % (status, status_str))
            
            installed_print_devices = device.getSupportedCUPSDevices(['hp']) 

            log.debug(installed_print_devices)

            if print_uri not in installed_print_devices or \
                printer_name not in installed_print_devices[print_uri]:

                log.error("Printer queue setup failed. Please restart CUPS and try again.")
                sys.exit(1)
            else:
                pass
                # TODO:
                #service.sendEvent(hpssd_sock, EVENT_CUPS_QUEUES_CHANGED, device_uri=print_uri)

            if username:
                import pwd
                user_path = pwd.getpwnam(username)[5]
                user_config_file = os.path.join(user_path, '.hplip.conf')

                if os.path.exists(user_config_file):
                    cfg = Config(user_config_file)
                    cfg.last_used.device_uri = print_uri


        # ******************************* FAX QUEUE SETUP
        if setup_fax and not prop.fax_build:
            log.error("Cannot setup fax - HPLIP not built with fax enabled.")
            setup_fax = False
        
        if setup_fax:
            try:
                from fax import fax
            except ImportError:
                # This can fail on Python < 2.3 due to the datetime module
                setup_fax = False
                log.warning("Fax setup disabled - Python 2.3+ required.")

        log.info("")

        if setup_fax:
            tui.header("FAX QUEUE SETUP")
            installed_fax_devices = device.getSupportedCUPSDevices(['hpfax'])    
            log.debug(installed_fax_devices)

            if not auto and fax_uri in installed_fax_devices:
                log.warning("One or more fax queues already exist for this device: %s." % ', '.join(installed_fax_devices[fax_uri]))
                ok, setup_fax = tui.enter_yes_no("\nWould you like to install another fax queue for this device", 'n')
                if not ok: sys.exit(0)

        if setup_fax:
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
                        fax_name = raw_input(log.bold("\nPlease enter a name for this fax queue (m=use model name:'%s'*, q=quit) ?" % fax_default_model))

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

                        for c in fax_name:
                            if c in (' ', '#', '/', '%'):
                                log.error("Invalid character '%s' in fax name. Please enter a name that does not contain this character." % c)
                                name_ok = False

                        if name_ok:
                            break

            else:
                fax_name = fax_default_model

            log.info("Using queue name: %s" % fax_name)

            fax_type = mq.get('fax-type', FAX_TYPE_NONE)

            if fax_type == FAX_TYPE_SOAP:
                fax_ppd_name = 'HP-Fax2-hplip'
            else:
                fax_ppd_name = 'HP-Fax-hplip'

            for f in ppds:
                if f.find(fax_ppd_name) >= 0:
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
                    location = raw_input(log.bold("Enter a location description for this printer (q=quit) ?"))

                    if location.strip().lower() == 'q':
                        log.info("OK, done.")
                        sys.exit(0)

                    # TODO: Validate chars
                    break

                while True:
                    info = raw_input(log.bold("Enter additonal information or notes for this printer (q=quit) ?"))

                    if info.strip().lower() == 'q':
                        log.info("OK, done.")
                        sys.exit(0)

                    # TODO: Validate chars
                    break

            log.info(log.bold("\nAdding fax queue to CUPS:"))
            log.info("Device URI: %s" % fax_uri)
            log.info("Queue name: %s" % fax_name)
            log.info("PPD file: %s" % fax_ppd)
            log.info("Location: %s" % location)
            log.info("Information: %s" % info)

            if not os.path.exists(fax_ppd): # assume foomatic: or some such
                status, status_str = cups.addPrinter(fax_name.encode('utf8'), fax_uri,
                    location, '', fax_ppd, info)
            else:
                status, status_str = cups.addPrinter(fax_name.encode('utf8'), fax_uri,
                    location, fax_ppd, '', info)
                    
            log.debug("addPrinter() returned (%d, %s)" % (status, status_str))
            
            installed_fax_devices = device.getSupportedCUPSDevices(['hpfax']) 

            log.debug(installed_fax_devices) 

            if fax_uri not in installed_fax_devices or \
                fax_name not in installed_fax_devices[fax_uri]:

                log.error("Fax queue setup failed. Please restart CUPS and try again.")
                sys.exit(1)
            else:
                pass
                # TODO:
                #service.sendEvent(hpssd_sock, EVENT_CUPS_QUEUES_CHANGED, device_uri=fax_uri)


        # ******************************* FAX HEADER SETUP
            tui.header("FAX HEADER SETUP")

            if auto:
                setup_fax = False
            else:
                while True:
                    user_input = raw_input(log.bold("\nWould you like to perform fax header setup (y=yes*, n=no, q=quit) ?")).strip().lower()

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
                d = fax.getFaxDevice(fax_uri, disable_dbus=True)

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
                                current_phone_num = str(d.getPhoneNum())
                                current_station_name = str(d.getStationName())
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
                                    phone_num = raw_input(log.bold("\nEnter the fax phone number for this device (c=use current:'%s'*, q=quit) ?" % current_phone_num))
                                else:
                                    phone_num = raw_input(log.bold("\nEnter the fax phone number for this device (q=quit) ?"))
                                if phone_num.strip().lower() == 'q':
                                    log.info("OK, done.")
                                    sys.exit(0)

                                if current_phone_num and (not phone_num or phone_num.strip().lower() == 'c'):
                                    phone_num = current_phone_num

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
                                    station_name = raw_input(log.bold("\nEnter the name and/or company for this device (c=use current:'%s'*, q=quit) ?" % current_station_name))
                                else:
                                    station_name = raw_input(log.bold("\nEnter the name and/or company for this device (q=quit) ?"))
                                if station_name.strip().lower() == 'q':
                                    log.info("OK, done.")
                                    sys.exit(0)
                                    
                                if current_station_name and (not station_name or station_name.strip().lower() == 'c'):
                                    station_name = current_station_name


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

            tui.header("PRINTER TEST PAGE")

            if auto:
                if testpage_in_auto_mode:
                    print_test_page = True
            else:
                ok, print_test_page = tui.enter_yes_no("\nWould you like to print a test page")
                if not ok: sys.exit(0)

            if print_test_page:
                path = utils.which('hp-testpage')

                if printer_name:
                    param = "-p%s" % printer_name
                else:
                    param = "-d%s" % print_uri

                if len(path) > 0:
                    cmd = 'hp-testpage %s' % param
                else:
                    cmd = 'python ./testpage.py %s' % param

                log.debug(cmd)

                os.system(cmd)

    except KeyboardInterrupt:
        log.error("User exit")

log.info("")
log.info("Done.")

