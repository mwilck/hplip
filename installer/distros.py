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
# Author: Don Welch, Aaron Albright
#

__version__ = '1.0'
__date__ = '2006-09-14'

# StdLib
import os

# Local
from base.g import *
from base import utils


# Distro IDs
# These must match the indexes used in the 'index' field 
# in the distros data structure
DISTRO_UNKNOWN = 0
DISTRO_MEPIS = 1 # (Debian based)
DISTRO_DEBIAN = 2 #
DISTRO_SUSE = 3 #
DISTRO_MANDRIVA = 4 # (RPM based)
DISTRO_FEDORA = 5 # (RPM based)
DISTRO_REDHAT = 6 # Old Red Hat 8/9 (RPM based)
DISTRO_RHEL = 7 # (RPM based)
DISTRO_SLACKWARE = 8 #
DISTRO_GENTOO = 9 #
DISTRO_TURBO = 10 # Japan/China (RH based)
DISTRO_REDFLAG = 11 # (RPM based)
DISTRO_UBUNTU = 12 # (Debian based)
DISTRO_XANDROS = 13 # (Debian based)
DISTRO_FREEBSD = 14 #
DISTRO_LINSPIRE = 15 # (Debian baseD)
DISTRO_ARK = 16 # (RPM based)
DISTRO_PCLINUXOS = 17 # (PCLinuxOS/RPM based)
DISTRO_ASIANUX = 18 # Red Flag+MIRACLE+Haansoft (based on RHEL)
DISTRO_PCBSD = 19 # (FreeBSD based)
DISTRO_SUNWAH = 20 # China (Debian based)
DISTRO_MIRACLE = 21 # Japan (Oracle)
DISTRO_XTEAM = 22 # China
DISTRO_CENTOS = 23 # (RHEL based)
DISTRO_COCREATE = 24 # China
DISTRO_HAANSOFT = 25 # Korea
DISTRO_NEOSHINE = 26 # China (CS2C)
DISTRO_DARWIN = 27 # (BSD based)
DISTRO_OPENBSD = 28 #
DISTRO_NETBSD = 29 #
DISTRO_DRAGONFLYBSD = 30 # (FreeBSD based)
DISTRO_YELLOWDOG = 31 # PPC


def getDistro():
    distro, distro_version = DISTRO_UNKNOWN, '0.0'

    found = False

    lsb_release = utils.which("lsb_release")
    if lsb_release:
        cmd = os.path.join(lsb_release, "lsb_release")

        status, name = utils.run(cmd + " -i")
        name = name.split(':')[1].strip().lower()

        status, distro_version = utils.run(cmd + " -r")
        distro_version = distro_version.split(':')[1].strip()

        status, code = utils.run(cmd + " -c")
        code = code.split(':')[1].strip()

        #log.debug("LSB: %s %s (%s)" % (name, distro_version, code))

        for d in distros:
            if name.find(d) > -1:
                distro = distros[d]['index']
                found = True
                break

    if not found:
        try:
            name = file('/etc/issue', 'r').read().lower().strip()
        except IOError:
            # Some O/Ss don't have /etc/issue (Mac)
            return DISTRO_UNKNOWN, '0.0'

        found = False
        for d in distros:
            if name.find(d) > -1:
                distro = distros[d]['index']
                found = True
            else:
                for x in distros[d].get('alt_names', '').split(','):
                    if x and name.find(x) > -1:
                        distro = distros[d]['index']
                        found = True
                        break
            
            if found:
                break
                
        if found:
            for n in name.split(): 
                if '.' in n:
                    m = '.'.join(n.split('.')[:2])
                else:
                    m = n
    
                try:
                    distro_version = str(float(m))
                except ValueError:
                    try:
                        distro_version = str(int(m))
                    except ValueError:
                        distro_version = '0.0'
                    else:
                        break
                else:
                    break

    return distro, distro_version



# Helper functions
def __copy_cmds(distro, src_ver, dst_ver):
    """ Copy the cmds from one version to another. """
    distros[distro]['versions'][dst_ver]['dependency_cmds'].update(distros[distro]['versions'][src_ver]['dependency_cmds'])

def __set_ver_cmds(distro, ver, cmds):
    """ Set the cmds for a given distro version. """
    distros[distro]['versions'][ver]['dependency_cmds'].update(cmds)

def __update_ver_cmd(distro, ver, dependency, cmd):
    """ Update an existing dependency cmd. """
    distros[distro]['versions'][ver]['dependency_cmds'][dependency] = cmd


# distros:
#
# { '<distro_name>' : { 
#    'alt_names': '<other names for this distro>',
#    'display_name': '<name to use for UIs>',
#    'display': True, | False,   # whether to show this distro in a distro list in a UI
#    'notes': '', # distro notes
#    'index' : <n>,   # Must match the enummerated values DISTRO_*
#    'package_mgrs' : [...list of possible package managers (as from ps listing)...],
#    'package_mgr_cmd': '<package mgr cmd for this distro>, #
#    'su_sudo' : 'su' | 'sudo'   # whether to use 'su' or 'sudo' on this distro
#    'pre_depend_cmd': '<cmd to run before dependency checks>', # optional
#    'post_depend_cmd': '<cmd to run after build and install>', # optional
#    'hpoj_remove_cmd': '<cmd to remove hpoj from system>',  # optional
#    'hplip_remove_cmd': '<cmd to remove hplip from system>',  # optional
#    'versions': { 'ver' : '<version name or number> : {'code_name': '<code name of version, if known>', 
#                                                       'release_date': <release date: dd/mm/yyyy or mm/yyyy or yyyy>',
#                                                        'supported': True|False,   # is this version supported?
#                                                        'dependency_cmds': { 
#                                                                             '<dependency>' : '('<package>', '<install cmds for dependency>'), 
#                                                                             ... 
#                                                                           },
#                                                        'notes': '<version notes>', # combines with distro notes
#                                                        'pre_depend_cmd': '<cmd to run before dependency checks>', # overrides distro pre_depend_cmd
#                                                        'post_depend_cmd': '<cmd to run after dependency checks>', # overrides distro post_depend_cmd
#                                                       }
#                 },
#    },
# }
#


