# -*- coding: utf-8 -*-
#
# (c) Copyright 2001-2008 Hewlett-Packard Development Company, L.P.
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

# Std Lib
import os.path
import re

# Local
from base.g import *
from base.codes import *
from base import utils

# Qt
from PyQt4.QtCore import *
from PyQt4.QtGui import *

pat_html_remove = re.compile("(?is)<.*?>", re.I)

# TODO: Cache pixmaps
def load_pixmap(name, subdir=None, resize_to=None):
    name = ''.join([os.path.splitext(name)[0], '.png'])

    if subdir is None:
        dir = prop.image_dir
    else:
        dir = os.path.join(prop.image_dir, subdir)

    log.debug("Loading pixmap '%s' from %s" % (name, dir))

    f = os.path.join(dir, name)
    if os.path.exists(f):
        if resize_to is not None:
            img = QImage(f)
            x, y = resize_to
            return QPixmap.fromImage(img.scaled(x, y, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        else:
            return QPixmap(f)

    for w in utils.walkFiles(dir, recurse=True, abs_paths=True, return_folders=False, pattern=name):
        if resize_to is not None:
            img = QImage(w)
            x, y = resize_to
            return QPixmap.fromImage(img.scaled(x, y, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        else:
            return QPixmap(w)

    log.error("Pixmap '%s' not found!" % name)
    return QPixmap()

    
class UserSettings(QSettings):
    def __init__(self):
        QSettings.__init__(self, os.path.join(prop.user_dir,  'hplip.conf'),  QSettings.IniFormat)
        #self.hide_tray_when_inactive = False
        self.systray_visible = SYSTRAY_VISIBLE_SHOW_ALWAYS
        self.last_used_device_uri = ''
        self.last_used_printer = ''
        self.last_used_working_dir = os.path.expanduser('~')
        self.version = ''
        self.date_time = ''
        self.auto_refresh = False
        self.auto_refresh_rate = 30
        self.auto_refresh_type = 1
        self.loadDefaults()
    
    
    def __setup(self,  cmds):
        for c in cmds:
            basename = c.split()[0]
            path = utils.which(basename)
            if path:
                return ' '.join([os.path.join(path, basename), ' '.join(c.split()[1:])])
        
        return ''
    
    def loadDefaults(self):
        #self.cmd_print = self.__setup(['hp-print -p%PRINTER',  
        #                               'kprinter -P%PRINTER% --system cups',
        #                               'gtklp -P%PRINTER%',
        #                               'xpp -P%PRINTER%'])
                                       
        self.cmd_scan = self.__setup(['xsane -V %SANE_URI%', 'kooka', 'xscanimage']) 
        #self.cmd_pcard = self.__setup(['hp-unload -d%DEVICE_URI%'])
        #self.cmd_fax = self.__setup(['hp-sendfax -p%PRINTER%'])
        #self.cmd_copy = self.__setup(['hp-makecopies -d%DEVICE_URI%'])
        #self.cmd_faxsetup = self.__setup(['hp-faxsetup -d$FAX_URI%'])
        self.cmd_fab = self.__setup(['hp-fab'])
        #self.cmd_align = self.__setup(['hp-align -d%DEVICE_URI%'])
        #self.cmd_pqdiag = self.__setup(['hp-pqdiag -d%DEVICE_URI%'])
        #self.cmd_colorcal = self.__setup(['hp-colorcal -d%DEVICE_URI%'])
        #self.cmd_testpage = self.__setup(['hp-testpage -p%PRINTER%'])
        #self.cmd_devicesetup = self.__setup(['hp-devicesetup -d%DEVICE_URI%'])
        #self.cmd_clean = self.__setup(['hp-clean -d%DEVICE_URI%'])
        #self.cmd_linefeedcal = self.__setup(['hp-linefeedcal -d%DEVICE_URI%'])
        #self.cmd_firmware = self.__setup(['hp-firmware -d%DEVICE_URI%'])
        #self.cmd_plugin = self.__setup(['hp-plugin -d%DEVICE_URI%'])
        #self.cmd_info = self.__setup(['hp-info -d%DEVICE_URI%'])
        
        
    def load(self):
        log.debug("Loading user settings...")
        
        self.beginGroup("settings")
        #self.hide_tray_when_inactive = bool(self.value("hide_tray_when_inactive").toBool()) or self.hide_tray_when_inactive
        i, ok = self.value("systray_visible").toInt()
        if ok:
            self.systray_visible = i
        
        self.endGroup()
        
        self.beginGroup("last_used")
        self.last_used_device_uri = unicode(self.value("device_uri").toString()) or self.last_used_device_uri
        self.last_used_printer = unicode(self.value("printer").toString()) or self.last_used_printer
        self.last_used_working_dir = unicode(self.value("working_dir").toString()) or self.last_used_working_dir
        self.endGroup()
        
        self.beginGroup("commands")
        #self.cmd_print = unicode(self.value("prnt").toString()) or self.cmd_print
        #self.cmd_copy = unicode(self.value("cpy").toString()) or self.cmd_copy
        #self.cmd_fax = unicode(self.value("fax").toString()) or self.cmd_fax
        self.cmd_scan = unicode(self.value("scan").toString()) or self.cmd_scan
        #self.cmd_pcard = unicode(self.value("pcard").toString()) or self.cmd_pcard
        #self.cmd_fab = unicode(self.value("fab").toString()) or self.cmd_fab
        self.endGroup()
        
        self.beginGroup("refresh")
        self.auto_refresh_rate = int(self.value("rate").toString() or self.auto_refresh_rate) 
        self.auto_refresh = bool(self.value("enable").toBool())
        self.auto_refresh_type = int(self.value("type").toString() or self.auto_refresh_type)
        self.endGroup()
        
        self.beginGroup("installation")
        self.version = unicode(self.value("version").toString())
        self.date_time = unicode(self.value("date_time").toString())
        self.endGroup()
        
        
    def save(self):
        log.debug("Saving user settings...")
        
        self.beginGroup("settings")
        #self.setValue("hide_tray_when_inactive",  QVariant(self.hide_tray_when_inactive))
        i = QVariant(self.systray_visible)
        #print i.toInt()
        self.setValue("systray_visible", QVariant(self.systray_visible))
        self.endGroup()
        
        self.beginGroup("last_used")
        self.setValue("device_uri",  QVariant(self.last_used_device_uri))
        self.setValue("printer", QVariant(self.last_used_printer))
        self.setValue("working_dir", QVariant(self.last_used_working_dir))
        self.endGroup()
        
        self.beginGroup("commands")
        #self.setValue("prnt",  QVariant(self.cmd_print))
        #self.setValue("cpy",  QVariant(self.cmd_copy))
        #self.setValue("fax",  QVariant(self.cmd_fax))
        self.setValue("scan",  QVariant(self.cmd_scan))
        #self.setValue("pcard",  QVariant(self.cmd_pcard))
        #self.setValue("fab",  QVariant(self.cmd_fab))
        self.endGroup()
        
        self.beginGroup("refresh")
        self.setValue("rate", QVariant(self.auto_refresh_rate))
        self.setValue("enable", QVariant(self.auto_refresh))
        self.setValue("type", QVariant(self.auto_refresh_type))
        self.endGroup()
        
        
    def debug(self):
        #log.debug("Print command: %s" % self.cmd_print)
        #log.debug("PCard command: %s" % self.cmd_pcard)
        #log.debug("Fax command: %s" % self.cmd_fax)
        log.debug("FAB command: %s" % self.cmd_fab)
        #log.debug("Copy command: %s " % self.cmd_copy)
        log.debug("Scan command: %s" % self.cmd_scan)
        log.debug("Auto refresh: %s" % self.auto_refresh)
        log.debug("Auto refresh rate: %s" % self.auto_refresh_rate)
        log.debug("Auto refresh type: %s" % self.auto_refresh_type)       
        #log.debug("Hide tray when inactive: %s" % self.hide_tray_when_inactive)
        log.debug("Systray visible: %d" % self.systray_visible)
        log.debug("Last used device URI: %s" % self.last_used_device_uri)
        log.debug("Last used printer: %s" % self.last_used_printer)
        log.debug("Last used working dir: %s" % self.last_used_working_dir)
    
    
def su_sudo():
    su_sudo_str = None

    if utils.which('kdesu'):
        su_sudo_str = 'kdesu -- %s'

    elif utils.which('gnomesu'):
        su_sudo_str = 'gnomesu -c "%s"'
    
    elif utils.which('gksu'):
        su_sudo_str = 'gksu "%s"'

    return su_sudo_str
    
    
def FailureUI(parent, error_text, title_text=None):
    log.error(pat_html_remove.sub(' ', unicode(error_text)))
    
    if title_text is None:
        title_text = parent.windowTitle()
        
    QMessageBox.critical(parent,
        title_text, 
        error_text,
        QMessageBox.Ok,
        QMessageBox.NoButton,
        QMessageBox.NoButton)
    


def WarningUI(parent,  warn_text, title_text=None):
    log.warn(pat_html_remove.sub(' ', unicode(warn_text)))
    
    if title_text is None:
        title_text = parent.windowTitle()

    QMessageBox.warning(parent,
        title_text, 
        warn_text,
        QMessageBox.Ok,
        QMessageBox.NoButton,
        QMessageBox.NoButton)
