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
# Authors: Don Welch

import os, Queue

from base.g import *
from prnt import cups, printable_areas
from base import device, utils, pml, service
from copier import copier

from qt import *
from makecopiesform_base import MakeCopiesForm_base
from waitform import WaitForm


class MakeCopiesForm(MakeCopiesForm_base):
    def __init__(self, sock, bus='cups', device_uri=None, printer_name=None, 
                num_copies=None, contrast=None, quality=None, 
                reduction=None, fit_to_page=None, 
                parent=None, name=None, modal=0, fl=0):

        MakeCopiesForm_base.__init__(self,parent,name,modal,fl)

        self.sock = sock
        self.device_uri = device_uri
        self.printer_name = printer_name
        self.init_failed = False
        self.waitdlg = None
        self.num_copies = num_copies
        self.contrast = contrast
        self.quality = quality
        self.reduction = reduction
        self.fit_to_page = fit_to_page

        self.update_queue = Queue.Queue() # UI updates from copy thread
        self.event_queue = Queue.Queue() # UI events (from hpssd) to send thread

        icon = QPixmap(os.path.join(prop.image_dir, 'HPmenu.png'))
        self.setIcon(icon)

        pix = QPixmap(os.path.join(prop.image_dir, 'status_refresh.png'))
        self.refreshToolButton.setPixmap(pix)

        if self.device_uri and self.printer_name:
            log.error("You may not specify both a printer (-p) and a device (-d).")
            self.FailureUI(self.__tr("<p><b>You may not specify both a printer (-p) and a device (-d)."))
            self.device_uri, self.printer_name = None, None
            self.init_failed = True

        self.cups_printers = cups.getPrinters()
        log.debug(self.cups_printers)

        if not self.device_uri and not self.printer_name:
            t = device.probeDevices(None, bus=bus, filter='copy')
            probed_devices = []

            for d in t:
                if d.startswith('hp:'):
                    probed_devices.append(d)

            log.debug(probed_devices)

            max_deviceid_size, x, devices = 0, 0, {}

            for d in probed_devices:
                printers = []
                for p in self.cups_printers:
                    if p.device_uri == d:
                        printers.append(p.name)
                devices[x] = (d, printers)
                x += 1
                max_deviceid_size = max(len(d), max_deviceid_size)

            if x == 0:
                from nodevicesform import NoDevicesForm
                self.FailureUI(self.__tr("<p><b>No devices found.</b><p>Please make sure your device is properly installed and try again."))
                self.init_failed = True

            elif x == 1:
                log.info(utils.bold("Using device: %s" % devices[0][0]))
                self.device_uri = devices[0][0]


            else:
                from choosedevicedlg import ChooseDeviceDlg
                dlg = ChooseDeviceDlg(devices) #, ['hp'])

                if dlg.exec_loop() == QDialog.Accepted:
                    self.device_uri = dlg.device_uri
                else:
                    self.init_failed = True


        QTimer.singleShot(0, self.InitialUpdate)

    def InitialUpdate(self):
        if self.init_failed:
            self.close()
            return        

        self.printer_list = []

        self.dev = copier.PMLCopyDevice(device_uri=self.device_uri, 
                                        printer_name=self.printer_name, 
                                        hpssd_sock=self.sock)

        if self.dev.copy_type == COPY_TYPE_NONE:
            self.FailureUI(self.__tr("<b>Sorry, make copies functionality is not implemented for this device.</b>"))
            self.close()
            return

        self.scan_style = self.dev.mq.get('scan-style', SCAN_STYLE_FLATBED)
        self.copy_type = self.dev.mq.get('copy-type', COPY_TYPE_DEVICE)

        if self.scan_style == SCAN_STYLE_SCROLLFED:
            self.fitToPageCheckBox.setEnabled(False)
            self.fit_to_page = pml.COPIER_FIT_TO_PAGE_DISABLED

        self.device_uri = self.dev.device_uri
        user_cfg.last_used.device_uri = self.device_uri

        log.debug(self.device_uri)
        self.DeviceURIText.setText(self.device_uri)

        for p in self.cups_printers:
            if p.device_uri == self.device_uri:
                self.printer_list.append(p.name)

        for p in self.printer_list:
            self.printerNameComboBox.insertItem(p)

        self.UpdatePrinterStatus()

        if self.printer_name is None:
            self.printerNameComboBox.setCurrentItem(0)

        elif self.printer_name in self.printer_list:
            self.printerNameComboBox.setCurrentText(self.printer_name)

        self.current_printer = str(self.printerNameComboBox.currentText())

        self.UpdatePrinterInfo()


    def UpdatePrinterStatus(self):
        QApplication.setOverrideCursor(QApplication.waitCursor)

        try:
            try:
                self.dev.open()
            except Error, e:
                log.warn(e.msg)

            try:
                self.dev.queryDevice(quick=True)
            except Error, e:
                log.error("Query device error (%s)." % e.msg)
                self.dev.error_state = ERROR_STATE_ERROR

        finally:
            self.dev.close()
            QApplication.restoreOverrideCursor()


        self.StateText.setText(self.dev.status_desc)

        if self.dev.device_state == DEVICE_STATE_NOT_FOUND:
            self.FailureUI(self.__tr("<b>Unable to communicate with device:</b><p>%s" % self.device_uri))
        else:
            # get sticky settings as defaults (if not spec'd on command line)
            if self.num_copies is None:
                result_code, self.num_copies = self.dev.getPML(pml.OID_COPIER_NUM_COPIES)

            if self.contrast is None:
                result_code, self.contrast = self.dev.getPML(pml.OID_COPIER_CONTRAST)

            if self.reduction is None:
                result_code, self.reduction = self.dev.getPML(pml.OID_COPIER_REDUCTION)

            if self.quality is None:
                result_code, self.quality = self.dev.getPML(pml.OID_COPIER_QUALITY)

            if self.scan_style == SCAN_STYLE_FLATBED and self.fit_to_page is None:
                result_code, self.fit_to_page = self.dev.getPML(pml.OID_COPIER_FIT_TO_PAGE)

                if result_code != pml.ERROR_OK:
                    self.fit_to_page = pml.COPIER_FIT_TO_PAGE_DISABLED
                    self.fitToPageCheckBox.setEnabled(False)

            else:
                self.fit_to_page = pml.COPIER_FIT_TO_PAGE_DISABLED

            if self.scan_style != SCAN_STYLE_FLATBED:
                self.fitToPageCheckBox.setEnabled(False)


            result_code, self.max_reduction = self.dev.getPML(pml.OID_COPIER_REDUCTION_MAXIMUM)
            result_code, self.max_enlargement = self.dev.getPML(pml.OID_COPIER_ENLARGEMENT_MAXIMUM)

            # contrast
            self.contrastTextLabel.setText("%d" % (self.contrast/25))
            self.contrastSlider.setValue(self.contrast/25)
            self.contrastSlider.setTickmarks(QSlider.Below)
            self.contrastSlider.setTickInterval(1)

            self.reductionSlider.setValue(self.reduction)
            self.reductionSlider.setRange(self.max_reduction, self.max_enlargement)
            self.reductionSlider.setTickmarks(QSlider.Below)
            self.reductionSlider.setTickInterval(10)

            if self.fit_to_page == pml.COPIER_FIT_TO_PAGE_ENABLED:
                self.fitToPageCheckBox.setChecked(True)
                self.reductionTextLabel.setText("")
                self.reductionSlider.setEnabled(False)
            else:
                self.fitToPageCheckBox.setChecked(False)
                self.reductionTextLabel.setText("%d%%" % self.reduction)
                self.reductionSlider.setEnabled(True)

            # num_copies
            self.numberCopiesSpinBox.setValue(self.num_copies)

            # quality
            if self.quality == pml.COPIER_QUALITY_FAST:
                self.qualityButtonGroup.setButton(0)

            elif self.quality == pml.COPIER_QUALITY_DRAFT:
                self.qualityButtonGroup.setButton(1)

            elif self.quality == pml.COPIER_QUALITY_NORMAL:
                self.qualityButtonGroup.setButton(2)

            elif self.quality == pml.COPIER_QUALITY_PRESENTATION:
                self.qualityButtonGroup.setButton(3)

            elif self.quality == pml.COPIER_QUALITY_BEST:
                self.qualityButtonGroup.setButton(4)


    def UpdatePrinterInfo(self):
        for p in self.cups_printers:
            if p.name == self.current_printer:

                try:
                    self.LocationText.setText(p.location)
                except AttributeError:
                    self.LocationText.setText('')

                try:
                    self.CommentText.setText(p.info)
                except AttributeError:
                    self.CommentText.setText('')

                break


    def copy_canceled(self):
        self.event_queue.put(copier.COPY_CANCELED)
        service.sendEvent(self.sock, EVENT_COPY_JOB_CANCELED, device_uri=self.device_uri)


    def copy_timer_timeout(self):
        while self.update_queue.qsize():
            try:
                status = self.update_queue.get(0)
            except Queue.Empty:
                break

            if status == copier.STATUS_IDLE:
                self.copy_timer.stop()

                if self.waitdlg is not None:
                    self.waitdlg.hide()
                    self.waitdlg.close()
                    self.waitdlg = None

            elif status in (copier.STATUS_SETTING_UP, copier.STATUS_WARMING_UP):
                self.waitdlg.setMessage(self.__tr("Warming up..."))

            elif status == copier.STATUS_ACTIVE:
                self.waitdlg.setMessage(self.__tr("Copying..."))

            elif status in (copier.STATUS_ERROR, copier.STATUS_DONE):
                self.copy_timer.stop()

                if self.waitdlg is not None:
                    self.waitdlg.hide()
                    self.waitdlg.close()
                    self.waitdlg = None

                if status == copier.STATUS_ERROR:
                    self.FailureUI(self.__tr("<b>Copier error.</b><p>"))
                    service.sendEvent(self.sock, EVENT_COPY_JOB_FAIL, device_uri=self.device_uri)

                elif status == copier.STATUS_DONE:
                    service.sendEvent(self.sock, EVENT_END_COPY_JOB, device_uri=self.device_uri)

    def makeCopiesPushButton_clicked(self):
        service.sendEvent(self.sock, EVENT_START_COPY_JOB, device_uri=self.device_uri)

        self.waitdlg = WaitForm(0, self.__tr("Initializing..."), self.copy_canceled, self, modal=1)
        self.waitdlg.show()

        self.copy_timer = QTimer(self, "CopyTimer")
        self.connect(self.copy_timer, SIGNAL('timeout()'), self.copy_timer_timeout)
        self.copy_timer.start(1000) # 1 sec UI updates

        self.dev.copy(self.num_copies, self.contrast, self.reduction,
                      self.quality, self.fit_to_page, self.scan_style,
                      self.update_queue, self.event_queue)


    def SuccessUI(self):
        QMessageBox.information(self,
                             self.caption(),
                             self.__tr("<p><b>The operation completed successfully.</b>"),
                              QMessageBox.Ok,
                              QMessageBox.NoButton,
                              QMessageBox.NoButton)

    def FailureUI(self, error_text):
        QMessageBox.critical(self,
                             self.caption(),
                             error_text,
                              QMessageBox.Ok,
                              QMessageBox.NoButton,
                              QMessageBox.NoButton)

    def WarningUI(self, msg):
        QMessageBox.warning(self,
                             self.caption(),
                             msg,
                              QMessageBox.Ok,
                              QMessageBox.NoButton,
                              QMessageBox.NoButton)

    def qualityButtonGroup_clicked(self,a0):
        if a0 == 0:
            self.quality = pml.COPIER_QUALITY_FAST
        elif a0 == 1:
            self.quality = pml.COPIER_QUALITY_DRAFT
        elif a0 == 2:
            self.quality = pml.COPIER_QUALITY_NORMAL
        elif a0 == 3:
            self.quality = pml.COPIER_QUALITY_PRESENTATION
        elif a0 == 4:
            self.quality = pml.COPIER_QUALITY_BEST

    def reductionSlider_valueChanged(self,a0):
        self.reduction = a0
        self.reductionTextLabel.setText("%d%%" % self.reduction)

    def contrastSlider_valueChanged(self,a0):
        self.contrast = a0 * 25
        self.contrastTextLabel.setText("%+d" % a0)

    def fitToPageCheckBox_clicked(self):
        if self.fitToPageCheckBox.isChecked():
            self.fit_to_page = pml.COPIER_FIT_TO_PAGE_ENABLED
            self.reductionTextLabel.setText("")
            self.reductionSlider.setEnabled(False)
        else:
            self.fit_to_page = pml.COPIER_FIT_TO_PAGE_DISABLED
            self.reductionTextLabel.setText("%d%%" % self.reduction)
            self.reductionSlider.setEnabled(True)

    def numberCopiesSpinBox_valueChanged(self,a0):
        self.num_copies = a0


    def __tr(self,s,c = None):
        return qApp.translate("MakeCopiesForm",s,c)