# NOTE: Do NOT put dependency cmds in this data structure here
distros = \
{
    'ubuntu': {
        'alt_names': 'kubunbu,edubuntu,xubuntu',
        'display_name': 'Ubuntu',
        'display': True,
        'notes': '',
        'index': 12,
        'package_mgrs': ["dpkg", "apt-get","synaptic","update-manager", "adept", "adept-notifier", "aptitude"],
        'package_mgr_cmd' : 'sudo apt-get install --yes --force-yes $packages_to_install',
        'pre_depend_cmd': ['sudo dpkg --configure -a', 'sudo apt-get install --yes --force-yes -f ', 'sudo apt-get update', 'xterm -e sudo apt-get install --yes --force-yes postfix'],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': 'sudo apt-get remove --yes --force-yes hpoj',
        'hplip_remove_cmd': 'sudo apt-get remove --yes --force-yes hplip hpijs',
        'su_sudo' : 'sudo',
        'versions': {
            '5.04': {
                'code_name': 'Hoary', 
                'release_date': '5/2004', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': 'Enable the universe/multiverse repositories. See: https://help.ubuntu.com/community/Repositories/Ubuntu for more information.', 
                'pre_depend_cmd': [ ],
                'post_depend_cmd':  [],
            },
            '5.1': {
                'code_name': 'Breezy', 
                'release_date': '10/2005', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': 'Enable the universe/multiverse repositories. See: https://help.ubuntu.com/community/Repositories/Ubuntu for more information.', 
                'pre_depend_cmd': [],
                'post_depend_cmd': [],
            },
            '6.06': {
                'code_name': 'Dapper', 
                'release_date': '6/2006', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': 'Enable the universe/multiverse repositories. See: https://help.ubuntu.com/community/Repositories/Ubuntu for more information.',
                'pre_depend_cmd': [],
                'post_depend_cmd': [],
            },
            '6.10': {
                'code_name': 'Edgy', 
                'release_date': '10/2006', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': 'Enable the universe/multiverse repositories. See: https://help.ubuntu.com/community/Repositories/Ubuntu for more information.', 
                'pre_depend_cmd': [],
                'post_depend_cmd': [],
            },
            '7.04': {
                'code_name': 'Feisty', 
                'release_date': '', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': 'Enable the universe/multiverse repositories. See: https://help.ubuntu.com/community/Repositories/Ubuntu for more information.', 
                'pre_depend_cmd': [],
                'post_depend_cmd': [],
            },
        },
    },


     'debian': {
        'alt_names': '',
        'display_name': 'Debian',
        'display': True,
        'notes': '',
        'index': 2,
        'package_mgrs': ["dpkg", "apt-get","synaptic","update-manager", "adept", "adept-notifier", "aptitude"],            
        'package_mgr_cmd' : 'su -c "apt-get install --yes $packages_to_install"',
        'pre_depend_cmd': ['su -c "dpkg --configure -a"', 'su -c "apt-get install -f"', 'su -c "apt-get update"'],
        'post_depend_cmd': [],
        'su_sudo' : 'su',
        'hpoj_remove_cmd': 'su -c "apt-get remove --yes hpoj"',
        'hplip_remove_cmd': 'su -c "apt-get remove --yes hplip hpijs"',
        'versions': {
            '2.2': {
                'code_name': 'Potato', 
                'release_date': '15/8/2000', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '3.0': {
                'code_name': 'Woody', 
                'release_date': '19/7/2002', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '3.1': {
                'code_name': 'Sarge', 
                'release_date': '6/6/2005', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        }
    },

     'suse': {
        'alt_names': '',
        'display_name': 'SUSE Linux',
        'display': True,
        'notes': '',
        'index': 3,
        'package_mgrs': ["yast", "yast2"],
        'package_mgr_cmd': 'xterm -e su -c "yast --install $packages_to_install"',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'su_sudo' : 'su',
        'hpoj_remove_cmd': 'su -c "yast --remove hpoj"',
        'hplip_remove_cmd': 'su -c "yast --remove hplip"',
        'versions': {
            '9.0': {
                'code_name': '', 
                'release_date': '15/11/2003', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '9.1': {
                'code_name': '', 
                'release_date': '23/4/2004', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '9.2': {
                'code_name': '', 
                'release_date': '25/10/2004', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '9.3': {
                'code_name': '', 
                'release_date': '16/4/2005', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '10.0': {
                'code_name': '', 
                'release_date': '5/10/2005', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': 'Before proceeding, open another terminal and run: installation_sources -a http://suse.mirrors.tds.net/pub/opensuse/distribution/SL-10.0-OSS/inst-source/\n and then run: installation_sources -a http://mirrors.kernel.org/suse/i386/10.0/SUSE-Linux10.0-GM-Extra/', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '10.1': {
                'code_name': '', 
                'release_date': '11/5/2006', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': 'Add http://suse.mirrors.tds.net/pub/opensuse/distribution/SL-10.1/inst-source/  and http://mirrors.kernel.org/suse/i386/10.1/SUSE-Linux10.1-GM-Extra to your YaST installation sources.', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '10.2': {
                'code_name': '', 
                'release_date': '12/7/2006', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': ['xterm -e su -c "installation_sources -a http://download.opensuse.org/distribution/10.2/repo/oss/"', 'xterm -e su -c "installation_sources -a http://download.opensuse.org/distribution/10.2/repo/non-oss/"','xterm -e su -c "installation_sources -a http://download.opensuse.org/distribution/10.2/repo/debug/"',], 
                'post_depend_cmd': [],
            },
        },
    },

     'mandriva': {
        'alt_names': 'Mandrakelinux, Mandrake Linux',
        'display_name': 'Mandriva Linux',
        'display': True,
        'notes': '',
        'index': 4,
        'package_mgrs': ["urpmi"],
        'package_mgr_cmd': 'su - -c "urpmi --auto $packages_to_install"',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'su_sudo' : 'su',
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            '9.1': {
                'code_name': 'Bamboo', 
                'release_date': '2003', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': 'Before proceeding, please add the "contrib", "main", and "updates" installation sources to your URPMI configuration.  Open your browser and go to http://easyurpmi.zarb.org/ and follow the instructions provided and then proceed with the HPLIP install. Also you may wish to turn off the cdrom1-12 media sources to speed up the process.', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '9.2': {
                'code_name': 'Fivestar', 
                'release_date': '2003', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': 'Before proceeding, please add the "contrib", "main", and "updates" installation sources to your URPMI configuration.  Open your browser and go to http://easyurpmi.zarb.org/ and follow the instructions provided and then proceed with the HPLIP install. Also you may wish to turn off the cdrom1-12 media sources to speed up the process.', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '10.0': {
                'code_name': 'Community and official', 
                'release_date': '2004', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': 'Before proceeding, please add the "contrib", "main", and "updates" installation sources to your URPMI configuration./n Open your browser and go to http://easyurpmi.zarb.org/ and follow the instructions provided and then proceed with the HPLIP install. Also you may wish to turn off the cdrom1-12 media sources to speed up the process.', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '10.1': {
                'code_name': 'Official', 
                'release_date': '2004', 
                'supported': False, 
                'dependency_cmds': {}, 'notes': 'Before proceeding, please add the "contrib", "main", and "updates" installation sources to your URPMI configuration./n Open your browser and go to http://easyurpmi.zarb.org/ and follow the instructions provided and then proceed with the HPLIP install. Also you may wish to turn off the cdrom1-12 media sources to speed up the process.', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '10.2': {
                'code_name': 'Limited edition 2005', 
                'release_date': '2005', 
                'supported': False, 
                'dependency_cmds': {}, 'notes': 'Before proceeding, please add the "contrib", "main", and "updates" installation sources to your URPMI configuration./n Open your browser and go to http://easyurpmi.zarb.org/ and follow the instructions provided and then proceed with the HPLIP install. Also you may wish to turn off the cdrom1-12 media sources to speed up the process.', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '2006.0': {
                'code_name': '2k6', 
                'release_date': '2005', 
                'supported': True, 
                'dependency_cmds': {}, 'notes': 'Before proceeding, please add the "contrib", "main", and "updates" installation sources to your URPMI configuration./n Open your browser and go to http://easyurpmi.zarb.org/ and follow the instructions provided and then proceed with the HPLIP install. Also you may wish to turn off the cdrom1-12 media sources to speed up the process.', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '2007.0': {
                'code_name': '2k7', 
                'release_date': '2007', 
                'supported': True, 
                'dependency_cmds': {}, 'notes': 'Before proceeding, please add the "contrib", "main", and "updates" installation sources to your URPMI configuration./n Open your browser and go to http://easyurpmi.zarb.org/ and follow the instructions provided and then proceed with the HPLIP install. Also you may wish to turn off the cdrom1-12 media sources to speed up the process.', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'fedora': {
        'alt_names': 'Fedora Core',
        'display': True,
        'display_name': 'Fedora',
        'notes': 'SELinux must be disabled for HPLIP to function properly. Please disable SELinux before continuing.',
        'index': 5,
        'package_mgrs': ["yum", "rpm", "up2date"],
        'package_mgr_cmd': 'su -c "yum -y -d 10 -e 1 install $packages_to_install"',
        'pre_depend_cmd': ['su -c "yum clean all"'],
        'post_depend_cmd': [],
        'su_sudo' : 'su',
        'hpoj_remove_cmd': 'su -c "yum -y -d 10 -e 1 remove hplip hpijs"',
        'hplip_remove_cmd': 'su -c "yum -y -d 10 -e 1 remove hplip hpijs"',
        'versions': {
            '1.0': {
                'code_name': 'Yarrow', 
                'release_date': '5/11/2003', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '2.0': {
                'code_name': 'Tettnang', 
                'release_date': '18/5/2004',
                'supported':  False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '3.0': {
                'code_name': 'Heidelberg', 
                'release_date': '8/11/2004', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '4.0': {
                'code_name': 'Stentz', 
                'release_date': '13/6/2005', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '5.0': {
                'code_name': 'Bordeaux', 
                'release_date': '20/3/2006', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '5.92': {
                'code_name': 'RC3', 
                'release_date': '20/3/2006', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '6.0': {
                'code_name': '', 
                'release_date': '20/3/2006', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '6': {
                'code_name': '', 
                'release_date': '20/3/2006', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'redhat': {
        'alt_names': '',
        'display_name': 'Red Hat',
        'display': True,
        'notes': '',
        'index': 6,
        'package_mgrs': ["yum", "rpm", "up2date"],
        'package_mgr_cmd': 'rpm install $packages_to_install',
        'su_sudo' : 'su',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            '8.0': {
                'code_name': 'Psyche', 
                'release_date': '9/2002', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '9.0': {
                'code_name': 
                'Shrike', 'release_date': '3/2003', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'rhel': {
        'alt_names': 'red hat enterprise linux',
        'display_name': 'Red Hat Enterprise Linux',
        'display': True,
        'notes': '',
        'index': 7,
        'su_sudo' : 'su',
        'package_mgrs': ["yum", "rpm", "up2date"],
        'package_mgr_cmd': 'rpm install $packages_to_install',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            '3.0': {
                'code_name': 'Taroon', 
                'release_date': '22/10/2003', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '4.0': {
                'code_name': 'Nahant', 
                'release_date': '15/2/2005', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'slackware': {
        'alt_names': '',
        'display_name': 'Slackware Linux',
        'notes': '',
        'index': 8,
        'display': False,
        'su_sudo' : 'su',
        'package_mgrs': [],
        'package_mgr_cmd' : '',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            '10.0': {
                'code_name': '', 
                'release_date': '23/6/2004', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '10.1': {
                'code_name': '', 
                'release_date': '2/2/2005', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '10.2': {
                'code_name': '', 
                'release_date': '14/9/2005', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '9.0': {
                'code_name': '', 
                'release_date': '19/3/2003', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
            '9.1': {
                'code_name': '', 
                'release_date': '26/9/2003', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'gentoo': {
        'alt_names': '',
        'display_name': 'Gentoo Linux',
        'notes': '',
        'index': 9,
        'display': False,
        'su_sudo' : 'su',
        'package_mgrs': [],
        'package_mgr_cmd' : '',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            'any': {
                'code_name': '', 
                'release_date': '', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'turbolinux': {
        'alt_names': '',
        'display_name': 'Turbolinux',
        'notes': '',
        'index': 10,
        'display': False,
        'su_sudo' : 'su',
        'package_mgrs': [],
        'package_mgr_cmd' : '',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            'any': {
                'code_name': '', 
                'release_date': '', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'redflag': {
        'alt_names': '',
        'display_name': 'Red Flag Linux',
        'notes': '',
        'index': 11,
        'display': False,
        'su_sudo' : 'su',
        'package_mgrs': [],
        'package_mgr_cmd' : '',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            'any': {
                'code_name': '', 
                'release_date': '', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'mepis': {
        'alt_names': '',
        'display_name': 'Mepis',
        'display': True,
        'notes': '',
        'index': 1,
        'package_mgrs': ["dpkg", "apt-get","synaptic","update-manager", "adept", "adept-notifier", "aptitude"],
        'package_mgr_cmd' : 'sudo apt-get install --yes $packages_to_install',
        'pre_depend_cmd': ['sudo dpkg --configure -a', 'sudo apt-get update'],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': 'sudo apt-get remove --yes hpoj',
        'hplip_remove_cmd': 'sudo apt-get remove --yes hplip hpijs',
        'su_sudo' : 'sudo',
        'versions': {
            '6.0': {
                'code_name': 'mepis', 
                'release_date': '7/2006', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': 'Before proceeding please enable the universe/multiverse repositories in Synaptic or Apt.', 
                'pre_depend_cmd': [],
                'post_depend_cmd':  ''
            },
        },
    },

    'xandros': {
        'alt_names': '',
        'display_name': 'Xandros',
        'notes': '',
        'index': 13,
        'display': False,
        'su_sudo' : 'su',
        'package_mgrs': [],
        'package_mgr_cmd' : '',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            'any': {
                'code_name': '', 
                'release_date': '', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'freebsd': {
        'alt_names': '',
        'display_name': 'FreeBSD',
        'notes': '',
        'index': 14,
        'display': False,
        'su_sudo' : 'su',
        'package_mgrs': [],
        'package_mgr_cmd' : '',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            'any': {
                'code_name': '', 
                'release_date': '', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'linspire': {
        'alt_names': '',
        'display_name': 'Linspire',
        'notes': 'The installer will uncomment out several Debian repositories to complete the installation.  This may pull in packages that are incompatible with Linspire and may cause CNR to stop working.',
        'index': 15,
        'display': False,
        'su_sudo' : 'su',
        'package_mgrs': ["apt-get", ],
        'package_mgr_cmd' : 'su -c "apt-get install --yes $packages_to_install"',
        'pre_depend_cmd': ['su -c "cp -f /etc/apt/sources.list /etc/apt/sources.hplip', 'echo deb ftp://mirrors.kernel.org/debian/ sid main contrib non-free | sudo tee -a /etc/apt/sources.list', 'echo deb-src ftp://mirrors.kernel.org/debian/ sid main contrib non-free | sudo tee -a /etc/apt/sources.list', 'su -c "apt-get update"'],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': 'su -c "apt-get remove hpoj"',
        'hplip_remove_cmd': 'su -c "apt-get remove hplip hpijs"',
        'versions': {
            '5.0': {
                'code_name': 'Linspire', 
                'release_date': '', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'ark': {
        'alt_names': '',
        'display_name': 'Ark Linux',
        'notes': '',
        'index': 16,
        'display': False,
        'su_sudo' : 'su',
        'package_mgrs': [],
        'package_mgr_cmd' : '',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            'any': {
                'code_name': '', 
                'release_date': '', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'pclinuxos': {
        'alt_names': '',
        'display_name': 'PCLinuxOS',
        'notes': '',
        'index': 17,
        'display': True,
        'su_sudo' : 'su',
        'package_mgrs': ["apt-get", "synaptic"],
        'package_mgr_cmd' : 'su -c "apt-get install --yes $packages_to_install"',
        'pre_depend_cmd': ['su -c "apt-get update"'],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': 'su -c "apt-get remove --yes hpoj"',
        'hplip_remove_cmd': 'su -c "apt-get remove --yes hplip hpijs"',
        'versions': {
            '2006.0': {
                'code_name': 'Texstar', 
                'release_date': '', 
                'supported': True, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'asianux': {
        'alt_names': '',
        'display_name': 'AsianUX',
        'notes': '',
        'index': 18,
        'display': False,
        'su_sudo' : 'su',
        'package_mgrs': [],
        'package_mgr_cmd' : '',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            'any': {
                'code_name': '', 
                'release_date': '', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'pcbsd': {
        'alt_names': '',
        'display_name': 'PC-BSD',
        'notes': '',
        'index': 19,
        'display': False,
        'su_sudo' : 'su',
        'package_mgrs': [],
        'package_mgr_cmd' : '',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            'any': {
                'code_name': '', 
                'release_date': '', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'sun wah rays lx': {
        'alt_names': '',
        'display_name': 'Sun Wah RAYS LX',
        'notes': '',
        'index': 20,
        'display': False,
        'su_sudo' : 'su',
        'package_mgrs': [],
        'package_mgr_cmd' : '',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            'any': {
                'code_name': '', 
                'release_date': '', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'miracle': {
        'alt_names': '',
        'display_name': 'Miracle Linux',
        'notes': '',
        'index': 21,
        'display': False,
        'su_sudo' : 'su',
        'package_mgrs': [],
        'package_mgr_cmd' : '',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            'any': {
                'code_name': '', 
                'release_date': '', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

         'centos': {
        'alt_names': '',
        'display_name': 'CentOS',
        'notes': '',
        'index': 23,
        'display': False,
        'su_sudo' : 'su',
        'package_mgrs': [],
        'package_mgr_cmd' : '',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
            'any': {
                'code_name': '', 
                'release_date': '', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    },

     'unknown' : {
        'index': 0,
        'display': True, # Must be 'True' 
        'notes': '',
        'display_name' : 'Unknown or not listed',
        'package_mgrs': [],
        'package_mgr_cmd' : '',
        'pre_depend_cmd': [],
        'post_depend_cmd': [],
        'hpoj_remove_cmd': '',
        'hplip_remove_cmd': '',
        'versions': {
                'any': {
                'code_name': '', 
                'release_date': '', 
                'supported': False, 
                'dependency_cmds': {}, 
                'notes': '', 
                'pre_depend_cmd': [], 
                'post_depend_cmd': [],
            },
        },
    }
}

# Create the 'reverse' index (index# --> distro name)
distros_index = {}
for d in distros:
    distros_index[distros[d]['index']] = d

# Package manager names
package_mgrs = []
for d in distros:
    for a in distros[d]['package_mgrs']:
        if a not in package_mgrs:
            package_mgrs.append(a)


################### UBUNTU (1) ###################
__set_ver_cmds('ubuntu', '5.04',
{ 
'cups' : ('libcupsys', ''),
'cups-devel': ('libcupsys-dev', ''),
'gcc' : ('build-essential', ''),
'make' : ('build-essential', ''),
'python-devel' : ('python-dev', ''),
'libpthread' : ('build-essential', ''),
'python2x': ('python', ''),
'gs': ('gs-esp', ''),
'libusb': ('libusb-dev', ''),
'lsb': ('lsb', ''),
'sane': ('sane', ''),
'xsane': ('xsane', ''),
'scanimage': ('sane-utils', ''),
'reportlab': ('python-reportlab', ''), 
'ppdev': ('', 'modprobe ppdev && cp -f /etc/modules /etc/modules.hplip && echo ppdev | sudo tee -a /etc/modules'),
'pyqt': ('python-qt3', ''),
'python23': ('python', ''),
'libnetsnmp-devel': ('libsnmp9-dev', ''),
'libcrypto': ('openssl', ''),
'libjpeg': ('libjpeg62-dev', ''),
})

__copy_cmds('ubuntu', '5.04', '5.1') # 5.10 = 5.04
__copy_cmds('ubuntu', '5.1', '6.06') # 6.06 = 5.10
__copy_cmds('ubuntu', '6.06', '6.10') # 6.06 = 6.10
__copy_cmds('ubuntu', '6.10', '7.04') 
__update_ver_cmd('ubuntu', '5.04', 'gs', ('gs', ''))
__update_ver_cmd('ubuntu', '5.04', 'libnetsnmp-devel', ('libsnmp5-dev', ''))
__update_ver_cmd('ubuntu', '5.1', 'libnetsnmp-devel', ('libsnmp5-dev', ''))
__update_ver_cmd('ubuntu', '6.06', 'cups', ('libcupsys2', ''))
__update_ver_cmd('ubuntu', '6.10', 'cups', ('libcupsys2', ''))
__update_ver_cmd('ubuntu', '7.04', 'cups', ('libcupsys2', ''))
__update_ver_cmd('ubuntu', '6.06', 'cups-devel', ('libcupsys2-dev', ''))
__update_ver_cmd('ubuntu', '6.10', 'cups-devel', ('libcupsys2-dev', ''))
__update_ver_cmd('ubuntu', '7.04', 'cups-devel', ('libcupsys2-dev', ''))
__update_ver_cmd('ubuntu', '5.1', 'cups-devel', ('libcupsys2-dev', ''))
__update_ver_cmd('ubuntu', '5.1', 'pyqt', ('python2.4-qt3', ''))

################### DEBIAN (2) ###################
__set_ver_cmds('debian', '2.2',
{ 
'cups' : ('cupsys cupsys-client', ''),
'cups-devel' : ('libcupsys2-dev', ''),
'gcc' : ('gcc g++', ''),
'make' : ('make', ''),
'python-devel' : ('python-dev', ''),
'libpthread' : ('libc6', ''),
'python2x' : ('python', ''),
'gs' : ('gs-esp', ''),
'libusb' : ('libusb-dev', ''),
'lsb' : ('lsb', ''),
'sane' : ('sane', ''),
'xsane' : ('sane', ''),
'scanimage' : ('sane-utils', ''),
'reportlab' : ('python-reportlab', ''),
'ppdev': ('', 'modprobe ppdev && cp -f /etc/modules /etc/modules.hplip && echo ppdev | sudo tee -a /etc/modules'),
'pyqt' : ('python-qt3', ''),
'python23' : ('python', ''),
'libnetsnmp-devel' : ('libsnmp5-dev', ''),
'libcrypto' : ('libsnmp5-dev', ''),
'libjpeg' : ('libjpeg62-dev', ''),
})

__copy_cmds('debian', '2.2', '3.0') # 2.2 = 3.0
__copy_cmds('debian', '3.0', '3.1') # 3.0 = 3.1


################### SUSE (3) ###################
__set_ver_cmds('suse', '9.0',
{ 
'cups' : ('cups cups-client', ''),
'cups-devel' : ('cups-devel', ''),
'gcc' : ('gcc-c++', ''),
'make' : ('make', ''),
'python-devel' : ('python-devel python-xml', ''),
'libpthread' : ('glibc', ''),
'python2x' : ('python', ''),
'gs' : ('ghostscript-library', ''),
'libusb' : ('libusb libusb-devel', ''),
'lsb' : ('lsb', ''),
'sane' : ('sane', ''),
'xsane' : ('xsane', ''),
'scanimage' : ('sane', ''),
'reportlab' : ('', ''),
'ppdev': ('', 'modprobe ppdev && cp -f /etc/init.d/boot.local /etc/init.d/boot.hplip && echo modprobe ppdev | sudo tee -a /etc/init.d/boot.local'),
'pyqt' : ('python-qt', ''),
'python23' : ('python', ''),
'libnetsnmp-devel' : ('net-snmp-devel', ''),
'libcrypto' : ('openssl', ''),
'libjpeg' : ('libjpeg-devel', ''),
})
__copy_cmds('suse', '9.0', '9.1') # 9.0 = 9.1
__copy_cmds('suse', '9.1', '9.2') # 9.1 = 9.2
__copy_cmds('suse', '9.2', '9.3') # 9.2 = 9.3
__copy_cmds('suse', '9.3', '10.0') # 9.2 = 9.3
__copy_cmds('suse', '10.0', '10.1') # 10.0 = 10.1
__copy_cmds('suse', '10.1', '10.2') # 10.0 = 10.1
__update_ver_cmd('suse', '10.2', 'reportlab', ('', ''))
__update_ver_cmd('suse', '10.2', 'libusb', ('libusb', ''))

################### MANDRIVA (4) ###################
__set_ver_cmds('mandriva', '10.0',
{ 
'cups' : ('cups', ''),
'cups-devel' : ('cups-devel', ''),
'gcc' : ('gcc-c++', ''),
'make' : ('make', ''),
'python-devel' : ('python-devel', ''),
'libpthread' : ('glibc-i18ndata-2.3.5-5mdk.i586 glibc_lsb-2.3.4-2mdk.i586', ''),
'python2x' : ('python', ''),
'gs' : ('ghostscript', ''),
'libusb' : ('libusb0.1_4-devel', ''),
'lsb' : ('lsb-3.0-6mdk.i586 lsb-release-2.0-1mdk.i586', ''),
'sane' : ('sane', ''),
'xsane' : ('xsane', ''),
'scanimage' : ('sane-utils', ''),
'reportlab' : ('python-reportlab', ''),
'ppdev': ('', 'modprobe ppdev'),
'pyqt' : ('PyQt', ''),
'python23' : ('python', ''),
'libnetsnmp-devel' : ('libsnmp0-devel', ''),
'libcrypto' : ('libcryptopp5 libcryptopp5-devel', ''),
'libjpeg' : ('libjpeg62-dev', ''),
})

__copy_cmds('mandriva', '10.0', '10.1') 
__copy_cmds('mandriva', '10.1', '10.2')
__copy_cmds('mandriva', '10.2', '2006.0')
__copy_cmds('mandriva', '2006.0', '2007.0')
__update_ver_cmd('mandriva', '2007.0', 'lsb', ('lsb-core-3.1-7mdv2007.0 lsb-release-2.0-4mdk', ''))
__update_ver_cmd('mandriva', '2007.0', 'libpthread', ('glibc-i18ndata-2.4-4mdk glibc_lsb-2.3.6-1mdk', ''))

################### FEDORA (5) ###################
__set_ver_cmds('fedora', '3.0',
{ 
'cups' : ('cups', ''),
'cups-devel' : ('cups-devel', ''),
'gcc' : ('gcc-c++', ''),
'make' : ('make', ''),
'python-devel' : ('python-devel', ''),
'libpthread' : ('glibc-headers', ''),
'python2x' : ('python', ''),
'gs' : ('ghostscript', ''),
'libusb' : ('libusb-devel', ''),
'lsb' : ('redhat-lsb', ''),
'sane' : ('sane-backends', ''),
'xsane' : ('xsane', ''),
'scanimage' : ('sane-frontends', ''),
'reportlab' : ('python-reportlab', ''),
'ppdev': ('', 'su -c "/sbin/modprobe ppdev"'),
'pyqt' : ('PyQt', ''),
'python23' : ('python', ''),
'libnetsnmp-devel' : ('net-snmp-devel', ''),
'libcrypto' : ('net-snmp-devel', ''),
'libjpeg' : ('libjpeg-devel', ''),
})

__copy_cmds('fedora', '3.0', '4.0') 
__copy_cmds('fedora', '4.0', '5.0') 
__copy_cmds('fedora', '5.0', '5.92') 
__copy_cmds('fedora', '5.92', '6.0') 
__copy_cmds('fedora', '5.92', '6') 
__update_ver_cmd('fedora', '3.0', 'pyqt', ('sip PyQt',''))


################### REDHAT (6) ###################
__set_ver_cmds('redhat', '8.0',
{ 
'cups' : ('cups', ''),
'cups-devel' : ('cups-devel', ''),
'gcc' : ('gcc-c++', ''),
'make' : ('make', ''),
'python-devel' : ('python-devel', ''),
'libpthread' : ('glibc-headers', ''),
'python2x' : ('python', ''),
'gs' : ('ghostscript', ''),
'libusb' : ('libusb-devel', ''),
'lsb' : ('redhat-lsb', ''),
'sane' : ('sane-backends', ''),
'xsane' : ('xsane', ''),
'scanimage' : ('sane-frontends', ''),
'reportlab' : ('python-reportlab', ''),
'ppdev': ('', 'modprobe ppdev && cp -f /etc/modules /etc/modules.hplip && echo ppdev | sudo tee -a /etc/modules'),
'pyqt' : ('PyQt', ''),
'python23' : ('python', ''),
'libnetsnmp-devel' : ('net-snmp-devel', ''),
'libcrypto' : ('net-snmp-devel', ''),
'libjpeg' : ('libjpeg-devel', ''),
})

__copy_cmds('redhat', '8.0', '9.0') 

################### RHEL (7) ###################
__set_ver_cmds('rhel', '3.0',
{ 
'cups' : ('cups', ''),
'cups-devel' : ('cups-devel', ''),
'gcc' : ('gcc-c++', ''),
'make' : ('make', ''),
'python-devel' : ('python-devel', ''),
'libpthread' : ('glibc-headers', ''),
'python2x' : ('python', ''),
'gs' : ('ghostscript', ''),
'libusb' : ('libusb-devel', ''),
'lsb' : ('redhat-lsb', ''),
'sane' : ('sane-backends', ''),
'xsane' : ('xsane', ''),
'scanimage' : ('sane-frontends', ''),
'reportlab' : ('python-reportlab', ''),
'ppdev': ('', 'modprobe ppdev && cp -f /etc/modules /etc/modules.hplip && echo ppdev | sudo tee -a /etc/modules'),
'pyqt' : ('PyQt', ''),
'python23' : ('python', ''),
'libnetsnmp-devel' : ('net-snmp-devel', ''),
'libcrypto' : ('net-snmp-devel', ''),
'libjpeg' : ('libjpeg-devel', ''),
})

__copy_cmds('rhel', '3.0', '4.0') 

################### SLACKWARE (8) ###################
__set_ver_cmds('slackware', '10.0',
{ 
'cups' : ('cups', ''),
'cups-devel' : ('cups-devel', ''),
'gcc' : ('gcc-c++', ''),
'make' : ('make', ''),
'python-devel' : ('python-devel', ''),
'libpthread' : ('glibc-headers', ''),
'python2x' : ('python', ''),
'gs' : ('ghostscript', ''),
'libusb' : ('libusb-devel', ''),
'lsb' : ('redhat-lsb', ''),
'sane' : ('sane-backends', ''),
'xsane' : ('xsane', ''),
'scanimage' : ('sane-frontends', ''),
'reportlab' : ('python-reportlab', ''),
'ppdev': ('', 'modprobe ppdev && cp -f /etc/modules /etc/modules.hplip && echo ppdev | sudo tee -a /etc/modules'),
'pyqt' : ('PyQt', ''),
'python23' : ('python', ''),
'libnetsnmp-devel' : ('net-snmp-devel', ''),
'libcrypto' : ('net-snmp-devel', ''),
'libjpeg' : ('libjpeg-devel', ''),
})

__copy_cmds('slackware', '10.0', '10.1') 
__copy_cmds('slackware', '10.1', '10.2') 
__copy_cmds('slackware', '10.2', '9.0') 
__copy_cmds('slackware', '9.0', '9.1') 


################### GENTOO (9) ###################
__set_ver_cmds('gentoo', 'any',
{ 
'cups' : ('cups', ''),
'cups-devel' : ('cups-devel && yum -y -d 10 -e 1 remove hplip hpijs', ''),
'gcc' : ('gcc-c++', ''),
'make' : ('make', ''),
'python-devel' : ('python-devel', ''),
'libpthread' : ('glibc-headers', ''),
'python2x' : ('python', ''),
'gs' : ('ghostscript', ''),
'libusb' : ('libusb-devel', ''),
'lsb' : ('redhat-lsb', ''),
'sane' : ('sane-backends', ''),
'xsane' : ('xsane', ''),
'scanimage' : ('sane-frontends', ''),
'reportlab' : ('python-reportlab', ''),
'ppdev': ('', 'modprobe ppdev && cp -f /etc/modules /etc/modules.hplip && echo ppdev | sudo tee -a /etc/modules'),
'pyqt' : ('PyQt', ''),
'python23' : ('python', ''),
'libnetsnmp-devel' : ('net-snmp-devel', ''),
'libcrypto' : ('net-snmp-devel', ''),
'libjpeg' : ('libjpeg-devel', ''),
})

#__copy_cmds('gentoo', 'any', 'any') # not needed

################### TURBOLINUX (10) ###################

################### REDFLAG (11) ###################

################### MEPIS (12) ###################
__set_ver_cmds('mepis', '6.0',
{ 
'cups' : ('libcupsys2', ''),
'cups-devel': ('libcupsys2-dev', ''),
'gcc' : ('build-essential', ''),
'make' : ('build-essential', ''),
'python-devel' : ('python-dev', ''),
'libpthread' : ('build-essential', ''),
'python2x': ('python', ''),
'gs': ('gs-esp', ''),
'libusb': ('libusb-dev', ''),
'lsb': ('lsb', ''),
'sane': ('sane', ''),
'xsane': ('xsane', ''),
'scanimage': ('sane-utils', ''),
'reportlab': ('python-reportlab', ''), 
'ppdev': ('', 'modprobe ppdev && cp -f /etc/modules /etc/modules.hplip && echo ppdev | sudo tee -a /etc/modules'),
'pyqt': ('python-qt3', ''),
'python23': ('python', ''),
'libnetsnmp-devel': ('libsnmp9-dev', ''),
'libcrypto': ('openssl', ''),
'libjpeg': ('libjpeg62-dev', ''),
})

#__copy_cmds('gentoo', 'any', 'any') # not needed
################### XANDROS (13) ###################

################### FREEBSD (14) ###################

################### LINSPIRE (15) ###################
__set_ver_cmds('linspire', '5.0',
{ 
'cups' : ('libcupsys2', ''),
'cups-devel': ('libcupsys2-dev', ''),
'gcc' : ('gcc g++', ''),
'make' : ('make', ''),
'python-devel' : ('python-dev', ''),
'libpthread' : ('libpthread20', ''),
'python2x': ('python', ''),
'gs': ('gs-esp', ''),
'libusb': ('libusb-0.1-4', ''),
'lsb': ('lsb lsb-desktop lsb-qt4 libqt3-mt', ''),
'sane': ('sane', ''),
'xsane': ('xsane', ''),
'scanimage': ('sane-utils', ''),
'reportlab': ('python-reportlab', ''), 
'ppdev': ('', 'modprobe ppdev && cp -f /etc/modules /etc/modules.hplip && echo ppdev | sudo tee -a /etc/modules'),
'pyqt': ('python-qt3', ''),
'python23': ('python', ''),
'libnetsnmp-devel': ('libnet1-dev', ''),
'libcrypto': ('openssl', ''),
'libjpeg': ('libjpeg62-devel', ''),
})

################### ARK (16) ###################

################### PCLINUXOS (17) ###################
__set_ver_cmds('pclinuxos', '2006.0',
{ 
'cups' : ('libcups2', ''),
'cups-devel': ('libcups2-devel', ''),
'gcc' : ('gcc-c++', ''),
'make' : ('make', ''),
'python-devel' : ('python-devel', ''),
'libpthread' : ('glibc', ''),
'python2x': ('python', ''),
'gs': ('ghostscript', ''),
'libusb': ('libusb0.1_4-devel', ''),
'lsb': ('lsb', ''),
'sane': ('sane-frontends', ''),
'xsane': ('xsane', ''),
'scanimage': ('sane-frontends', ''),
'reportlab': ('python-reportlab', ''), 
'ppdev': ('', 'modprobe ppdev && cp -f /etc/modules /etc/modules.hplip && echo ppdev | sudo tee -a /etc/modules'),
'pyqt': ('pyqt', ''),
'python23': ('python', ''),
'libnetsnmp-devel': ('libnet-snmp5-devel', ''),
'libcrypto': ('openssl', ''),
'libjpeg': ('libjpeg62-devel', ''),
})
################### ASIANUX (18) ###################

################### PCBSD (19) ###################

################### SUN WAH RAYS LX (20) ###################

################### MIRACLE (21) ###################


