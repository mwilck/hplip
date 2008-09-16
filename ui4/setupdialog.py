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
# Authors: Don Welch
#


# Local
from base.g import *
from base import device, utils
from prnt import cups
from base.codes import *
from ui_utils import *

# Qt
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Ui
from setupdialog_base import Ui_Dialog


class SetupDialog(QDialog, Ui_Dialog):
    def __init__(self, parent, param, jd_port, username):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        #self.setWindowTitle(self.__tr("HP Device Manager - Fax Device Setup"))

        # connect signals/slots
        #self.connect(self.CancelButton, SIGNAL("clicked()"), self.CancelButton_clicked)
        #self.connect(self.ApplyButton, SIGNAL("clicked()"), self.ApplyButton_clicked)
        #self.connect(self.NextButton, SIGNAL("clicked()"), self.NextButton_clicked)

        #self.initFilePage()
        #self.initOptionsPage()
        
        self.initUi()

        #self.StackedWidget.setCurrentIndex(0)
        QTimer.singleShot(0, self.updateUi)

    def initUi(self):
        #self.FaxComboBox.setType(DEVICEURICOMBOBOX_TYPE_FAX_ONLY)
        # Application icon
        self.setWindowIcon(QIcon(load_pixmap('prog', '48x48')))
    
    def updateUi(self):
        pass
        #self.FaxComboBox.updateUi()
    
    def CancelButton_clicked(self):
        self.close()
        
    def ApplyButton_clicked(self):
        pass

    #
    # Misc
    # 

    def __tr(self,s,c = None):
        return qApp.translate("SetupDialog",s,c)


