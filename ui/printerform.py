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
# Authors: Don Welch


from qt import *
from printerform_base import PrinterForm_base
from base.g import *
from base.codes import *
from base import utils, device, magic
from prnt import cups
import glob


class RangeValidator(QValidator):
    def __init__(self, parent=None, name=None):
        QValidator.__init__(self, parent, name)

    def validate(self, input, pos):
        for x in str(input)[pos-1:]:
            if x not in '0123456789,-':
                return QValidator.Invalid, pos

        return QValidator.Acceptable, pos


class PrinterForm(PrinterForm_base):

    def __init__(self, sock, bus='cups', device_uri=None, printer_name=None, args=None, 
                 parent=None,name=None,modal=0,fl=0):

        PrinterForm_base.__init__(self,parent,name,modal,fl)
        self.sock = sock
        self.device_uri = device_uri
        self.printer_name = printer_name
        self.file_list = []
        self.auto_duplex_button_group = 0
        self.orientation_button_group = 0
        self.pages_button_group = 0
        self.init_failed = False

        self.pageRangeEdit.setValidator(RangeValidator(self.pageRangeEdit))

        icon = QPixmap(os.path.join(prop.image_dir, 'HPmenu.png'))
        self.setIcon(icon)
        pix = QPixmap(os.path.join(prop.image_dir, 'folder_open.png'))
        self.addFileButton.setPixmap(pix)
        pix = QPixmap(os.path.join(prop.image_dir, 'folder_remove.png'))
        self.delFileButton.setPixmap(pix)
        pix = QPixmap(os.path.join(prop.image_dir, 'status_refresh.png'))
        self.refreshToolButton.setPixmap(pix)
        self.fileListView.setSorting(-1)

        self.allowable_mime_types = cups.getAllowableMIMETypes()
        log.debug(self.allowable_mime_types)

        self.MIME_TYPES_DESC = \
        {
            "application/pdf" : self.__tr("PDF Document"),
            "application/postscript" : self.__tr("Postscript Document"),
            "application/vnd.hp-HPGL" : self.__tr("HP Graphics Language File"),
            "application/x-cshell" : self.__tr("C Shell Script"),
            "application/x-perl" : self.__tr("Perl Script"),
            "application/x-python" : self.__tr("Python Program"),
            "application/x-shell" : self.__tr("Shell Script"),
            "text/plain" : self.__tr("Plain Text"),
            "text/html" : self.__tr("HTML Dcoument"),
            "image/gif" : self.__tr("GIF Image"),
            "image/png" : self.__tr("PNG Image"),
            "image/jpeg" : self.__tr("JPEG Image"),
            "image/tiff" : self.__tr("TIFF Image"),
            "image/x-bitmap" : self.__tr("Bitmap (BMP) Image"),
            "image/x-photocd" : self.__tr("Photo CD Image"),
            "image/x-portable-anymap" : self.__tr("Portable Image (PNM)"),
            "image/x-portable-bitmap" : self.__tr("Portable B&W Image (PBM)"),
            "image/x-portable-graymap" : self.__tr("Portable Grayscale Image (PGM)"),
            "image/x-portable-pixmap" : self.__tr("Portable Color Image (PPM)"),
            "image/x-sgi-rgb" : self.__tr("SGI RGB"),
            "image/x-xbitmap" : self.__tr("X11 Bitmap (XBM)"),
            "image/x-xpixmap" : self.__tr("X11 Pixmap (XPM)"),
            "image/x-sun-raster" : self.__tr("Sun Raster Format"),
        }

        if args is not None:
            for f in args:
                self.addFile(f)

        icon = QPixmap(os.path.join(prop.image_dir, 'HPmenu.png'))
        self.setIcon(icon)

        pix = QPixmap(os.path.join(prop.image_dir, 'folder_open.png'))
        self.addFileButton.setPixmap(pix)

        pix = QPixmap(os.path.join(prop.image_dir, 'folder_remove.png'))
        self.delFileButton.setPixmap(pix)

        pix = QPixmap(os.path.join(prop.image_dir, 'status_refresh.png'))
        self.refreshToolButton.setPixmap(pix)

        self.fileListView.setSorting(-1)


        if self.device_uri and self.printer_name:
            log.error("You may not specify both a printer (-p) and a device (-d).")
            self.FailureUI(self.__tr("<p><b>You may not specify both a printer (-p) and a device (-d)."))
            self.device_uri, self.printer_name = None, None
            self.init_failed = True

        self.cups_printers = cups.getPrinters()
        log.debug(self.cups_printers)

        if not self.device_uri and not self.printer_name:
            t = device.probeDevices(self.sock, bus=bus, filter='none')
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
                from chooseprinterdlg import ChoosePrinterDlg
                dlg = ChoosePrinterDlg(self.cups_printers)
                
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

        try:
            self.dev = device.Device(device_uri=self.device_uri, 
                                     printer_name=self.printer_name, 
                                     hpssd_sock=self.sock)
        except Error, e:
            log.error("Invalid device URI or printer name.")
            self.FailureUI("<b>Invalid device URI or printer name.</b><p>Please check the parameters to hp-print and try again.")
            self.close()
            return

        self.device_uri = self.dev.device_uri

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
        
        
        if self.dev.device_state == DEVICE_STATE_NOT_FOUND:
            self.FailureUI(self.__tr("<b>Unable to communicate with device:</b><p>%s" % self.device_uri))

        try:
            self.StateText.setText(self.dev.status_desc)
        except AttributeError:
            pass
        


    def EventUI(self, event_code, event_type, error_string_short,
                error_string_long, retry_timeout, job_id,
                device_uri):

        log.debug("Event: device_uri=%s code=%d type=%s string=%s timeout=%d id=%d uri=%s" %
                 (device_uri, event_code, event_type,  
                  error_string_short, retry_timeout, job_id, device_uri))

        if device_uri == self.dev.device_uri:
            self.StateText.setText(error_string_short)


    def addFile(self, path):
        path = os.path.realpath(path)
        if os.path.exists(path):
            mime_type = magic.mime_type(path)
            mime_type_desc = mime_type

            try:
                mime_type_desc = self.MIME_TYPES_DESC[mime_type]
            except KeyError:
                self.WarningUI(self.__tr("<b>You are trying to add a file that cannot be directly printed with this utility.</b><p>To print this file, use the print command in the application that created it."))
            else:
                log.debug("Adding file %s (%s,%s)" % (path, mime_type, mime_type_desc))
                self.file_list.append((path, mime_type, mime_type_desc))
        else:
            self.FailureUI(self.__tr("<b>Unable to add file '%s' to file list.</b><p>Check the file name and try again." % path))

        self.UpdateFileList()

    def UpdateFileList(self):
        self.fileListView.clear()
        temp = self.file_list[:]
        temp.reverse()

        for p, t, d in temp:
            i = QListViewItem(self.fileListView, os.path.basename(p), d, p)
            #self.fileListView.setSelected( i, True )

        non_empty_file_list = self.fileListView.childCount() > 0
        ##self.delFileButton.setEnabled( non_empty_file_list )
        self.printPushButton.setEnabled(non_empty_file_list)

    def addFileButton_clicked(self):
        self.setFocus()

        log.debug("isTopLevel %d" % self.isTopLevel())
        log.debug("hasFocus %d" % self.hasFocus())
        log.debug("isEnabled %d" % self.isEnabled())

        workingDirectory = os.path.expanduser("~")

        log.debug("workingDirectory: %s" % workingDirectory)

        dlg = QFileDialog(workingDirectory, QString.null, None, None, True)

        dlg.setCaption("openfile")
        dlg.setMode(QFileDialog.ExistingFile)
        dlg.show()

        if dlg.exec_loop() == QDialog.Accepted:
                results = dlg.selectedFile()
                workingDirectory = dlg.url()
                log.debug("results: %s" % results)
                log.debug("workingDirectory: %s" % workingDirectory)

                if results:
                    self.addFile(str(results))



    def delFileButton_clicked(self):
        try:
            path = self.fileListView.currentItem().text(2)
        except AttributeError:
            return
        else:
            temp = self.file_list[:]
            index = 0
            for p, t, d in temp:
                if p == path:
                    del self.file_list[index]
                    break
                index += 1

            self.UpdateFileList()


    def fileListView_currentChanged(self,item):
        #print item
        pass

    def printerNameComboBox_highlighted(self,a0):
        self.current_printer = str(a0)
        self.UpdatePrinterInfo()

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

                cups.openPPD(p.name)
                self.UpdateDuplex()
                cups.closePPD()
                break

    def UpdateDuplex(self):
        duplex = cups.getPPDOption("Duplex")
        if duplex is not None:
            if duplex.startswith("long"):
                self.duplexButtonGroup.setButton(1)
                self.auto_duplex_button_group = 1
            elif duplex.startswith("short"):
                self.duplexButtonGroup.setButton(2)
                self.auto_duplex_button_group = 2
            else:
                self.duplexButtonGroup.setButton(0)
                self.auto_duplex_button_group = 0
        else:
            self.duplexButtonGroup.setEnabled(False)


    def pagesButtonGroup_clicked(self,item):
        self.pageRangeEdit.setEnabled(item == 1)

    def printPushButton_clicked(self):
        copies = int(self.copiesSpinBox.value())
        rev = bool(self.reverseCheckBox.isChecked())
        collate = bool(self.collateCheckBox.isChecked())
        all_pages = self.pages_button_group == 0
        page_range = str(self.pageRangeEdit.text())
        page_set = int(self.pageSetComboBox.currentItem())
        nup = int(str(self.nUpComboBox.currentText()))
        mirror = bool(self.mirrorCheckBox.isChecked())

        for p, t, d in self.file_list:
            
            alt_nup = (nup > 1 and t == 'application/postscript' and utils.which('psnup'))
                
            if utils.which('lpr'):
                if alt_nup:
                    cmd = ' '.join(['psnup', '-%d' % nup, ''.join(['"', p, '"']), '| lpr -P', self.current_printer])
                else:
                    cmd = ' '.join(['lpr -P', self.current_printer])
                
                if copies > 1:
                    cmd = ' '.join([cmd, '-#%d' % copies])
                
            else:
                if alt_nup:
                    cmd = ' '.join(['psnup', '-%d' % nup, ''.join(['"', p, '"']), '| lp -c -d', self.current_printer])
                else:
                    cmd = ' '.join(['lp -c -d', self.current_printer])
                
                if copies > 1:
                    cmd = ' '.join([cmd, '-n%d' % copies])


            if not all_pages and len(page_range) > 0:
                cmd = ' '.join([cmd, '-o page-ranges=%s' % page_range])

            if page_set > 0:
                if page_set == 1:
                    cmd = ' '.join([cmd, '-o page-set=even'])
                else:
                    cmd = ' '.join([cmd, '-o page-set=odd'])

            if rev:
                cmd = ' '.join([cmd, '-o outputorder=reverse'])
                
            if mirror:
                cmd = ' '.join([cmd, '-o mirror'])

            if collate and copies > 1:
                cmd = ' '.join([cmd, '-o Collate=True'])

            if t in ["application/x-cshell",
                     "application/x-perl",
                     "application/x-python",
                     "application/x-shell",
                     "text/plain",]:
                     
                cmd = ' '.join([cmd, '-o prettyprint'])

            if nup > 1 and not alt_nup:
                cmd = ' '.join([cmd, '-o number-up=%d' % nup])

            if self.auto_duplex_button_group == 1: # long
                cmd = ' '.join([cmd, '-o sides=two-sided-long-edge'])
            elif self.auto_duplex_button_group == 2: # short
                cmd = ' '.join([cmd, '-o sides=two-sided-short-edge'])
            else:
                cmd = ' '.join([cmd, '-o sides=one-sided'])

            if self.orientation_button_group == 1:
                cmd = ' '.join([cmd, '-o landscape'])

            if not alt_nup:
                cmd = ''.join([cmd, ' "', p, '"'])

            log.debug("Printing: %s" % cmd)

            if os.system(cmd) != 0:
                log.error("Print command failed.")
                self.FailureUI(self.__tr("Print command failed."))
        
        del self.file_list[:]
        self.UpdateFileList()

    def pagesButtonGroup_clicked(self,a0):
        self.pages_button_group = a0
        self.pageRangeEdit.setEnabled(a0 == 1)


    def duplexButtonGroup_clicked(self,a0):
        self.auto_duplex_button_group = a0

    def orientationButtonGroup_clicked(self,a0):
        self.orientation_button_group = a0

    def refreshToolButton_clicked(self):
        self.UpdatePrinterStatus()


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


    def __tr(self,s,c = None):
        return qApp.translate("PrinterForm",s,c)


