#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) Copyright 2015 HP Development Company, L.P.
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
# Author: Amarnath Chitumalla, Sanjay Kumar
#
#Global imports
import os
import stat
import datetime

#Local imports
from base.codes import *
from base.strings import *
from base import utils
from base import os_utils
from base.g import *
from subprocess import Popen, PIPE


class DigiSign_Verification(object):
    def __init__(self):
        pass

    def validate(self):
        pass


class GPG_Verification(DigiSign_Verification):
    def __init__(self, pgp_site = 'pgp.mit.edu', key = 0x4ABA2F66DBD5A95894910E0673D770CDA59047B9):
        self.__pgp_site = pgp_site
        self.__key = key
        self.__gpg = utils.which('gpg',True)

        sts, self.__hplipdir = os_utils.getHPLIPDir()
        self.__gpg_dir = os.path.join(self.__hplipdir, ".gnupg")

        #Make sure gpg directory is present. GPG keys will be retrieved here from the key server
        

        if not os.path.exists(self.__gpg_dir):
            try:
                os.mkdir(self.__gpg_dir, 0o755)
            except OSError:
                log.error("Failed to create %s" % self.__gpg_dir)
        self.__change_owner()
    def __change_owner(self, Recursive = False):
        try:
            os.umask(0)
            s = os.stat(self.__hplipdir)
            os_utils.changeOwner(self.__gpg_dir, s[stat.ST_UID], s[stat.ST_GID], Recursive)

        except OSError:
            log.error("Failed to Change ownership of %s" %self.__gpg_dir)

    def __gpg_check(self, hplip_package, hplip_digsig):

        cmd = '%s --homedir %s -no-permission-warning --verify %s %s' % (self.__gpg, self.__gpg_dir, hplip_digsig, hplip_package)

        log.debug("Verifying file %s : cmd = [%s]" % (hplip_package,cmd))

        status, output = utils.run(cmd)

        log.debug("%s status: %d  output:%s" % (self.__gpg, status,output))

        return status


    def __acquire_gpg_key(self):

        key_AC69536A2CF3A243 = """
-----BEGIN PGP PUBLIC KEY BLOCK-----

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
6saq
=EWRb
-----END PGP PUBLIC KEY BLOCK-----
"""

        import tempfile
        tf = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        tf.write(key_AC69536A2CF3A243)
        tf.close()

        cmd = '%s --homedir %s --import %s' \
              % (self.__gpg, self.__gpg_dir, tf.name)

        log.info("Importing digital keys: %s" % cmd)
        status, output = utils.run(cmd)
        log.debug(output)

        self.__change_owner(True)

        return status 


    def validate(self, hplip_package, hplip_digsig):      

        log.debug("Validating %s with %s signature file" %(hplip_package, hplip_digsig))
        if not self.__gpg:
            return ERROR_GPG_CMD_NOT_FOUND, queryString(ERROR_GPG_CMD_NOT_FOUND)

        if not os.path.exists(hplip_package):
            return ERROR_FILE_NOT_FOUND, queryString(ERROR_FILE_NOT_FOUND, 0, hplip_package)

        if not os.path.exists(hplip_digsig):
            return ERROR_DIGITAL_SIGN_NOT_FOUND, queryString(ERROR_DIGITAL_SIGN_NOT_FOUND, 0, hplip_digsig)

        status = self.__acquire_gpg_key()
        if status != 0:
            return ERROR_UNABLE_TO_RECV_KEYS, queryString(ERROR_UNABLE_TO_RECV_KEYS)

        status = self.__gpg_check(hplip_package, hplip_digsig)
        if status != 0:
            return ERROR_DIGITAL_SIGN_BAD, queryString(ERROR_DIGITAL_SIGN_BAD, 0, hplip_package)
        else:
            return ERROR_SUCCESS, ""

