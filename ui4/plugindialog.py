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
from plugindialog_base import Ui_Dialog


PAGE_SELECT_FAX = 0
PAGE_COVERPAGE = 1
PAGE_FILES = 2
PAGE_RECIPIENTS = 3
PAGE_SEND_FAX = 4
PAGE_MAX = 4



class PluginDialog(QDialog, Ui_Dialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.initUi()

        #QTimer.singleShot(0, self.updateXXXPage)


    def initUi(self):
        # connect signals/slots
        self.connect(self.CancelButton, SIGNAL("clicked()"), self.CancelButton_clicked)
        self.connect(self.BackButton, SIGNAL("clicked()"), self.BackButton_clicked)
        self.connect(self.NextButton, SIGNAL("clicked()"), self.NextButton_clicked)

        # Application icon
        self.setWindowIcon(QIcon(load_pixmap('prog', '48x48')))

        #self.initSelectFaxPage()
        #self.initCoverpagePage()
        #self.initFilesPage()
        #self.initRecipientsPage()
        #self.initSendFaxPage()

        self.StackedWidget.setCurrentIndex(0)


    #
    # Misc    
    #

    def CancelButton_clicked(self):
        self.close()

    def BackButton_clicked(self):
        p = self.StackedWidget.currentIndex()
        if p == PAGE_SELECT_FAX:
            log.error("Invalid!")

        elif p == PAGE_COVERPAGE:
            log.error("Invalid!")

        elif p == PAGE_FILES:
            self.StackedWidget.setCurrentIndex(PAGE_COVERPAGE)
            self.updateCoverpagePage()

        elif p == PAGE_RECIPIENTS:
            self.StackedWidget.setCurrentIndex(PAGE_FILES)
            self.updateFilesPage()

        elif p == PAGE_SEND_FAX:
            self.StackedWidget.setCurrentIndex(PAGE_RECIPIENTS)
            self.updateRecipientsPage()


    def NextButton_clicked(self):
        p = self.StackedWidget.currentIndex()
        if p == PAGE_SELECT_FAX:
            self.StackedWidget.setCurrentIndex(PAGE_COVERPAGE)
            self.updateCoverpagePage()

        elif p == PAGE_COVERPAGE:
            self.StackedWidget.setCurrentIndex(PAGE_FILES)
            self.updateFilesPage()

        elif p == PAGE_FILES:
            self.StackedWidget.setCurrentIndex(PAGE_RECIPIENTS)
            self.updateRecipientsPage()

        elif p == PAGE_RECIPIENTS:
            self.StackedWidget.setCurrentIndex(PAGE_SEND_FAX)
            self.updateSendFaxPage()

        elif p == PAGE_SEND_FAX:
            self.executeSendFax()


    def updateStepText(self, p):
        self.StepText.setText(self.__tr("Step %1 of %2").arg(p+1).arg(PAGE_MAX+1))


    def restoreNextButton(self):
        self.NextButton.setText(self.__tr("Next >"))


    def __tr(self,s,c = None):
        return qApp.translate("PluginDialog",s,c)


