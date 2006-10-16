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

__version__ = '0.14'
__title__ = 'HPLIP Installer (EXPERIMENTAL)'
__doc__ = "Installer for HPLIP tarball."


# Std Lib
import sys, os, os.path, getopt, re, socket, gzip

# Local
from base.g import *
from base import utils, device, msg, service, dcheck
from base.distros import *


USAGE = [(__doc__, "", "name", True),
         ("Usage: sh ./hplip-install [MODE] [OPTIONS]", "", "summary", True),
         utils.USAGE_SPACE,
         ("[MODE]", "", "header", False),
         #("Enter graphical UI mode:", "-u or --gui (DISABLED)", "option", False),
         ("Run in interactive mode:", "-i or --interactive (Default)", "option", False),
         utils.USAGE_SPACE,
         utils.USAGE_OPTIONS,
         ("Automatic mode (chooses the most common options):", "-a or --auto", "option", False),
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2, utils.USAGE_LOGGING3,
         utils.USAGE_HELP,
         utils.USAGE_SPACE,
         utils.USAGE_NOTES,
         #("1. You must be superuser to run hplip-install", "", "note", False),
        ]

def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)

    utils.format_text(USAGE, typ, __title__, 'hplip-install', __version__)
    sys.exit(0)        


def check_pkg_mgr(): # modified from EasyUbuntu
    """
    Check if any pkg mgr processes are running
    """
    log.debug("Searching for '%s' in 'ps' output..." % package_mgrs)
    
    p = os.popen("ps -U root -o comm")
    pslist = p.readlines()
    p.close()

    for process in pslist:
        p = process.strip()
        if p in package_mgrs:
            return p

    return ''

def getHPLIPVersion():
    version_description, version_public, version_internal = '', '', ''
    ac_init_pat = re.compile(r"""AC_INIT\(\[(.*?)\], *\[(.*?)\], *\[(.*?)\], *\[(.*?)\] *\)""", re.IGNORECASE)
    config_in = file('./configure.in', 'r')

    for c in config_in:
        if c.startswith("AC_INIT"):
            match_obj = ac_init_pat.search(c)
            version_description = match_obj.group(1)
            version_public = match_obj.group(2)
            version_internal = match_obj.group(3)
            name = match_obj.group(4)
            break

    if name != 'hplip':
        log.error("Invalid archive!")
        sys.exit(1)

    return version_description, version_public, version_internal

def getHPIJSVersion():
    hpijs_version_description, hpijs_version = '', ''
    ac_init_pat = re.compile(r"""AC_INIT\(\[(.*?)\], *(.*?), *(.*?), *(.*?) *\)""", re.IGNORECASE)
    config_in = file('./prnt/hpijs/configure.in', 'r')

    for c in config_in:
        if c.startswith("AC_INIT"):
            match_obj = ac_init_pat.search(c)
            hpijs_version_description = match_obj.group(1)
            hpijs_version = match_obj.group(2)
            #version_internal = match_obj.group(3)
            name = match_obj.group(4)
            break

    if name != 'hpijs':
        log.error("Invalid archive!")
        sys.exit(1)

    return hpijs_version_description, hpijs_version

def configure():
    configure_cmd = './configure'

    if selected_options['network']:
        configure_cmd += ' --enable-network-build'
    else:
        configure_cmd += ' --disable-network-build'

    if selected_options['parallel']:
        configure_cmd += ' --enable-pp-build'
    else:
        configure_cmd += ' --disable-pp-build'

    if selected_options['fax']:
        configure_cmd += ' --enable-fax-build'
    else:
        configure_cmd += ' --disable-fax-build'

    if selected_options['gui']:
        configure_cmd += ' --enable-gui-build'
    else:
        configure_cmd += ' --disable-gui-build'

    if selected_options['scan']:
        configure_cmd += ' --enable-scan-build'
    else:
        configure_cmd += ' --disable-scan-build'

    if bitness == 64:
        configure_cmd += ' --libdir=/usr/lib64'

    configure_cmd += ' --prefix=%s' % install_location

    return configure_cmd


def hpijs_configure():
    configure_cmd = './configure'

    if bitness == 64:
        configure_cmd += ' --libdir=/usr/lib64'

    configure_cmd += ' --enable-foomatic-install'
    configure_cmd += ' --disable-hplip-build'

    if selected_options['hpijs-cups']:
        configure_cmd += ' --enable-cups-install'
    else:
        configure_cmd += ' --disable-cups-install'

    return configure_cmd

    
def restart_cups():
    if os.path.exists('/etc/init.d/cups'):
        return su_sudo() % '/etc/init.d/cups restart'
    
    elif os.path.exists('/etc/init.d/cupsys'):
        return su_sudo() % '/etc/init.d/cupsys restart'
    
    else:
        return su_sudo() % 'killall -HUP cupsd'
        
        
def su_sudo():
    if os.geteuid() == 0:
        return '%s'
    else:
        try:
            cmd = distros[distro_name]['su_sudo']
        except KeyError:
            cmd = 'su'
            
        if cmd == 'su':
            return 'su -c "%s"'
        else:
            return 'sudo %s'

def build_cmds(gui):
    return [configure(), 
            'make clean', 
            'make', 
            su_sudo() % 'make install',
            su_sudo() % '/etc/init.d/hplip restart',
            restart_cups()]

def hpijs_build_cmds(gui):
    return [hpijs_configure(), 
            'make clean', 
            'make', 
            su_sudo() % 'make install']


