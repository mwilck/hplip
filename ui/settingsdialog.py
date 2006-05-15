# -*- coding: utf-8 -*-
#
# (c) Copyright 2001-2006 Hewlett-Packard Development Company, L.P.
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

from base.g import *
from base.codes import *
from base import utils, service
from qt import *
from settingsdialog_base import SettingsDialog_base

class SettingsDialog(SettingsDialog_base):
    def __init__(self, hpssd_sock, parent = None,name = None,modal = 0,fl = 0):
        SettingsDialog_base.__init__(self,parent,name,modal,fl)
        self.DefaultsButton.setEnabled(False)
        self.hpssd_sock = hpssd_sock
        #print repr(user_cfg.refresh.enable)
        #self.auto_refresh = utils.to_bool(user_cfg.refresh.enable)
        #self.autoRefreshCheckBox.setChecked(self.auto_refresh)
        
        self.sendmail = utils.which('sendmail')
        if not self.sendmail:
            self.EmailTestButton.setEnabled(False)

    def PrintCmdChangeButton_clicked(self):
        pass

    def ScanCmdChangeButton_clicked(self):
        pass

    def AccessPCardCmdChangeButton_clicked(self):
        pass

    def SendFaxCmdChangeButton_clicked(self):
        pass

    def MakeCopiesCmdChangeButton_clicked(self):
        pass

    def DefaultsButton_clicked(self):
        cmd_print, cmd_scan, cmd_pcard, \
        cmd_copy, cmd_fax, cmd_fab = utils.deviceDefaultFunctions()
        
        self.PrintCommand.setText(cmd_print)
        self.ScanCommand.setText(cmd_scan)
        self.AccessPCardCommand.setText(cmd_pcard)
        self.SendFaxCommand.setText(cmd_fax)
        self.MakeCopiesCommand.setText(cmd_copy)

    def TabWidget_currentChanged(self,a0):
        name = str(a0.name())

        if name == 'FunctionCommands':
            self.DefaultsButton.setEnabled(True)
        else:
            self.DefaultsButton.setEnabled(False)

    def EmailTestButton_clicked(self): 
        email_to_addresses = str(self.EmailAddress.text())
        email_from_address = str(self.senderLineEdit.text())
        
        if not email_to_addresses or not email_from_address:
            QMessageBox.warning(self,
                                 self.caption(),
                                 self.__tr("<b>One or more email addresses are missing.</b><p>Please enter this information and try again."),
                                  QMessageBox.Ok,
                                  QMessageBox.NoButton,
                                  QMessageBox.NoButton)
            return
        
        user_cfg.alerts.email_to_addresses = email_to_addresses
        user_cfg.alerts.email_from_address = email_from_address
        user_cfg.alerts.email_alerts = True
        
        service.setAlerts(self.hpssd_sock, 
                          True,
                          email_from_address,
                          email_to_addresses)

        result_code = service.testEmail(self.hpssd_sock, prop.username)
        log.debug(result_code)
        
        QMessageBox.information(self,
                     self.caption(),
                     self.__tr("<p><b>Please check your email for a test message.</b><p>If the message doesn't arrive, please check your settings and try again."),
                      QMessageBox.Ok,
                      QMessageBox.NoButton,
                      QMessageBox.NoButton)

        
    def autoRefreshCheckBox_clicked(self):
        pass
        
    def CleaningLevel_clicked(self,a0):
        pass
        
    def refreshScopeButtonGroup_clicked(self,a0):
        self.auto_refresh_type = int(a0)
        
        
    def __tr(self,s,c = None):
        return qApp.translate("SettingsDialog",s,c)

        
