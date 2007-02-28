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
from base import utils, pml, maint
from prnt import cups
from base.codes import *

# Qt
from qt import *
from scrollview import ScrollView

# Std Lib
import sys, os.path, os

# Alignment and ColorCal forms
from alignform import AlignForm
from aligntype6form1 import AlignType6Form1
from aligntype6form2 import AlignType6Form2
from paperedgealignform import PaperEdgeAlignForm
from colorcalform import ColorCalForm # Type 1 color cal
from coloradjform import ColorAdjForm  # Type 5 and 6 color adj
from colorcalform2 import ColorCalForm2 # Type 2 color cal
from colorcal4form import ColorCal4Form # Type 4 color cal
from align10form import Align10Form # Type 10 and 11 alignment

# Misc forms
from loadpaperform import LoadPaperForm
from settingsdialog import SettingsDialog
from aboutdlg import AboutDlg
from cleaningform import CleaningForm
from cleaningform2 import CleaningForm2
from waitform import WaitForm
from faxsettingsform import FaxSettingsForm
from informationform import InformationForm



class ScrollToolView(ScrollView):
    def __init__(self,parent = None,name = None,fl = 0):
        ScrollView.__init__(self,parent,name,fl)
        
        cmd_print, cmd_scan, cmd_pcard, \
            cmd_copy, cmd_fax, cmd_fab = utils.deviceDefaultFunctions()

        self.cmd_print = user_cfg.commands.prnt or cmd_print
        self.cmd_scan = user_cfg.commands.scan or cmd_scan
        self.cmd_pcard = user_cfg.commands.pcard or cmd_pcard
        self.cmd_copy = user_cfg.commands.cpy or cmd_copy
        self.cmd_fax = user_cfg.commands.fax or cmd_fax
        self.cmd_fab = user_cfg.commands.fab or cmd_fab
        
        
    def fillControls(self):
        ScrollView.fillControls(self)
        
        if self.cur_device is not None and \
            self.cur_device.supported and \
            self.cur_device.device_state != DEVICE_STATE_NOT_FOUND:
    
            if self.cur_device.device_settings_ui is not None:
                self.addItem( "device_settings", self.__tr("<b>Device Settings</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_settings.png')), 
                    self.__tr("Your device has special device settings. You may alter these settings here."), 
                    self.__tr("Device Settings..."), 
                    self.deviceSettingsButton_clicked)
        
            if self.cur_device.fax_type:
                self.addItem( "fax_settings", self.__tr("<b>Fax Setup</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_fax.png')), 
                    self.__tr("Fax support must be setup before you can send faxes."), 
                    self.__tr("Setup Fax..."), 
                    self.faxSettingsButton_clicked)
        
                self.addItem( "fax_address_book", self.__tr("<b>Fax Address Book</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_fax.png')), 
                    self.__tr("Setup fax phone numbers to use when sending faxes from the PC."), 
                    self.__tr("Fax Address Book..."), 
                    self.faxAddressBookButton_clicked)
        
        
            self.addItem( "testpage", self.__tr("<b>Print Test Page</b>"), 
                QPixmap(os.path.join(prop.image_dir, 'icon_testpage.png')), 
                self.__tr("Print a test page to test the setup of your printer."), 
                self.__tr("Print Test Page..."), 
                self.PrintTestPageButton_clicked)
        
        
            self.addItem( "info", self.__tr("<b>View Device Information</b>"), 
                QPixmap(os.path.join(prop.image_dir, 'icon_info.png')), 
                self.__tr("This information is primarily useful for debugging and troubleshooting."), 
                self.__tr("View Information..."), 
                self.viewInformation) 
        
            if self.cur_device.pq_diag_type:
                self.addItem( "pqdiag", self.__tr("<b>Print Quality Diagnostics</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_pq_diag.png')),
                    self.__tr("Your printer can print a test page to help diagnose print quality problems."), 
                    self.__tr("Print Diagnostic Page..."), 
                    self.pqDiag)
        
            if self.cur_device.fw_download:
                self.addItem( "fwdownload", self.__tr("<b>Download Firmware</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'download.png')),
                    self.__tr("Download firmware to your printer (required on some devices after each power-up)."), 
                    self.__tr("Download Firmware..."), 
                    self.downloadFirmware)
        
            if self.cur_device.clean_type:
                self.addItem( "clean", self.__tr("<b>Clean Cartridges</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_clean.png')), 
                    self.__tr("You only need to perform this action if you are having problems with poor printout quality due to clogged ink nozzles."), 
                    self.__tr("Clean Cartridges..."), 
                    self.CleanPensButton_clicked)
        
            if self.cur_device.align_type:
                self.addItem( "align", self.__tr("<b>Align Cartridges</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_align.png')), 
                    self.__tr("This will improve the quality of output when a new cartridge is installed."), 
                    self.__tr("Align Cartridges..."), 
                    self.AlignPensButton_clicked)
        
            if self.cur_device.color_cal_type:
                self.addItem( "colorcal", self.__tr("<b>Perform Color Calibration</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_colorcal.png')), 
                    self.__tr("Use this procedure to optimimize your printer's color output."), 
                    self.__tr("Color Calibration..."), 
                    self.ColorCalibrationButton_clicked)
        
            if self.cur_device.linefeed_cal_type:
                self.addItem( "linefeed", self.__tr("<b>Perform Line Feed Calibration</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_linefeed_cal.png')),
                    self.__tr("Use line feed calibration to optimize print quality (to remove gaps in the printed output)."), 
                    self.__tr("Line Feed Calibration..."), 
                    self.linefeedCalibration) 
        
            if self.cur_device.embedded_server_type and self.cur_device.bus == 'net':
                self.addItem( "ews", self.__tr("<b>Access Embedded Web Page</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_ews.png')), 
                    self.__tr("You can use your printer's embedded web server to configure, maintain, and monitor the device from a web browser."),
                    self.__tr("Open in Browser..."), 
                    self.OpenEmbeddedBrowserButton_clicked)
        
        self.addItem("support",  self.__tr("<b>View Documentation</b>"), 
            QPixmap(os.path.join(prop.image_dir, 'icon_support2.png')), 
            self.__tr("View documentation installed on your system."), 
            self.__tr("View Documentation..."), 
            self.viewSupport) 
            

    def addItem(self, name, title, pix, text, button_text, button_func):
        widget = self.getWidget()
        layout1 = QGridLayout(widget, 1, 1, 10, 5, "layout1")

        pushButton1 = QPushButton(widget, "pushButton1")
        layout1.addWidget(pushButton1, 1, 3)

        icon = QLabel(widget, "icon")
        icon.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed, 0, 0,
            icon.sizePolicy().hasHeightForWidth()))

        icon.setScaledContents(1)
        icon.setPixmap(pix)
        layout1.addWidget(icon, 1, 0)

        spacer1 = QSpacerItem(20, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout1.addItem(spacer1, 1, 2)

        titleLabel = QLabel(widget, "titleLabel")
        layout1.addMultiCellWidget(titleLabel, 0, 0, 0, 3)

        textLabel = QLabel(widget, "textLabel")
        textLabel.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred, 0, 0,
            textLabel.sizePolicy().hasHeightForWidth()))

        textLabel.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter)

        layout1.addWidget(textLabel, 1, 1)

        line1 = QFrame(widget,"line1")
        line1.setFrameShape(QFrame.HLine)

        layout1.addMultiCellWidget(line1, 2, 2, 0, 3)

        self.connect(pushButton1,SIGNAL("clicked()"), button_func)

        titleLabel.setText(title)
        textLabel.setText(text)
        pushButton1.setText(button_text)

        self.addControl(widget, name)
        
        
    def viewInformation(self):
        InformationForm(self.cur_device, self).exec_loop()

    def viewSupport(self):
        f = "file://%s" % os.path.join(sys_cfg.dirs.doc, 'index.html')
        log.debug(f)
        utils.openURL(f)
        
    def pqDiag(self):
        d = self.cur_device
        pq_diag = d.pq_diag_type

        try:
            QApplication.setOverrideCursor(QApplication.waitCursor)
            d.open()

            if d.isIdleAndNoError():
                QApplication.restoreOverrideCursor()

                if pq_diag == 1:
                    maint.printQualityDiagType1(d, self.LoadPaperUI)
                    
                elif pq_diag == 2:
                    maint.printQualityDiagType2(d, self.LoadPaperUI)

            else:
                self.CheckDeviceUI()

        finally:
            d.close()
            QApplication.restoreOverrideCursor()


    def linefeedCalibration(self):
        d = self.cur_device
        linefeed_type = d.linefeed_cal_type

        try:
            QApplication.setOverrideCursor(QApplication.waitCursor)
            d.open()

            if d.isIdleAndNoError():
                QApplication.restoreOverrideCursor()

                if linefeed_type == 1:
                    maint.linefeedCalType1(d, self.LoadPaperUI)
                    
                elif linefeed_type == 2:
                    maint.linefeedCalType2(d, self.LoadPaperUI)

            else:
                self.CheckDeviceUI()

        finally:
            d.close()
            QApplication.restoreOverrideCursor()

    def downloadFirmware(self):
        d = self.cur_device

        try:
            QApplication.setOverrideCursor(QApplication.waitCursor)
            d.open()

            if d.isIdleAndNoError():
                d.downloadFirmware()
            else:
                self.FailureUI(self.__tr("<b>An error occured downloading firmware file.</b><p>Please check your printer and try again."))

        finally:
            d.close()
            QApplication.restoreOverrideCursor()
            
            
    def CheckDeviceUI(self):
        self.FailureUI(self.__tr("<b>Device is busy or in an error state.</b><p>Please check device and try again."))

    def LoadPaperUI(self):
        if LoadPaperForm(self).exec_loop() == QDialog.Accepted:
            return True
        return False

    def AlignmentNumberUI(self, letter, hortvert, colors, line_count, choice_count):
        dlg = AlignForm(self, letter, hortvert, colors, line_count, choice_count)
        if dlg.exec_loop() == QDialog.Accepted:
            return True, dlg.value
        else:
            return False, 0

    def PaperEdgeUI(self, maximum):
        dlg = PaperEdgeAlignForm(self)
        if dlg.exec_loop() == QDialog.Accepted:
            return True, dlg.value
        else:
            return False, 0

    def BothPensRequiredUI(self):
        self.WarningUI(self.__tr("<p><b>Both cartridges are required for alignment.</b><p>Please install both cartridges and try again."))

    def InvalidPenUI(self):
        self.WarningUI(self.__tr("<p><b>One or more cartiridges are missing from the printer.</b><p>Please install cartridge(s) and try again."))

    def PhotoPenRequiredUI(self):
        self.WarningUI(self.__tr("<p><b>Both the photo and color cartridges must be inserted into the printer to perform color calibration.</b><p>If you are planning on printing with the photo cartridge, please insert it and try again."))

    def PhotoPenRequiredUI2(self):
        self.WarningUI(self.__tr("<p><b>Both the photo (regular photo or photo blue) and color cartridges must be inserted into the printer to perform color calibration.</b><p>If you are planning on printing with the photo or photo blue cartridge, please insert it and try again."))

    def NotPhotoOnlyRequired(self): # Type 11
        self.WarningUI(self.__tr("<p><b>Cannot align with only the photo cartridge installed.</b><p>Please install other cartridges and try again."))

    def AioUI1(self):
        dlg = AlignType6Form1(self)
        return dlg.exec_loop() == QDialog.Accepted


    def AioUI2(self):
        AlignType6Form2(self).exec_loop()

    def Align10and11UI(self, pattern, align_type):
        dlg = Align10Form(pattern, align_type, self)
        dlg.exec_loop()
        return dlg.getValues()

    def AlignPensButton_clicked(self):
        d = self.cur_device
        align_type = d.align_type

        log.debug(utils.bold("Align: %s %s (type=%d) %s" % ("*"*20, self.cur_device.device_uri, align_type, "*"*20)))

        try:
            QApplication.setOverrideCursor(QApplication.waitCursor)
            d.open()

            if d.isIdleAndNoError():
                QApplication.restoreOverrideCursor()

                if align_type == ALIGN_TYPE_AUTO:
                    maint.AlignType1(d, self.LoadPaperUI)

                elif align_type == ALIGN_TYPE_8XX:
                    maint.AlignType2(d, self.LoadPaperUI, self.AlignmentNumberUI,
                                     self.BothPensRequiredUI)

                elif align_type in (ALIGN_TYPE_9XX,ALIGN_TYPE_9XX_NO_EDGE_ALIGN):
                     maint.AlignType3(d, self.LoadPaperUI, self.AlignmentNumberUI,
                                      self.PaperEdgeUI, align_type)

                elif align_type in (ALIGN_TYPE_LIDIL_0_3_8, ALIGN_TYPE_LIDIL_0_4_3, ALIGN_TYPE_LIDIL_VIP):
                    maint.AlignxBow(d, align_type, self.LoadPaperUI, self.AlignmentNumberUI,
                                    self.PaperEdgeUI, self.InvalidPenUI, self.ColorAdjUI)

                elif align_type == ALIGN_TYPE_LIDIL_AIO:
                    maint.AlignType6(d, self.AioUI1, self.AioUI2, self.LoadPaperUI)

                elif align_type == ALIGN_TYPE_DESKJET_450:
                    maint.AlignType8(d, self.LoadPaperUI, self.AlignmentNumberUI)

                elif align_type == ALIGN_TYPE_LBOW:
                    maint.AlignType10(d, self.LoadPaperUI, self.Align10and11UI) 

                elif align_type == ALIGN_TYPE_LIDIL_0_5_4:
                    maint.AlignType11(d, self.LoadPaperUI, self.Align10and11UI, self.NotPhotoOnlyRequired) 
                    
                elif align_type == ALIGN_TYPE_OJ_PRO:
                    maint.AlignType12(d, self.LoadPaperUI)

            else:
                self.CheckDeviceUI()

        finally:
            d.close()
            QApplication.restoreOverrideCursor()



    def ColorAdjUI(self, line, maximum=0):
        dlg = ColorAdjForm(self, line)
        if dlg.exec_loop() == QDialog.Accepted:
            return True, dlg.value
        else:
            return False, 0

    def ColorCalUI(self):
        dlg = ColorCalForm(self)
        if dlg.exec_loop() == QDialog.Accepted:
            return True, dlg.value
        else:
            return False, 0

    def ColorCalUI2(self):
        dlg = ColorCalForm2(self)
        if dlg.exec_loop() == QDialog.Accepted:
            return True, dlg.value
        else:
            return False, 0

    def ColorCalUI4(self):
        dlg = ColorCal4Form(self)
        if dlg.exec_loop() == QDialog.Accepted:
            return True, dlg.values
        else:
            return False, None

    def ColorCalibrationButton_clicked(self):
        d = self.cur_device
        color_cal_type = d.color_cal_type
        log.debug(utils.bold("Color-cal: %s %s (type=%d) %s" % ("*"*20, self.cur_device.device_uri, color_cal_type, "*"*20)))

        try:
            QApplication.setOverrideCursor(QApplication.waitCursor)
            d.open()

            if d.isIdleAndNoError():
                QApplication.restoreOverrideCursor()

                if color_cal_type == COLOR_CAL_TYPE_DESKJET_450:
                     maint.colorCalType1(d, self.LoadPaperUI, self.ColorCalUI,
                                         self.PhotoPenRequiredUI)

                elif color_cal_type == COLOR_CAL_TYPE_MALIBU_CRICK:
                    maint.colorCalType2(d, self.LoadPaperUI, self.ColorCalUI2,
                                        self.InvalidPenUI)

                elif color_cal_type == COLOR_CAL_TYPE_STRINGRAY_LONGBOW_TORNADO:
                    maint.colorCalType3(d, self.LoadPaperUI, self.ColorAdjUI,
                                        self.PhotoPenRequiredUI2)

                elif color_cal_type == COLOR_CAL_TYPE_CONNERY:
                    maint.colorCalType4(d, self.LoadPaperUI, self.ColorCalUI4,
                                        self.WaitUI)

                elif color_cal_type == COLOR_CAL_TYPE_COUSTEAU:
                    maint.colorCalType5(d, self.LoadPaperUI)
                    
                elif color_cal_type == COLOR_CAL_CARRIER:
                    maint.colorCalType6(d, self.LoadPaperUI)

            else:
                self.CheckDeviceUI()

        finally:
            d.close()
            QApplication.restoreOverrideCursor()


    def PrintTestPageButton_clicked(self):
        d = self.cur_device
        printer_name = d.cups_printers[0]

        if len(d.cups_printers) > 1:
            from chooseprinterdlg import ChoosePrinterDlg2
            dlg = ChoosePrinterDlg2(d.cups_printers)

            if dlg.exec_loop() == QDialog.Accepted:
                printer_name = dlg.printer_name
            else:
                return

        try:
            QApplication.setOverrideCursor(QApplication.waitCursor)
            d.open()

            if d.isIdleAndNoError():
                QApplication.restoreOverrideCursor()
                d.close()

                if self.LoadPaperUI():
                    d.printTestPage(printer_name)

                    QMessageBox.information(self,
                                         self.caption(),
                                         self.__tr("<p><b>A test page should be printing on your printer.</b><p>If the page fails to print, please visit http://hplip.sourceforge.net for troubleshooting and support."),
                                          QMessageBox.Ok,
                                          QMessageBox.NoButton,
                                          QMessageBox.NoButton)

            else:
                d.close()
                self.CheckDeviceUI()

        finally:
            QApplication.restoreOverrideCursor()


    def CleanUI1(self):
        return CleaningForm(self, self.cur_device, 1).exec_loop() == QDialog.Accepted


    def CleanUI2(self):
        return CleaningForm(self, self.cur_device, 2).exec_loop() == QDialog.Accepted


    def CleanUI3(self):
        CleaningForm2(self).exec_loop()
        return True


    def WaitUI(self, seconds):
        WaitForm(seconds, None, self).exec_loop()


    def CleanPensButton_clicked(self):
        d = self.cur_device
        clean_type = d.clean_type
        log.debug(utils.bold("Clean: %s %s (type=%d) %s" % ("*"*20, self.cur_device.device_uri, clean_type, "*"*20)))

        try:
            QApplication.setOverrideCursor(QApplication.waitCursor)
            d.open()

            if d.isIdleAndNoError():
                QApplication.restoreOverrideCursor()

                if clean_type == CLEAN_TYPE_PCL:
                    maint.cleaning(d, clean_type, maint.cleanType1, maint.primeType1,
                                    maint.wipeAndSpitType1, self.LoadPaperUI,
                                    self.CleanUI1, self.CleanUI2, self.CleanUI3,
                                    self.WaitUI)

                elif clean_type == CLEAN_TYPE_LIDIL:
                    maint.cleaning(d, clean_type, maint.cleanType2, maint.primeType2,
                                    maint.wipeAndSpitType2, self.LoadPaperUI,
                                    self.CleanUI1, self.CleanUI2, self.CleanUI3,
                                    self.WaitUI)

                elif clean_type == CLEAN_TYPE_PCL_WITH_PRINTOUT:
                    maint.cleaning(d, clean_type, maint.cleanType1, maint.primeType1,
                                    maint.wipeAndSpitType1, self.LoadPaperUI,
                                    self.CleanUI1, self.CleanUI2, self.CleanUI3,
                                    self.WaitUI)
            else:
                self.CheckDeviceUI()

        finally:
            d.close()
            QApplication.restoreOverrideCursor()

    def OpenEmbeddedBrowserButton_clicked(self):
        utils.openURL("http://%s" % self.cur_device.host)
            
    def faxAddressBookButton_clicked(self):
        self.RunCommand(self.cmd_fab)
        
    def faxSettingsButton_clicked(self):
        try:
            self.cur_device.open()

            try:
                result_code, fax_num = self.cur_device.getPML(pml.OID_FAX_LOCAL_PHONE_NUM)
            except Error:
                log.error("PML failure.")
                self.FailureUI(self.__tr("<p><b>Operation failed. Device busy.</b>"))
                return

            fax_num = str(fax_num)

            try:
                result_code, name = self.cur_device.getPML(pml.OID_FAX_STATION_NAME)
            except Error:
                log.error("PML failure.")
                self.FailureUI(self.__tr("<p><b>Operation failed. Device busy.</b>"))
                return

            name = str(name)

            dlg = FaxSettingsForm(self.cur_device, fax_num, name, self)
            dlg.exec_loop()
        finally:
            self.cur_device.close()


    def addressBookButton_clicked(self):
        self.RunCommand(self.cmd_fab)
        
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
        

    def FailureUI(self, error_text):
        QMessageBox.critical(self,
                             self.caption(),
                             error_text,
                              QMessageBox.Ok,
                              QMessageBox.NoButton,
                              QMessageBox.NoButton)
        
    def __tr(self,s,c = None):
        return qApp.translate("DevMgr4",s,c)