hpssd_sock = None
hpiod_sock = None

def setupHPSSDSock():
    global hpssd_sock

    # This happens after an HPLIP restart, sock
    # make sure the port info is still correct
    prop.run_dir = sys_cfg.dirs.run or '/var/run'

    try:
        prop.hpssd_port = int(file(os.path.join(prop.run_dir, 'hpssd.port'), 'r').read())
    except:
        prop.hpssd_port = 0    

    hpssd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        hpssd_sock.connect((prop.hpssd_host, prop.hpssd_port))
    except socket.error:
        raise Error(ERROR_UNABLE_TO_CONTACT_SERVICE)

def setupHPIODSock():
    global hpiod_sock

    # This happens after an HPLIP restart, sock
    # make sure the port info is still correct
    prop.run_dir = sys_cfg.dirs.run or '/var/run'

    try:
        prop.hpiod_port = int(file(os.path.join(prop.run_dir, 'hpiod.port'), 'r').read())
    except:
        prop.hpiod_port = 0    

    hpiod_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        hpiod_sock.connect((prop.hpiod_host, prop.hpiod_port))
    except socket.error:
        raise Error(ERROR_UNABLE_TO_CONTACT_SERVICE)



# components
# 'name': ('description', [<option list>])
components = {
    'hplip': ("HP Linux Imaging and Printing System", ['base', 'network', 'gui', 'fax', 'scan', 'parallel']),
    'hpijs': ("HP IJS Printer Driver", ['hpijs', 'hpijs-cups'])
}

selected_component = 'hplip'

# options
# name: (<required>, "<display_name>", [<dependency list>]), ...
options = { 
    'base':     (True,  'Required HPLIP base components', []), # HPLIP
    'network' : (False, 'Network/JetDirect I/O', []),
    'gui' :     (False, 'GUI', []),
    'fax' :     (False, 'PC Send Fax', []),
    'scan':     (False, 'Scanning', []),
    'parallel': (False, 'Parallel I/O (LPT)', []),

    # hpijs only
    'hpijs':       (True,  'Required HPIJS base components', []),
    'hpijs-cups' : (False, 'CUPS support for HPIJS', []),
}

# holds whether the user has selected (turned on each option)
# initial values are defaults (for GUI only)
selected_options = {
    'base':        True,
    'network':     True,
    'gui':         True,
    'fax':         True,
    'scan':        True,
    'lsb':         True,
    'parallel':    False,

    # hpijs only
    'hpijs':       True,
    'hpijs-cups' : True,
}

# dependencies
# 'name': (<required for option>, [<option list>], <display_name>, <check_func>), ...
# Note: any change to the list of dependencies must be reflected in base/distros.py
dependencies = {
    'libjpeg':          (True,  ['base', 'hpijs'], "libjpeg - JPEG library", dcheck.check_libjpeg),
    'cups' :            (True,  ['base', 'hpijs-cups'], 'cups - Common Unix Printing System', dcheck.check_cups), 
    'cups-devel':       (True,  ['base'], 'cups-devel- Common Unix Printing System development files', dcheck.check_cups_devel),
    'gcc' :             (True,  ['base', 'hpijs'], 'gcc - GNU Project C and C++ Compiler', dcheck.check_gcc),
    'make' :            (True,  ['base', 'hpijs'], "make - GNU make utility to maintain groups of programs", dcheck.check_make),
    'python-devel' :    (True,  ['base'], "python-devel - Python development files", dcheck.check_python_devel),
    'libpthread' :      (True,  ['base'], "libpthread - POSIX threads library", dcheck.check_libpthread),
    'python2x':         (True,  ['base'], "Python 2.2 or greater - Python programming language", dcheck.check_python2x),
    'gs':               (True,  ['base', 'hpijs'], "GhostScript - PostScript and PDF language interpreter and previewer", dcheck.check_gs),
    'libusb':           (True,  ['base'], "libusb - USB library", dcheck.check_libusb),
    'lsb':              (True,  ['base'], "LSB - Linux Standard Base support", dcheck.check_lsb),

    'sane':             (True,  ['scan'], "SANE - Scanning library", dcheck.check_sane),
    'xsane':            (False, ['scan'], "xsane - Graphical scanner frontend for SANE", dcheck.check_xsane),
    'scanimage':        (False, ['scan'], "scanimage - Shell scanning program", dcheck.check_scanimage),

    'reportlab':        (False, ['fax'], "Reportlab - PDF library for Python", dcheck.check_reportlab), 
    'python23':         (True,  ['fax'], "Python 2.3 or greater - Required for fax functionality", dcheck.check_python23),

    'ppdev':            (True,  ['parallel'], "ppdev - Parallel port support kernel module.", dcheck.check_ppdev),

    'pyqt':             (True,  ['gui'], "PyQt - Qt interface for Python", dcheck.check_pyqt),

    'libnetsnmp-devel': (True,  ['network'], "libnetsnmp-devel - SNMP networking library development files", dcheck.check_libnetsnmp),
    'libcrypto':        (True,  ['network'], "libcrypto - OpenSSL cryptographic library", dcheck.check_libcrypto),

}



log.set_module("hplip-install")

log.debug("euid = %d" % os.geteuid())
mode = INTERACTIVE_MODE
auto = False

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hl:guia', 
        ['help', 'help-rest', 'help-man', 'help-desc',
        'logging=', 'gui', 'interactive', 'auto']) 

