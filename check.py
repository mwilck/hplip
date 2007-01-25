#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) Copyright 2003-2007 Hewlett-Packard Development Company, L.P.
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

__version__ = '5.2'
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
from installer import dcheck, distros


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

build_str = "HPLIP will not build, install, and/or function properly without this dependency."

dependencies = {
    'libjpeg':          (True, "libjpeg - JPEG library", build_str, dcheck.check_libjpeg),
    'cups' :            (True, "cups - Common Unix Printing System", build_str, dcheck.check_cups), 
    'cups-devel':       (True, 'cups-devel- Common Unix Printing System development files', build_str, dcheck.check_cups_devel),
    'gcc' :             (True, 'gcc - GNU Project C and C++ Compiler', build_str, dcheck.check_gcc),
    'make' :            (True, "make - GNU make utility to maintain groups of programs", build_str, dcheck.check_make),
    'python-devel' :    (True, "python-devel - Python development files", build_str, dcheck.check_python_devel),
    'libpthread' :      (True, "libpthread - POSIX threads library", build_str, dcheck.check_libpthread),
    'python2x':         (True, "Python 2.2 or greater - Python programming language", build_str, dcheck.check_python2x),
    'gs':               (True, "GhostScript - PostScript and PDF language interpreter and previewer", build_str, dcheck.check_gs),
    'libusb':           (True, "libusb - USB library", build_str, dcheck.check_libusb),
    'lsb':              (True, "LSB - Linux Standard Base support", build_str, dcheck.check_lsb),

    'sane':             (True,  "SANE - Scanning library", "HPLIP scanning feature will not function.", dcheck.check_sane),
    'xsane':            (False, "xsane - Graphical scanner frontend for SANE", "This is an optional package.", dcheck.check_xsane),
    'scanimage':        (False, "scanimage - Shell scanning program", "This is an optional package.", dcheck.check_scanimage),

    'reportlab':        (False, "Reportlab - PDF library for Python", "HPLIP faxing will not have the coverpage feature.", dcheck.check_reportlab), 
    'python23':         (True,  "Python 2.3 or greater - Required for fax functionality", "HPLIP faxing feature will not function.", dcheck.check_python23),

    'ppdev':            (False,  "ppdev - Parallel port support kernel module.", "Parallel port (LPT) connected printers will not work with HPLIP", dcheck.check_ppdev),

    'pyqt':             (True,  "PyQt - Qt interface for Python", "HPLIP GUIs will not function.", dcheck.check_pyqt),

    'libnetsnmp-devel': (True,  "libnetsnmp-devel - SNMP networking library development files", "Networked connected printers will not work with HPLIP", dcheck.check_libnetsnmp),
    'libcrypto':        (True,  "libcrypto - OpenSSL cryptographic library", "Networked connected printers will not work with HPLIP", dcheck.check_libcrypto),

}

def header(text):
    c = len(text)
    log.info("")
    log.info("-"*(c+4))
    log.info("| "+text+" |")
    log.info("-"*(c+4))
    log.info("")

num_errors = 0

