# -*- coding: utf-8 -*-
#
# (c) Copyright 2001-2007 Hewlett-Packard Development Company, L.P.
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

# Local
from base.g import *
from base import utils

# Qt
from qt import *
from scrollview import ScrollView

# Std Lib
import os.path, os

class ScrollFunctionsView(ScrollView):
    def __init__(self, cmd_print, cmd_scan, cmd_pcard, cmd_fax, cmd_copy, parent = None,name = None,fl = 0):
        ScrollView.__init__(self,parent,name,fl)
        self.cmd_print = cmd_print
        self.cmd_scan = cmd_scan
        self.cmd_copy = cmd_copy
        self.cmd_pcard = cmd_pcard
        self.cmd_fax = cmd_fax

        self.ScanPixmap = QPixmap(os.path.join(prop.image_dir, "scan_icon.png"))
        self.PrintPixmap = QPixmap(os.path.join(prop.image_dir, "print_icon.png"))
        self.SendFaxPixmap =QPixmap(os.path.join(prop.image_dir, "fax_icon.png"))
        self.PhotoCardPixmap = QPixmap(os.path.join(prop.image_dir, "pcard_icon.png"))
        self.MakeCopiesPixmap = QPixmap(os.path.join(prop.image_dir, "makecopies_icon.png"))

    def setCmds(self, cmd_print, cmd_scan, cmd_pcard, cmd_fax, cmd_copy):
        self.cmd_print = cmd_print
        self.cmd_scan = cmd_scan
        self.cmd_copy = cmd_copy
        self.cmd_pcard = cmd_pcard
        self.cmd_fax = cmd_fax

    def fillControls(self):
        ScrollView.fillControls(self)
        
        self.addItem(self.__tr("<b>Print</b>"), self.__tr("Print a document using %1 (selected file types only).").arg('hp-print'), 
            self.__tr("Print..."), self.PrintPixmap, self.PrintButton_clicked)

        if self.cur_device.scan_type:
            self.addItem(self.__tr("<b>Scan</b>"), self.__tr("Scan a document or image using %1.").arg('xsane'),
                self.__tr("Scan..."), self.ScanPixmap, self.ScanButton_clicked)

        if self.cur_device.fax_type:
            self.addItem(self.__tr("<b>Send PC Fax</b>"), self.__tr("Send a fax from the PC using %1.").arg('hp-sendfax'),
                self.__tr("Send PC Fax..."), self.SendFaxPixmap, self.SendFaxButton_clicked)

        if self.cur_device.copy_type:
            self.addItem(self.__tr("<b>Make Copies</b>"), self.__tr("Initiate device copies from the PC using %1.").arg('hp-makecopies'),
                self.__tr("Make Copies..."), self.MakeCopiesPixmap, self.MakeCopiesButton_clicked)

        if self.cur_device.pcard_type:
            self.addItem(self.__tr("<b>Unload Photo Card</b>"), self.__tr("Copy/move image files from the device to the PC using %1.").arg('hp-unload'),
                self.__tr("Unload Photo Card..."), self.PhotoCardPixmap, self.PCardButton_clicked)


    def PrintButton_clicked(self):
        self.RunCommand(self.cmd_print)

    def ScanButton_clicked(self):
        self.RunCommand(self.cmd_scan)

    def PCardButton_clicked(self):
        if self.cur_device.pcard_type == PCARD_TYPE_MLC:
            self.RunCommand(self.cmd_pcard)

        elif self.cur_device.pcard_type == PCARD_TYPE_USB_MASS_STORAGE:
            self.FailureUI(self.__tr("<p><b>Photocards on your printer are only available by mounting them as drives using USB mass storage.</b><p>Please refer to your distribution's documentation for setup and usage instructions."))

    def SendFaxButton_clicked(self):
        self.RunCommand(self.cmd_fax)

    def MakeCopiesButton_clicked(self):
        self.RunCommand(self.cmd_copy)

    def RunCommand(self, cmd, macro_char='%'):
        QApplication.setOverrideCursor(QApplication.waitCursor)

        try:
            if len(cmd) == 0:
                self.FailureUI(self.__tr("<p><b>Unable to run command. No command specified.</b><p>Use <pre>Configure...</pre> to specify a command to run."))
                log.error("No command specified. Use settings to configure commands.")
            else:
                log.debug(utils.bold("Run: %s %s (%s) %s" % ("*"*20, cmd, self.cur_device.device_uri, "*"*20)))
                log.debug(cmd)
                cmd = ''.join([self.cur_device.device_vars.get(x, x) \
                                 for x in cmd.split(macro_char)])
                log.debug(cmd)

                path = cmd.split()[0]
                args = cmd.split()

                log.debug(path)
                log.debug(args)

                self.CleanupChildren()
                os.spawnvp(os.P_NOWAIT, path, args)

        finally:
            QApplication.restoreOverrideCursor()

    def CleanupChildren(self):
        log.debug("Cleaning up child processes.")
        try:
            os.waitpid(-1, os.WNOHANG)
        except OSError:
            pass

    def addItem(self, title, text, button_text, pixmap, button_func):
        widget = self.getWidget()
        vp = self.viewport()

        layout1 = QGridLayout(widget, 1, 1, 10, 5,"layout1")

        pushButton = QPushButton(widget, "pushButton")
        pushButton.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed, 0, 0,
            pushButton.sizePolicy().hasHeightForWidth()))

        layout1.addWidget(pushButton, 1, 3)

        icon = QLabel(widget, "icon")
        icon.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed, 0, 0,
            icon.sizePolicy().hasHeightForWidth()))

        icon.setMinimumSize(QSize(32, 32))
        icon.setMaximumSize(QSize(32, 32))
        icon.setScaledContents(1)
        layout1.addWidget(icon, 1, 0)

        textLabel = QLabel(widget, "textLabel")
        #textLabel.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter)
        textLabel.setAlignment(QLabel.WordBreak)
        textLabel.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred, 0, 0,
            textLabel.sizePolicy().hasHeightForWidth()))        

        layout1.addWidget(textLabel, 1, 1)

        titleLabel = QLabel(widget, "titleLabel")
        layout1.addMultiCellWidget(titleLabel, 0, 0, 0, 3)

        spacer1 = QSpacerItem(141, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout1.addItem(spacer1, 1, 2)

        line1 = QFrame(widget, "line1")
        line1.setFrameShape(QFrame.HLine)
        layout1.addMultiCellWidget(line1, 2, 2, 0, 3)

        titleLabel.setText(title)
        textLabel.setText(text)
        pushButton.setText(button_text)
        icon.setPixmap(pixmap)

        self.connect(pushButton, SIGNAL("clicked()"), button_func)

        self.addControl(widget, str(title))


    def __tr(self,s,c = None):
        return qApp.translate("DevMgr4",s,c)