except getopt.GetoptError:
    usage()
    sys.exit(1)

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

    elif o in ('-l', '--logging'):
        log_level = a.lower().strip()
        if not log.set_level(log_level):
            usage()

    elif o == '-g':
        log.set_level('debug')

    elif o in ('-i', '--interactive'):
        mode = NON_INTERACTIVE_MODE

    elif o in ('-u', '--gui'):
        mode = GUI_MODE

    elif o in ('-a', '--auto'):
        auto = True
        
        
log_file = os.path.normpath('./install.log')
if os.path.exists(log_file):
    os.remove(log_file)
    
log.set_logfile(log_file)
log.set_where(log.LOG_TO_CONSOLE_AND_FILE)

log.debug("Log file=%s" % log_file)
        

version_description, version_public, version_internal = getHPLIPVersion()
log.debug("HPLIP Description=%s Public version=%s Internal version = %s"  % 
    (version_description, version_public, version_internal))

hpijs_version_description, hpijs_version = getHPIJSVersion()
log.debug("HPIJS Description=%s Version=%s"  % 
    (hpijs_version_description, hpijs_version))
        
prop.version = version_public
utils.log_title(__title__, __version__)    

log.info("Initializing...")

if auto:
    log.note("Running in automatic mode. The most common options will be selected.")

if mode == GUI_MODE:
    log.error("GUI mode has been disabled. Reverting to interactive mode.")
    mode = INTERACTIVE_MODE

# Create the dependencies list in options 
for opt in options:
    update_spinner()
    for d in dependencies:
        if opt in dependencies[d][1]:
            options[opt][2].append(d)

cleanup_spinner()

# have_dependencies
# is each dependency satisfied?
# start with each one 'No'
have_dependencies = {}
for d in dependencies:
    have_dependencies[d] = False

try:
    import pprint
    log.debug_block('distros', pprint.pformat(distros), fmt=True)
    log.debug_block('distros_index', pprint.pformat(distros_index), fmt=True)
    log.debug_block('options', pprint.pformat(options), fmt=True)
    log.debug_block('components', pprint.pformat(components), fmt=True)
    log.debug_block('dependencies', pprint.pformat(dependencies), fmt=True)
    log.debug_block('package_mgrs', pprint.pformat(package_mgrs), fmt=True)
except ImportError:
    log.debug(distros)
    log.debug(distros_index)
    log.debug(options)
    log.debug(components)
    log.debug(dependencies)
    log.debug(package_mgrs)

dcheck.update_ld_output()

for d in dependencies:
    log.debug("***")

    update_spinner()

    log.debug("Checking for dependency '%s'..." % d)
    have_dependencies[d] = dependencies[d][3]()
    log.debug("have %s = %d" % (d, have_dependencies[d]))

cleanup_spinner()

log.debug("******")
for d in dependencies:
    log.debug("have %s = %d" % (d, have_dependencies[d]))
log.debug("******")

log.debug("Running package manager: %s" % check_pkg_mgr())

bitness = utils.getBitness()
log.debug("Bitness = %d" % bitness)

endian = utils.getEndian()
log.debug("Endian = %d" % endian)

distro, distro_version = getDistro()
distro_name = distros_index[distro]

try:
    distro_version_supported = distros[distro_name]['versions'][distro_version]['supported']
except KeyError:
    distro_version_supported = False

log.debug("Distro = %s Distro Name = %s Display Name= %s Version = %s Supported = %s" % 
    (distro, distro_name, distros[distro_name]['display_name'], distro_version, distro_version_supported))

install_location = sys_cfg.dirs.home.replace("/share/hplip", '') or '/usr' # --prefix

hpoj_present = dcheck.check_hpoj()
log.debug("HPOJ = %s" % hpoj_present)

hplip_present = dcheck.check_hplip()
log.debug("HPLIP (prev install) = %s" % hplip_present)


if mode == GUI_MODE:
    if not os.getenv('DISPLAY'):
        mode = INTERACTIVE_MODE
        log.warn("X11 is not running. Switching to interactive (-i) mode.")
    else:
        try:
            from Tkinter import *
            import tkMessageBox
        except ImportError:
            log.warn("Could initialize UI. Switching to interactive (-i) mode.")
            mode = INTERACTIVE_MODE


if mode == GUI_MODE:
    pass # CODE REMOVED