try:
    log.set_module("hp-check")

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hl:g', 
            ['help', 'help-rest', 'help-man', 'help-desc', 'logging=']) 

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

        elif o == '--help-desc':
            print __doc__,
            sys.exit(0)

        elif o in ('-l', '--logging'):
            log_level = a.lower().strip()

        elif o == '-g':
            log_level = 'debug'


    if not log.set_level(log_level):
        usage()

    utils.log_title(__title__, __version__)    

    header("SYSTEM INFO")

    log.info(utils.bold("Basic system information:"))
    status, output = utils.run('uname -a')
    log.info("%s" % output.replace('\n', ''))

    log.info(utils.bold("\nDetected distro (/etc/issue):"))
    distro, distro_version = distros.getDistro()
    distro_name = distros.distros_index[distro]
    log.info("%s %s" % (distro_name, distro_version))

    log.info(utils.bold("\nDetected distro (lsb_release):"))
    lsb_release = utils.which("lsb_release")
    if lsb_release:
        cmd = os.path.join(lsb_release, "lsb_release")
        status, vendor = utils.run(cmd + " -i")
        vendor = vendor.split(':')[1].strip()
        status, ver = utils.run(cmd + " -r")
        ver = ver.split(':')[1].strip()
        status, code = utils.run(cmd + " -c")
        code = code.split(':')[1].strip()
        log.info("%s %s (%s)" % (vendor, ver, code))
    else:
        log.error("lsb_release not found.")

    log.info(utils.bold("\nCurrently installed HPLIP version..."))
    v = sys_cfg.hplip.version
    home = sys_cfg.dirs.home

    if v:
        log.info("HPLIP %s currently installed in '%s'." % (v, home))

        log.info(utils.bold("\nCurrent contents of '/etc/hp/hplip.conf' file:"))
        output = file('/etc/hp/hplip.conf', 'r').read()
        log.info(output)

    else:
        log.info("Not found.")

    log.info(utils.bold("\nHPLIP running?"))
    hplip_present = dcheck.check_hplip_running()
    if hplip_present:
        log.info("Yes, HPLIP is running (OK).")
    else:
        log.info("No, HPLIP is not running (OK).")

    log.info(utils.bold("\nHPOJ running?"))
    hplip_present = dcheck.check_hpoj()
    if hplip_present:
        log.error("Yes, HPOJ is running. HPLIP is not compatible with HPOJ. To run HPLIP, please remove HPOJ.")
        num_errors += 1
    else:
        log.info("No, HPOJ is not running (OK).")


    log.info(utils.bold("\nChecking Python version..."))
    ver = sys.version_info
    log.debug("sys.version_info = %s" % repr(ver))
    ver_maj = ver[0]
    ver_min = ver[1]
    ver_pat = ver[2]

    if ver_maj == 2:
        if ver_min >= 1:
            log.info("OK, version %d.%d.%d installed" % ver[:3])
        else:
            log.error("Version %d.%d.%d installed. Please update to Python >= 2.1" % ver[:3])
            sys.exit(1)


    log.info(utils.bold("\nChecking PyQt version..."))

    # PyQt
    try:
        import qt
    except ImportError:
        num_errors += 1
        log.error("Not found!")
    else:
        # check version of Qt
        qtMajor = int(qt.qVersion().split('.')[0])

        if qtMajor < MINIMUM_QT_MAJOR_VER:
            log.error("Incorrect version of Qt installed. Ver. 3.0.0 or greater required.")
        else:
            #check version of PyQt
            try:
                pyqtVersion = qt.PYQT_VERSION_STR
            except:
                pyqtVersion = qt.PYQT_VERSION

            while pyqtVersion.count('.') < 2:
                pyqtVersion += '.0'

            (maj_ver, min_ver, pat_ver) = pyqtVersion.split('.')

            if pyqtVersion.find('snapshot') >= 0:
                log.error("A non-stable snapshot version of PyQt is installed (%s)." % pyqtVersion)
                num_errors += 1
            else:
                try:
                    maj_ver = int(maj_ver)
                    min_ver = int(min_ver)
                    pat_ver = int(pat_ver)
                except ValueError:
                    maj_ver, min_ver, pat_ver = 0, 0, 0

                if maj_ver < MINIMUM_PYQT_MAJOR_VER or \
                    (maj_ver == MINIMUM_PYQT_MAJOR_VER and min_ver < MINIMUM_PYQT_MINOR_VER):
                    num_errors += 1
                    log.error("HPLIP may not function properly with the version of PyQt that is installed (%d.%d.%d)." % (maj_ver, min_ver, pat_ver))
                    log.error("Ver. %d.%d or greater required." % (MINIMUM_PYQT_MAJOR_VER, MINIMUM_PYQT_MINOR_VER))
                else:
                    log.info("OK, version %d.%d installed." % (maj_ver, min_ver))


    log.info(utils.bold("\nChecking SIP version..."))

    sip_ver = None
    try:
        import pyqtconfig
    except ImportError:
        pass
    else:
        sip_ver = pyqtconfig.Configuration().sip_version_str 

    if sip_ver is not None:
        log.info("OK, Version %s installed" % sip_ver)
    else:
        num_errors += 1
        log.error("SIP not installed or version not found.")


    header("DEPENDENCIES")

    dcheck.update_ld_output()
    log.info("")

    for d in dependencies:
        log.debug("***")

        log.info(utils.bold("Checking for dependency %s..." % dependencies[d][1]))

        if dependencies[d][3]():
            log.info("OK, found.")
        else:
            num_errors += 1
            log.error("Not found!")

            if dependencies[d][0]:
                log.error("This is a REQUIRED dependency. Please make sure that this dependency is installed before installing or running HPLIP.")
            else:
                log.info("This is an OPTIONAL dependency. Some HPLIP functionality may not function properly.")

        log.info("")

    header("INSTALLED PRINTERS")

    from base import device
    lpstat_pat = re.compile(r"""^device for (.*): (.*)""", re.IGNORECASE)

    status, output = utils.run('lpstat -v')
    log.info("")

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
        non_hp = False
        for p in cups_printers:
            try:
                back_end, is_hp, bus, model, serial, dev_file, host, port = \
                    device.parseDeviceURI(p[1])
            except Error:
                back_end, is_hp, bus, model, serial, dev_file, host, port = \
                    '', False, '', '', '', '', '', 1

            if is_hp:
                x = 'Yes'
            else:
                x = 'No'
                non_hp = True

            log.info(utils.bold(p[0]))
            log.info(utils.bold('-'*len(p[0])))
            log.info("Device URI: %s" % p[1])
            log.info("Installed in HPLIP? %s" % x)

            ppd = os.path.join('/etc/cups/ppd', p[0] + '.ppd')

            if os.path.exists(ppd):
                log.info("PPD: %s" % ppd)
                nickname_pat = re.compile(r'''\*NickName:\s*\"(.*)"''', re.MULTILINE)

                f = file(ppd, 'r').read(4096)

                try:
                    desc = nickname_pat.search(f).group(1)
                except AttributeError:
                    desc = ''

                log.info("PPD Description: %s" % desc)

                status, output = utils.run('lpstat -p%s' % p[0])
                log.info("Printer status: %s" % output)

                if back_end == 'hpfax' and desc != 'HP Fax':
                    num_errors += 1
                    log.error("Incorrect PPD file for fax queue '%s'. Fax queue must use 'HP-Fax-hplip.ppd'." % p[0])

                elif back_end == 'hp' and desc == 'HP Fax':
                    num_errors += 1
                    log.error("Incorrect PPD file for a print queue '%s'. Print queues must not use 'HP-Fax-hplip.ppd'." % p[0])

                elif back_end not in ('hp', 'hpfax'):
                    log.error("Printer is not HPLIP installed. Printers must use the hp: or hpfax: CUPS backend to function in HPLIP.")
                    num_errors += 1

            log.info("")

    else:
        log.warn("No queues found.")

    header("SANE CONFIGURATION")
    log.info(utils.bold("'hpaio' in /etc/sane.d/dll.conf'..."))
    f = file('/etc/sane.d/dll.conf', 'r')
    found = False
    for line in f:
        if 'hpaio' in line:
            found = True

    if found:
        log.info("OK, found. SANE backend 'hpaio' is properly set up.")
    else:
        num_errors += 1
        log.error("Not found. SANE backend 'hpaio' not properly setup (needs to be added to /etc/sane.d/dll.conf).")


    log.info(utils.bold("\nChecking output of 'scanimage -L'..."))
    if utils.which('scanimage'):
        status, output = utils.run("scanimage -L")
        log.info(output)
    else:
        log.error("scanimage not found.")

    header("PYTHON EXTENSIONS")

    log.info(utils.bold("Checking 'cupsext' CUPS extension..."))
    try:
        import cupsext
    except ImportError:
        num_errors += 1
        log.error("Not found! Please reinstall HPLIP and check for the proper installation of cupsext.")
    else:
        log.info("OK, found.")

    log.info(utils.bold("\nChecking 'pcardext' Photocard extension..."))
    try:
        import pcardext
    except ImportError:
        num_errors += 1
        log.error("Not found! Please reinstall HPLIP and check for the proper installation of pcardext.")
    else:
        log.info("OK, found.")

    log.info("")

    if num_errors:
        log.info("\n%d errors were detected." % num_errors)
        log.info("Please refer to the installation instructions at:")
        log.info("http://hplip.sourceforge.net/install/index.html\n")

    else:
        print utils.red("\nNo errors detected.")

except KeyboardInterrupt:
    log.warn("Aborted")