else: # INTERACTIVE_MODE
    def enter_yes_no(question, default="y"):
        default_bool = utils.to_bool(default)
        while True:
            user_input = raw_input(utils.bold(question)).lower().strip()
            if not user_input or user_input == default:
                return default_bool

            if user_input == 'n':
                return False

            if user_input == 'y':
                return True

            if user_input == 'q':
                sys.exit(0)

            log.error("Please enter 'y', 'n', or 'q'.")

    def enter_range(question, min_value, max_value, default_value=None):
        while True:
            user_input = raw_input(utils.bold(question)).lower().strip()

            if default_value is not None:
                if not user_input or user_input == str(default_value):
                    return default_value

            if user_input == 'q':
                sys.exit(0)

            try:
                value_int = int(user_input)
            except:
                log.error('Please enter a number between %d and %d, or "q" to quit.' % (min_value, max_value))
                continue

            if value_int < min_value or value_int > max_value:
                log.error('Please enter a number between %d and %d, or "q" to quit.' % (min_value, max_value))
                continue

            return value_int
            
    def enter_choice(question, choices, default_value):
        choices.append('q')
        while True:
            user_input = raw_input(utils.bold(question)).lower().strip()
            
            if not user_input or user_input == str(default_value):
                return default_value
                
            if user_input == 'q':
                sys.exit(0)
                
            if user_input in choices:
                return user_input
                
            log.error("Please enter %s or press <enter> for the default of '%s'." % (', '.join(["'%s'" % x for x in choices]), default_value))


    def sort_vers(x, y):
        try:
            return cmp(float(x), float(y))
        except ValueError:
            return cmp(x, y)


    def title(text):
        log.info(utils.bold("\n" + text))
        log.info(utils.bold("-"*len(text)))

    try:
        print
        log.note("Defaults for each question are maked with a '*'. Press <enter> to accept the default.")

        if not auto:
            print
            title("INSTALLATION MODE")
            
            user_input = enter_choice("Please choose the installation mode (a=automatic*, c=custom, q=quit) : ", ['a', 'c'], 'a')
            
            if user_input == 'a':
                auto = True
        
        #
        # HPLIP vs. HPLIP INSTALLATION
        #
        
        if auto:
            selected_component = 'hplip'
        else:
            user_input = enter_choice("\nWould you like to install HPLIP (desktop/recommended) or HPIJS only (server/printing only) (d='HPLIP'* (recommended), s='HPIJS only', q=quit) ? ", ['d', 's'], 'd')
            
            if user_input == 'd':
                selected_component = 'hplip'
            else:
                selected_component = 'hpijs'

        #
        # RELEASE NOTES
        #
        
        if selected_component == 'hplip':
            log.info("\nThis installer will install HPLIP version %s on your computer." % version_public)
        else:
            log.info("\nThis installer will install HPIJS version %s on your computer." % hpijs_version)
        
        if not auto and selected_component == 'hplip':
            if os.getenv('DISPLAY'):
                title("VIEW RELEASE NOTES")

                if enter_yes_no("\nWould you like to view the release notes for this version of HPLIP (y=yes, n=no*, q=quit) ? ", default="n"):
                    url = "file://%s" % os.path.join(os.getcwd(), 'doc', 'release_notes.html')
                    log.debug(url)
                    status, output = utils.run("xhost +")
                    utils.openURL(url)
        
            

        num_req_missing = 0
        # required options
        for opt in components[selected_component][1]:
            if options[opt][0]: # required options
                for d in options[opt][2]: # dependencies for option
                    if not have_dependencies[d]: # missing
                        num_req_missing += 1

        x = False
        num_opt_missing = 0
        # not-required options
        for opt in components[selected_component][1]:
            if not options[opt][0]: # not required
                if not x:
                    print
                    title("BUILD/INSTALL OPTIONS")
                    x = True
                
                if not auto:
                    selected_options[opt] = enter_yes_no("\nDo you wish to enable '%s' (y=yes*, n=no, q=quit) ? " % options[opt][1], default="y")
                
                if selected_options[opt]: # only for options that are ON
                    for d in options[opt][2]: # dependencies
                        if not have_dependencies[d]: # missing dependency
                            num_opt_missing += 1
                            
                            
        log.debug("Req missing=%d Opt missing=%d HPOJ=%s HPLIP=%s Component=%s" % (num_req_missing, num_opt_missing, hpoj_present, hplip_present, selected_component))

        if auto and distro != DISTRO_UNKNOWN and distro_version != '0.0':
            log.info("Distro is %s %s" % (distros[distro_name]['display_name'], distro_version))
        
        if num_req_missing or num_opt_missing or (hpoj_present and selected_component == 'hplip'):
            log.info("")
            title("DISTRO/OS SELECTION")
            distro_ok = False

            if distro != DISTRO_UNKNOWN and distro_version != '0.0':
                distro_ok = enter_yes_no('\nIs "%s %s" your correct distro/OS and version (y=yes*, n=no, q=quit) ? ' % (distros[distro_name]['display_name'], distro_version), 'y')

            if not distro_ok:
                distro, distro_version, distro = DISTRO_UNKNOWN, '0.0', 0
                distro_name = distros_index[distro]
                
                log.info(utils.bold("\nChoose the name of the distro/OS that most closely matches your system:\n"))

                max_name = 0
                for d in distros_index:
                    dd = distros[distros_index[d]]
                    if dd['display']:
                        max_name = max(max_name, len(dd['display_name']))

                formatter = utils.TextFormatter(
                        (
                            {'width': 4},
                            {'width': max_name, 'margin': 2},
                        )
                    )

                log.info(formatter.compose(("Num.", "Distro/OS Name")))
                log.info(formatter.compose(('-'*4, '-'*(max_name))))

                x = 0
                for d in distros_index:
                    dd = distros[distros_index[d]]
                    if dd['display']:
                        log.info(formatter.compose((str(x), dd['display_name'])))
                        x += 1

                distro = enter_range("\nEnter number 0...%d (q=quit) ?" % (x-1), 0, x-1)

                distro_name = distros_index[distro]
                distro_display_name = distros[distro_name]['display_name']
                log.debug("Distro = %s Distro Name = %s Display Name= %s" % 
                    (distro, distro_name, distro_display_name))

                if distro != DISTRO_UNKNOWN:
                    versions = distros[distro_name]['versions'].keys()
                    versions.sort(lambda x, y: sort_vers(x, y))

                    log.info(utils.bold('\nChoose the version of "%s" that most closely matches your system:\n' % distro_display_name))

                    formatter = utils.TextFormatter(
                            (
                                {'width': 4},
                                {'width': 40, 'margin': 2},
                            )
                        )

                    log.info(formatter.compose(("Num.", "Distro/OS Version")))
                    log.info(formatter.compose(('-'*4, '-'*40)))

                    log.info(formatter.compose(("0", "Unknown or not listed"))) 

                    x = 1
                    for ver in versions:
                        ver_info = distros[distro_name]['versions'][ver]

                        if ver_info['code_name'] and ver_info['release_date']:
                            text = ver + ' ("' + ver_info['code_name'] + '", Released ' + ver_info['release_date'] + ')'

                        elif ver_info['code_name']:
                            text = ver + ' ("' + ver_info['code_name'] + '")'

                        elif ver_info['release_date']:
                            text = ver + ' (Released ' + ver_info['release_date'] + ')'

                        else:
                            text = ver

                        if not ver_info['supported']:
                            text += " [Unsupported]"

                        log.info(formatter.compose((str(x), text))) 
                        x += 1

                    distro_version_int = enter_range("\nEnter number 0...%d (q=quit) ?" % (x-1), 0, x-1)

                    if distro_version_int == 0:
                        distro_version = '0.0'
                        distro_version_supported = False

                    else:
                        distro_version = versions[distro_version_int - 1]

                        try:
                            distro_version_supported = distros[distro_name]['versions'][distro_version]['supported']
                        except KeyError:
                            distro_version_supported = False

                    log.debug("Distro = %s Distro Name = %s Display Name= %s Version = %s Supported = %s" % 
                        (distro, distro_name, distros[distro_name]['display_name'], distro_version, distro_version_supported))

                if distro == DISTRO_UNKNOWN or not distro_version_supported:
                    if num_req_missing:
                        log.error("The distro/OS that you are running is unsupported and there are required dependencies missing. Please manually install the missing dependencies and then re-run this installer.")
                        
                        log.error("The following REQUIRED dependencies are missing and need to be installed before the installer can be run:")
                        
                        for opt in components[selected_component][1]:
                            if options[opt][0]: # required options
                                for d in options[opt][2]: # dependencies for option
                                    if not have_dependencies[d]: # missing
                                        log.error("Missing REQUIRED dependency: %s (%s)" % (d, dependencies[d][2]))
                        
                        sys.exit(1)
                    
                    log.error("The distro and/or distro version you are using is unsupported.\nYou may still try to use this installer, but some dependency problems may exist after install.")
                    log.error("The following OPTIONAL dependencies are missing and may need to be installed:")
                    
                    for opt in components[selected_component][1]:
                        if not options[opt][0]: # not required
                            if selected_options[opt]: # only for options that are ON
                                for d in options[opt][2]: # dependencies
                                    if not have_dependencies[d]: # missing dependency
        
                                        if dependencies[d][0]: # dependency is required for this option
                                            log.warning("Missing OPTIONAL dependency: %s (%s) [Required for option '%s']" % (d, dependencies[d][2], options[opt][1]))
                                        else:
                                            log.warning("Missing OPTIONAL dependency: %s (%s) [Optional for option '%s']" % (d, dependencies[d][2], options[opt][1]))
                    
                    
                    if not enter_yes_no("\n\nDo you still wish to continue (y=yes*, n=no, q=quit) ?", default="y"):
                        sys.exit(0)


        #
        # INSTALLATION NOTES
        #

        if distro_version_supported:
            try:
                distro_notes = distros[distro_name]['notes']
                ver_notes = distros[distro_name]['versions'][distro_version]['notes']
            except KeyError:
                distro_notes, ver_notes = '', ''
                
            distro_notes = distro_notes.strip()
            ver_notes = ver_notes.strip()
      
            if distro_notes or ver_notes:
                print
                title("INSTALLATION NOTES")
    
                if distro_notes:
                    log.info(distro_notes)
    
                if ver_notes:
                    log.info(ver_notes)
                    
                user_input = raw_input(utils.bold("\nPlease read the installation notes and hit <enter> to continue (<enter>=continue*, q=quit) : ")).lower().strip()
                
                if user_input == 'q':
                    sys.exit(0)

        #
        # REQUIRED DEPENDENCIES
        #
        
        try:
            su_sudo_str = distros[distro_name]['su_sudo']
        except KeyError:
            su_sudo_str = 'su'
        
        depends_to_install = []
        if num_req_missing:
            title("INSTALL MISSING REQUIRED DEPENDENCIES")
            print

            log.warn("There are %d missing REQUIRED dependencies." % num_req_missing)
            log.notice("Installation of dependencies requires an active internet connection.")
            
            if not os.geteuid() == 0:
                log.notice("You may be prompted for a password. Please enter the appropriate password for your system for '%s'" % su_sudo_str)

            # required options
            for opt in components[selected_component][1]:
                if options[opt][0]: # required options
                    for d in options[opt][2]: # dependencies for option

                        if not have_dependencies[d]: # missing
                            log.warning("Missing REQUIRED dependency: %s (%s)" % (d, dependencies[d][2]))

                            ok = False
                            try:
                                package, command = distros[distro_name]['versions'][distro_version]['dependency_cmds'][d]
                            except KeyError:
                                package, command = '', ''

                            if distro_version_supported and (package or command):
                                if auto:
                                    answer = True
                                else:
                                    answer = enter_yes_no("\nWould you like to have this installer install the missing dependency (y=yes*, n=no, q=quit)?", default="y")

                                if answer:
                                    ok = True
                                    log.debug("Adding '%s' to list of dependencies to install." % d)
                                    depends_to_install.append(d)

                            else:
                                log.error("This installer cannot install this dependency for your distro/OS and/or version.")
                            
                            if not ok:
                                log.error("Installation cannot continue without this dependency. Please manually install this dependency and re-run this installer.")                    
                                sys.exit(0)
                            
                            log.info("-"*10)
                            log.info("")

        #
        # OPTIONAL DEPENDENCIES
        #
        
        if num_opt_missing:
            title("INSTALL MISSING OPTIONAL DEPENDENCIES")
            print

            log.notice("Installation of dependencies requires an active internet connection.")

            if not os.geteuid() == 0:
                log.notice("You may be prompted for a password. Please enter the appropriate password for your system for '%s'" % su_sudo_str)
            

            for opt in components[selected_component][1]:
                if not options[opt][0]: # not required
                    if selected_options[opt]: # only for options that are ON
                        for d in options[opt][2]: # dependencies
                            if not have_dependencies[d]: # missing dependency

                                if dependencies[d][0]: # dependency is required for this option
                                    log.warning("Missing REQUIRED dependency for option '%s': %s (%s)" % (options[opt][1], d, dependencies[d][2]))

                                else:
                                    log.warning("Missing OPTIONAL dependency for option '%s': %s (%s)" % (options[opt][1], d, dependencies[d][2]))

                                installed = False
                                
                                try:
                                    package, command = distros[distro_name]['versions'][distro_version]['dependency_cmds'][d]
                                except KeyError:
                                    package, command = '', ''

                                if distro_version_supported and (package or command):
                                    if auto:
                                        answer = True
                                    else:
                                        answer = enter_yes_no("\nWould you like to have this installer install the missing dependency (y=yes*, n=no, q=quit)?", default="y")

                                    if answer:
                                        log.debug("Adding '%s' to list of dependencies to install." % d)
                                        depends_to_install.append(d)

                                    else:
                                        log.warning("Missing dependencies may effect the proper functioning of HPLIP. Please manually install this dependency after you exit this installer.")
                                        log.warning("Note: Options that have REQUIRED dependencies that are missing will be turned off.")
                                        
                                        if dependencies[d][0]:
                                            log.warn("Option '%s' has been turned off." % opt)
                                            selected_options[opt] = False
                                else:
                                    log.error("This installer cannot install this dependency for your distro/OS and/or version.")
                                    
                                    if dependencies[d][0]:
                                        log.warn("Option '%s' has been turned off." % opt)
                                        selected_options[opt] = False
                                        
                            
                                log.info("-"*10)
                                log.info("")


        log.debug(depends_to_install)
        
        if distro_version_supported and (depends_to_install or ((hplip_present or hpoj_present) and selected_component == 'hplip')):
            
            #
            # CHECK FOR RUNNING PACKAGE MANAGER
            #
            
            p = check_pkg_mgr()
            while p:
                user_input = raw_input(utils.bold("\nA running package manager '%s' has been detected. Please quit the package manager and press <enter> to continue (q=quit) :" % p))

                if user_input.strip().lower() == 'q':
                    sys.exit(0)

                p = check_pkg_mgr()
            
            
            #
            # PRE-DEPEND
            #
            
            try:
                pre_cmd = distros[distro_name]['versions'][distro_version]['pre_depend_cmd'] or distros[distro_name]['pre_depend_cmd']
            except KeyError:
                pre_cmd = ''
                
            if pre_cmd:
                if not os.geteuid() == 0:
                    log.notice("You may be prompted for a password. Please enter the appropriate password for your system for '%s' when prompted." % su_sudo_str)
                
                log.info("Running '%s'\nPlease wait, this may take several minutes..." % pre_cmd)
                status, output = utils.run(pre_cmd)
            
            #
            # INSTALL PACKAGES AND RUN COMMANDS
            #
            
            print
            title("DEPENDENCY AND CONFLICT RESOLUTION")
            
            packages_to_install = []
            commands_to_run = []
            try:
                package_mgr_cmd = distros[distro_name]['package_mgr_cmd']
            except KeyError:
                package_mgr_cmd = ''
            
            log.debug("Preparing to install packages and run commands...")
            
            for d in depends_to_install:
                log.debug("*** Processing dependency: %s" % d)
                package, command = distros[distro_name]['versions'][distro_version]['dependency_cmds'][d]
                
                if package:
                    log.debug("Package '%s' will be installed to satisfy dependency '%s'." % (package, d))
                    packages_to_install.append(package)
                    
                if command:
                    log.debug("Command '%s' will be run to satisfy dependency '%s'." % (command, d))
                    commands_to_run.append(command)
                    
                
            if package_mgr_cmd and packages_to_install:
                packages_to_install = ' '.join(packages_to_install)
                cmd = utils.cat(package_mgr_cmd)
                log.debug("Package manager command: %s" % cmd)
                
                if not os.geteuid() == 0:
                    log.notice("You may be prompted for a password. Please enter the appropriate password for your system for '%s' when prompted." % su_sudo_str)
                
                log.info("Running '%s'\nPlease wait, this may take several minutes..." % cmd)
                status, output = utils.run(cmd)
    
                if status != 0:
                    log.error("Install command failed with error code %d" % status)
                
            if commands_to_run:
                for cmd in commands_to_run:
                    #cmd = su_sudo() % cmd
                    log.debug(cmd)
                    log.info("Running '%s'\nPlease wait, this may take several minutes..." % cmd)
                    status, output = utils.run(cmd)
                    
                    if status != 0:
                        log.error("Install command failed with error code %d" % status)
               
            
            #
            # HPOJ REMOVAL
            #
            
            hpoj_present = dcheck.check_hpoj() # dependencies may have installed it as a sub-dependency

            if hpoj_present and selected_component == 'hplip' and distro_version_supported:
                log.error("HPOJ is installed and/or running. HPLIP is not compatible with HPOJ.")

                hpoj_remove_cmd = distros[distro_name]['hpoj_remove_cmd']

                if hpoj_remove_cmd:
                    if auto:
                        answer = True
                    else:
                        answer = enter_yes_no("\nWould you like to have this installer attempt to uninstall HPOJ (y=yes*, n=no, q=quit) ? ")

                    if answer:
                        
                        if not os.geteuid() == 0:
                            log.notice("You may be prompted for a password. Please enter the appropriate password for your system for '%s' when prompted." % su_sudo_str)
                    
                        log.info("\nRunning '%s'\nPlease wait, this may take several minutes..." % hpoj_remove_cmd)
                        status, output = utils.run(hpoj_remove_cmd)

                        if status != 0:
                            log.error("HPOJ removal failed. Please manually stop/remove/uninstall HPOJ and then re-run this installer.")
                            sys.exit(1)
                        else:
                            hpoj_present = dcheck.check_hpoj()

                            if hpoj_present:
                                log.error("HPOJ removal failed. Please manually stop/remove/uninstall HPOJ and then re-run this installer.")
                                sys.exit(1)
                            else:
                                log.info("Removal successful.")
                    else:
                        log.error("Please stop/remove/uninstall HPOJ and then re-run this installer.")
                        sys.exit(0)

                else:
                    log.error("Please stop/remove/uninstall HPOJ and then re-run this installer.")
                    sys.exit(0)
            
            
            #
            # HPLIP REMOVE
            #
            
            hplip_present = dcheck.check_hplip() # dependencies may have installed it as a sub-dependency

            if hplip_present and selected_component == 'hplip' and distro_version_supported:
                failed = True
                log.warn("A previous install of HPLIP is installed and/or running.")

                hplip_remove_cmd = distros[distro_name]['hplip_remove_cmd']

                if hplip_remove_cmd:
                    if auto:
                        answer = True
                    else:
                        answer = enter_yes_no("\nWould you like to have this installer attempt to uninstall the previously installed HPLIP (y=yes*, n=no, q=quit) ? ")

                    if answer:
                        if not os.geteuid() == 0:
                            log.notice("You may be prompted for a password. Please enter the appropriate password for your system for '%s' when prompted." % su_sudo_str)
                    
                        cmd = su_sudo() % '/etc/init.d/hplip stop'
                        log.info("Running '%s'\nPlease wait, this may take several minutes..." % cmd)
                        status, output = utils.run(cmd)
                        
                        log.info("\nRunning '%s'\nPlease wait, this may take several minutes..." % hplip_remove_cmd)
                        status, output = utils.run(hplip_remove_cmd)

                        if status == 0:
                            hplip_present = dcheck.check_hplip()

                            if not hplip_present:
                                log.info("Removal successful.")
                                failed = False

                else:
                    log.error("The previously installed version of HPLIP may conflict with the new one being installed.")
                    log.error("It is recommended that you quit this installer, and manually remove HPLIP before continuing.")
                    sys.exit(0)
                    
                if failed:
                    log.error("HPLIP removal failed. The previous install may have been installed using a tarball or this installer.")
                    log.error("Continuing to run installer - this installation should overwrite the previous one.")
                    
            
            # 
            # DEPENDENCIES RE-CHECK
            #
                
            #status, ld_output = run('%s -p' % os.path.join(ldconfig, 'ldconfig'))
            dcheck.update_ld_output()

            # re-check dependencies
            for d in dependencies:
                log.debug("***")
            
                update_spinner()
            
                log.debug("Checking for dependency '%s'..." % d)
                have_dependencies[d] = dependencies[d][3]()
                log.debug("have %s = %d" % (d, have_dependencies[d]))
                
            cleanup_spinner()
            
            # re-check missing required options
            for opt in components[selected_component][1]:
                if options[opt][0]: # required options
                    if not have_dependencies[d]: # missing
                        for d in options[opt][2]: # dependencies for option
                                log.error("A required dependency '%s' is still missing." % d)
                                #log.error("This installer cannot install this dependency for your distro/OS and/or version.")
                                log.error("Installation cannot continue without this dependency. Please manually install this dependency and re-run this installer.")                    
                                sys.exit(0)

    
            # re-check missing optional options
            for opt in components[selected_component][1]:
                if not options[opt][0]: # not required
                    if selected_options[opt]: # only for options that are ON
                        for d in options[opt][2]: # dependencies
                            if not have_dependencies[d]: # missing dependency
                                if dependencies[d][0]: # required for option
                                    log.warn("An optional dependency '%s' is still missing." % d)
                                    log.warn("Option '%s' has been turned off." % opt)
                                    selected_options[opt] = False
                                else:
                                    log.warn("An optional dependency '%s' is still missing." % d)
                                    log.warn("Some features may not function as expected.")
            #
            # POST-DEPEND
            #

            try:
                post_cmd = distros[distro_name]['versions'][distro_version]['post_depend_cmd'] or distros[distro_name]['post_depend_cmd']
            except KeyError:
                post_cmd = ''
                
            if post_cmd:
                if not os.geteuid() == 0:
                    log.notice("You may be prompted for a password. Please enter the appropriate password for your system for '%s' when prompted." % su_sudo_str)
                
                log.info("Running '%s'\nPlease wait, this may take several minutes..." % post_cmd)
                status, output = utils.run(post_cmd)

        #
        # INSTALL LOCATION
        #

        if selected_component == 'hplip':
            if auto:
                install_location = '/usr'
            else:
                print
                while True:
                    if install_location == '/usr':
                        s = ' (recommended)'
                    else:
                        s = ", r='/usr' (recommended)"
    
                    user_input = raw_input(utils.bold("\nEnter the install location (--prefix) (<enter>='%s'*%s, q=quit) : " % (install_location, s))).strip()
    
                    if not user_input:
                        break
    
                    if user_input.lower() == 'q':
                        sys.exit(0)
    
                    if user_input.lower() == 'r':
                        install_location = '/usr'
                        break
    
                    if not os.path.exists(user_input):
                        log.error("Path not found, please enter an existing path.")
                        continue
    
                    install_location = user_input
                    break
    
            log.debug("Install location = %s" % install_location)


            # Ready...
            if not auto:
                print
                title("READY TO BUILD AND INSTALL")

                user_input = raw_input(utils.bold("\nReady to perform build and install. Press <enter> to continue (<enter>=continue*, q=quit) : ")).lower().strip()

                if user_input == 'q':
                    sys.exit(0)

            log.info("")
            title("BUILD AND INSTALL")

            if not os.geteuid() == 0:
                log.notice("Note: You may be prompted for a password. Please enter the appropriate password for your system for '%s' when prompted." % su_sudo_str)

            for cmd in build_cmds(False):
                log.info("\nRunning '%s'\nPlease wait, this may take several minutes..." % cmd)
                status, output = utils.run(cmd)
                print

                if status != 0:
                    log.error("'%s' command failed with status code %d" % (cmd, status))
                    sys.exit(0)
                else:
                    log.info("Command completed successfully.")


            #
            # Install printer
            #

            if auto:
                install_printer = True
            else:
                install_printer = enter_yes_no("\nWould you like to setup a printer now (y=yes*, n=no, q=quit) ? ", default="y")

            if install_printer:
                log.info("Please make sure your printer is connected and powered on at this time.")

                if os.getenv('DISPLAY') and selected_options['gui'] and utils.checkPyQtImport():
                    x = "python ./setup.py -u"
                    os.system(su_sudo() % x)
                
                else:
                    io_choice = 'u'
                    io_choices = ['u']
                    io_list = '(u=USB*'
    
                    if selected_options['network']:
                        io_list += ', n=network'
                        io_choices.append('n')
    
                    if selected_options['parallel']:
                        io_list += ', p=parallel'
                        io_choices.append('p')
    
                    io_list += ', q=quit)'
    
                    if len(io_choices) > 1:
                        io_choice = enter_choice("\nWhat I/O type will the newly installed printer use %s ? " % io_list, io_choices, 'u')
    
                    log.debug("IO choice = %s" % io_choice)
    
                    
                    auto_str = ''
                    if auto:
                        auto_str = '--auto'
                        
                    if io_choice == 'n':
                        ip = ''
                        ip_pat = re.compile(r"""\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b""", re.IGNORECASE)
    
                        while True:
                            user_input = raw_input(utils.bold("\nEnter the IP address or hostname for the printer (q=quit) : ")).lower().strip()
    
                            if user_input == 'q':
                                sys.exit(0)
    
                            if ip_pat.search(user_input) is not None:
                                log.debug("IP match")
                                ip = user_input
                                break
    
                            try:
                                param = socket.gethostbyname(user_input)
                            except socket.gaierror:
                                log.debug("Gethostbyname() failed.")
                            else:
                                log.debug("gethostbyname() match")
                                ip = user_input
                                break
    
                            log.error("Invalid or unknown IP address/hostname")
    
                        if ip:
                            x = "python ./setup.py -i %s %s" % (ip, auto_str)
                            os.system(su_sudo() % x)
    
                    elif io_choice == 'p':
                        x = "python ./setup.py -i -b par %s" % auto_str
                        os.system(su_sudo() % x)
    
                    elif io_choice == 'u':
                        x = "python ./setup.py -i -b usb %s" % auto_str
                        os.system(su_sudo() % x)
    

        else: # hpijs only
            print
            title("READY TO BUILD AND INSTALL")

            # Ready...
            if not auto:
                user_input = raw_input(utils.bold("\nReady to perform build and install. Press <enter> to continue (<enter>=continue*, q=quit) : ")).lower().strip()

                if user_input == 'q':
                    sys.exit(0)

            title("BUILD AND INSTALL")

            os.chdir('prnt/hpijs')

            for cmd in hpijs_build_cmds(False):
                log.info("\nRunning '%s'\nPlease wait, this may take several minutes..." % cmd)
                status, output = utils.run(cmd)
                print

                if status != 0:
                    log.error("'%s' command failed with status code %d" % (cmd, status))
                    sys.exit(0)
                else:
                    log.info("Build and install successful.")


            os.chdir("../..")

    except KeyboardInterrupt:
        log.info("")
        log.error("Aborted.")

sys.exit(0)


