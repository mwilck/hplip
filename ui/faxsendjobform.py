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
# Author: Don Welch
#

# Std Lib
import glob, Queue, socket, struct

# Local
from base.g import *
from base import utils, device, pml, service, msg, magic

try:
    from fax import fax
except ImportError:
    # This can fail on Python < 2.3 due to the datetime module
    log.error("Fax send disabled - Python 2.3+ required.")
    sys.exit(1)

from prnt import cups

# Qt/UI
from qt import *
from faxsendjobform_base import FaxSendJobForm_base
from waitform import WaitForm
from faxsettingsform import FaxSettingsForm
from faxallowabletypesdlg import FaxAllowableTypesDlg

try:
    import reportlab
except ImportError:
    coverpages_enabled = False
else:
    from fax import coverpages
    from coverpageform import CoverpageForm
    coverpages_enabled = True

# Used to store MIME types for files
# added directly in interface.
job_types = {} # { job_id : "mime_type", ...}


class FileListViewItem(QListViewItem):
    def __init__(self, parent, title, mime_type_desc, path, str_pages):
        QListViewItem.__init__(self, parent, title, mime_type_desc, str_pages)
        self.path = path


class FaxSendJobForm(FaxSendJobForm_base):

    def __init__(self, sock, device_uri, printer_name, args, 
                 parent=None, name=None, 
                 modal=0, fl=0):

        FaxSendJobForm_base.__init__(self, parent, name, modal, fl)
        icon = QPixmap(os.path.join(prop.image_dir, 'HPmenu.png'))
        self.setIcon(icon)
        self.sock = sock
        self.init_failed = False
        self.device_uri = device_uri
        self.dev = None
        self.printer_name = printer_name
        bus = 'cups'
        self.document_num = 1
        self.filename = ''
        self.waitdlg = None
        self.recipient_list = []
        self.username = prop.username
        self.args = args
        self.prettyprint = False

        self.update_queue = Queue.Queue() # UI updates from send thread
        self.event_queue = Queue.Queue() # UI events (cancel) to send thread

        pix = QPixmap(os.path.join(prop.image_dir, 'folder_remove.png'))
        self.delFileButton.setPixmap(pix)

        pix = QPixmap(os.path.join(prop.image_dir, 'status_refresh.png'))
        self.refreshToolButton.setPixmap(pix)

        pix = QPixmap(os.path.join(prop.image_dir, 'up.png'))
        self.upFileButton.setPixmap(pix)

        pix = QPixmap(os.path.join(prop.image_dir, 'down.png'))
        self.downFileButton.setPixmap(pix)

        self.fileListView.setSorting(-1)

        # TODO: Hook these up. Need to read current settings
        # from PDD file for the current device queue
        #self.paperSizeButtonGroup.setEnabled(False)
        #self.qualityButtonGroup.setEnabled(False)

        self.addCoverpagePushButton.setEnabled(coverpages_enabled)
        self.cover_page_func, cover_page_png = None, None
        self.cover_page_message = ''
        self.cover_page_re = ''
        self.cover_page_name = ''

        self.file_list = []

        self.db =  fax.FaxAddressBook() # kirbybase instance
        self.last_db_modification = self.db.last_modification_time()

        self.allowable_mime_types = cups.getAllowableMIMETypes()
        self.allowable_mime_types.append("application/hplip-fax")
        self.allowable_mime_types.append("application/x-python")

        log.debug(self.allowable_mime_types)

        self.MIME_TYPES_DESC = \
        {
            "application/pdf" : (self.__tr("PDF Document"), '.pdf'),
            "application/postscript" : (self.__tr("Postscript Document"), '.ps'),
            "application/vnd.hp-HPGL" : (self.__tr("HP Graphics Language File"), '.hgl, .hpg, .plt, .prn'),
            "application/x-cshell" : (self.__tr("C Shell Script"), '.csh, .sh'),
            "application/x-csource" : (self.__tr("C Source Code"), '.c'),
            "text/cpp": (self.__tr("C++ Source Code"), '.cpp, .cxx'),
            "application/x-perl" : (self.__tr("Perl Script"), '.pl'),
            "application/x-python" : (self.__tr("Python Program"), '.py'),
            "application/x-shell" : (self.__tr("Shell Script"), '.sh'),
            "text/plain" : (self.__tr("Plain Text"), '.txt, .log, etc'),
            "text/html" : (self.__tr("HTML Dcoument"), '.htm, .html'),
            "image/gif" : (self.__tr("GIF Image"), '.gif'),
            "image/png" : (self.__tr("PNG Image"), '.png'),
            "image/jpeg" : (self.__tr("JPEG Image"), '.jpg, .jpeg'),
            "image/tiff" : (self.__tr("TIFF Image"), '.tif, .tiff'),
            "image/x-bitmap" : (self.__tr("Bitmap (BMP) Image"), '.bmp'),
            "image/x-bmp" : (self.__tr("Bitmap (BMP) Image"), '.bmp'),
            "image/x-photocd" : (self.__tr("Photo CD Image"), '.pcd'),
            "image/x-portable-anymap" : (self.__tr("Portable Image (PNM)"), '.pnm'),
            "image/x-portable-bitmap" : (self.__tr("Portable B&W Image (PBM)"), '.pbm'),
            "image/x-portable-graymap" : (self.__tr("Portable Grayscale Image (PGM)"), '.pgm'),
            "image/x-portable-pixmap" : (self.__tr("Portable Color Image (PPM)"), '.ppm'),
            "image/x-sgi-rgb" : (self.__tr("SGI RGB"), '.rgb'),
            "image/x-xbitmap" : (self.__tr("X11 Bitmap (XBM)"), '.xbm'),
            "image/x-xpixmap" : (self.__tr("X11 Pixmap (XPM)"), '.xpm'),
            "image/x-sun-raster" : (self.__tr("Sun Raster Format"), '.ras'),
            "application/hplip-fax" : (self.__tr("HP Fax"), '.g3'),
            "application/hplip-fax-coverpage" : (self.__tr("HP Fax Coverpage"), 'n/a'),
        }

        if self.device_uri and self.printer_name:
            log.error("You may not specify both a printer (-p) and a device (-d).")
            self.FailureUI(self.__tr("<p><b>You may not specify both a printer (-p) and a device (-d)."))
            self.device_uri, self.printer_name = None, None
            self.init_failed = True

        self.cups_printers = cups.getPrinters()
        log.debug(self.cups_printers)

        if self.printer_name:
            found = False
            for p in self.cups_printers:
                if p.name == printer_name:
                    self.device_uri = p.device_uri
                    found = True
                    break
    
            if not found:
                self.FailureUI(self.__tr("<b>Unknown printer name: %1</b><p>Please check the printer name and try again.").arg(self.printer_name))
    
            if found and not p.device_uri.startswith('hpfax:/'):
                self.FailureUI(self.__tr("You must specify a printer that has a device URI in the form 'hpfax:/...'"))
                self.init_failed = True
        
        if not self.device_uri and not self.printer_name:
            t = device.probeDevices(None, bus=bus, filter='fax')
            probed_devices = []

            for d in t:
                probed_devices.append(d.replace('hp:/', 'hpfax:/'))

            probed_devices = utils.uniqueList(probed_devices)
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
                dlg = ChoosePrinterDlg(self.cups_printers, ['hpfax'])
                if dlg.exec_loop() == QDialog.Accepted:
                    self.device_uri = dlg.device_uri
                else:
                    self.init_failed = True

        cmd_print, cmd_scan, cmd_pcard, \
            cmd_copy, cmd_fax, cmd_fab = utils.deviceDefaultFunctions()

        self.cmd_fab = user_cfg.commands.fab or cmd_fab
        log.debug("FAB command: %s" % self.cmd_fab)

        if not coverpages_enabled:
            log.warn("Coverpages disabled. Reportlab not installed.")

        QTimer.singleShot(0, self.InitialUpdate)


    # ************************************** Device status
    def InitialUpdate(self):
        if self.init_failed:
            self.close()
            return      

        self.printer_list = []

        try:
            self.dev = fax.FaxDevice(device_uri=self.device_uri, 
                                     printer_name=self.printer_name)
        except Error, e:
            log.error("Invalid device URI or printer name.")
            self.FailureUI("<b>Invalid device URI or printer name.</b><p>Please check the parameters to hp-sendfax and try again.")
            self.close()
            return

        self.device_uri = self.dev.device_uri
        user_cfg.last_used.device_uri = self.device_uri

        log.debug("Device URI=%s" %self.device_uri)
        self.DeviceURIText.setText(self.device_uri)

        log.debug("Setting date and time on device.")

        try:
            self.dev.setDateAndTime()
        except Error:
            pass # This will be caught further down

        for p in self.cups_printers:
            if p.device_uri == self.device_uri:
                self.printer_list.append(p.name)

        if not self.printer_list:
            self.FailureUI(self.__tr("<b>No appropriate CUPS fax queue is setup.</b><p>Please install a CUPS queue for device '%1' using the HPLIP Fax PPD file. (You could use 'hp-setup' to do this.)").arg(self.device_uri))
            self.close()
            return

        for p in self.printer_list:
            self.printerNameComboBox.insertItem(p)

        self.UpdatePrinterStatus()

        if self.printer_name is None:
            self.printerNameComboBox.setCurrentItem(0)
        elif self.printer_name in self.printer_list:
            self.printerNameComboBox.setCurrentText(self.printer_name)

        self.current_printer = str(self.printerNameComboBox.currentText())

        self.UpdatePrinterInfo()

        self.UpdateIndividualList()
        self.UpdateGroupList()
        self.CheckSendButtons()
        self.selection = []

        if len(self.args):
            for a in self.args:
                if os.path.exists(a):
                    self.processFile(a, a)
                else:
                    self.FailureUI(self.__tr("<b>File not found:</b><p>%1").arg(a))

        self.check_timer = QTimer(self, "CheckTimer")
        self.connect(self.check_timer, SIGNAL('timeout()'), self.PeriodicCheck)
        self.check_timer.start(3000)

        self.busy = False

    def PeriodicCheck(self):
        if not self.busy:
            log.debug("Checking for incoming faxes...")

            fields, data, result_code = \
                msg.xmitMessage(self.sock, "FaxCheck", None,
                                {"username": self.username})

            if result_code == ERROR_FAX_READY:
                # fax is waiting
                username = fields['username']
                job_id = fields['job-id']
                job_size = fields['job-size']
                title = fields['title']

                if self.isMinimized():
                    self.showNormal()

                self.check_timer.stop()
                self.addFileFromJob(0, title, username, job_id, job_size)
                self.check_timer.start(3000)
                return

            elif result_code == ERROR_FAX_PROCESSING:
                # fax is being processed
                print "processing..."
                if self.waitdlg is None:
                    self.waitdlg = WaitForm(0, self.__tr("Processing fax..."), None, self, modal=1) # self.add_fax_canceled
                    self.waitdlg.show()

            # Check for updated FAB
            last_db_modification = self.db.last_modification_time()

            if last_db_modification > self.last_db_modification:
                QApplication.setOverrideCursor(QApplication.waitCursor)
                log.debug("FAB has been modified. Re-reading...")
                self.last_db_modification = last_db_modification

                self.UpdateIndividualList()
                self.UpdateGroupList()
                self.UpdateSelectionEdit()
                QApplication.restoreOverrideCursor()


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
            self.FailureUI(self.__tr("<b>Unable to communicate with device:</b><p>%1").arg(self.device_uri))

        try:
            self.StateText.setText(self.dev.status_desc)
        except AttributeError:
            pass            


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

                self.appPrintNoteLabel.setText(self.__tr("<i>You can also add items by printing documents from an application using the CUPS printer '%1'.</i>").arg(self.current_printer))

                break  
        else: # No CUPS queue for this device
            log.error("No CUPS queue found!")


    def refreshToolButton_clicked(self):
        self.UpdatePrinterStatus()

    def printerNameComboBox_highlighted(self, a0):
        self.current_printer = str(a0)
        self.UpdatePrinterInfo()

    # ************************************** Recepient handling
    def UpdateIndividualList(self):
        already_checked = []

        i = self.individualSendListView.firstChild()
        while i is not None:
            if i.isOn():
                already_checked.append(str(i.text(1)))

            i = i.itemBelow()

        self.individualSendListView.clear()

        all_entries = self.db.AllRecordEntries()

        if len(all_entries) > 0:

            for i in all_entries:
                j = QCheckListItem(self.individualSendListView, '', 
                                    QCheckListItem.CheckBox)

                j.setText(1, i.name)
                j.setText(2, i.fax)
                j.setText(3, i.notes)

                if i.name in already_checked:
                    j.setOn(True)


    def UpdateGroupList(self):
        already_checked = []

        i = self.groupSendListView.firstChild()
        while i is not None:
            if i.isOn():
                already_checked.append(str(i.text(1)))
            i = i.itemBelow()

        self.groupSendListView.clear()
        all_groups = self.db.AllGroups()

        for g in all_groups:
            j = QCheckListItem(self.groupSendListView, '', 
                               QCheckListItem.CheckBox)

            j.setText(1, g)
            j.setText(2, ', '.join(self.db.GroupEntries(g)))

            if g in already_checked:
                j.setOn(True)


    def CheckSendButtons(self):
        self.sendNowButton.setEnabled(bool(self.recipient_list and self.file_list))


    def addressBookButton_clicked(self):
        log.debug(self.cmd_fab)
        cmd = ''.join([self.dev.device_vars.get(x, x) \
                         for x in self.cmd_fab.split('%')])
        log.debug(cmd)

        path = cmd.split()[0]
        args = cmd.split()

        self.CleanupChildren()
        os.spawnvp(os.P_NOWAIT, path, args)        


    def CleanupChildren(self):
        log.debug("Cleaning up child processes.")
        try:
            os.waitpid(-1, os.WNOHANG)
        except OSError:
            pass


    def sendLaterButton_clicked(self):
        print "FaxSendJobForm.sendLaterButton_clicked(): Not implemented yet"

    def individualSendListView_clicked(self,a0):
        self.UpdateSelectionEdit()

    def groupSendListView_clicked(self,a0):
        self.UpdateSelectionEdit()


    def UpdateSelectionEdit(self):
        self.recipient_list = []
        i = self.groupSendListView.firstChild()
        while i is not None:
            if i.isOn():
                group = str(i.text(1))
                self.recipient_list.extend(self.db.GroupEntries(group))
            i = i.itemBelow()

        i = self.individualSendListView.firstChild()
        while i is not None:
            if i.isOn():
                self.recipient_list.append(str(i.text(1)))
            i = i.itemBelow()

        log.debug("List=%s" % self.recipient_list)
        self.recipient_list = utils.uniqueList(self.recipient_list)
        log.debug("Unique list=%s" % self.recipient_list)

        self.selectionEdit.setText(', '.join(self.recipient_list))
        self.CheckSendButtons()


    # ************************************** Send fax handling
    def sendNowButton_clicked(self):

        phone_num_list = []

        log.debug("Current printer=%s" % self.current_printer)
        ppd_file = cups.getPPD(self.current_printer)

        if ppd_file is not None and os.path.exists(ppd_file):
            if file(ppd_file, 'r').read().find('HP Fax') == -1:
                self.FailureUI(self.__tr("<b>Fax configuration error.</b><p>The CUPS fax queue for '%1' is incorrectly configured.<p>Please make sure that the CUPS fax queue is configured with the 'HPLIP Fax' Model/Driver.").arg(self.current_printer))
                return

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


        if self.dev.error_state > ERROR_STATE_MAX_OK:
            self.FailureUI(self.__tr("<b>Device is busy or in an error state (code=%1)</b><p>Please wait for the device to become idle or clear the error and try again.").arg(self.dev.status_code))
            return

        # Check to make sure queue in CUPS is idle
        self.cups_printers = cups.getPrinters()
        for p in self.cups_printers:
            if p.name == self.current_printer:
                if p.state == cups.IPP_PRINTER_STATE_STOPPED:
                    self.FailureUI(self.__tr("<b>The CUPS queue for '%1' is in a stopped or busy state.</b><p>Please check the queue and try again.").arg(self.current_printer))
                    return
                break

        log.debug("Recipient list:")

        for p in self.recipient_list:
            a = fax.AddressBookEntry(self.db.select(['name'], [p])[0])
            phone_num_list.append(a)
            log.debug("Name=%s Number=%s" % (a.name, a.fax))

        log.debug("File list:")


        for f in self.file_list:
            log.debug(str(f))

        self.busy = True

        service.sendEvent(self.sock, EVENT_START_FAX_JOB, device_uri=self.device_uri)

        if not self.dev.sendFaxes(phone_num_list, self.file_list, self.cover_page_message, 
                                  self.cover_page_re, self.cover_page_func, self.current_printer,
                                  self.update_queue, self.event_queue):

            self.FailureUI(self.__tr("<b>Send fax is active.</b><p>Please wait for operation to complete."))
            service.sendEvent(self.sock, EVENT_FAX_JOB_FAIL, device_uri=self.device_uri)
            self.busy = False
            return


        self.waitdlg = WaitForm(0, self.__tr("Initializing..."), self.send_fax_canceled, self, modal=1)
        self.waitdlg.show()

        self.send_fax_timer = QTimer(self, "SendFaxTimer")
        self.connect(self.send_fax_timer, SIGNAL('timeout()'), self.send_fax_timer_timeout)
        self.send_fax_timer.start(1000) # 1 sec UI updates


    def send_fax_canceled(self):
        self.event_queue.put((fax.EVENT_FAX_SEND_CANCELED, '', '', ''))
        service.sendEvent(self.sock, EVENT_FAX_JOB_CANCELED, device_uri=self.device_uri)


    def send_fax_timer_timeout(self):
        while self.update_queue.qsize():
            try:
                status, page_num, phone_num = self.update_queue.get(0)
            except Queue.Empty:
                break

            if status == fax.STATUS_IDLE:
                self.busy = False
                self.send_fax_timer.stop()

                if self.waitdlg is not None:
                    self.waitdlg.hide()
                    self.waitdlg.close()
                    self.waitdlg = None

            elif status == fax.STATUS_PROCESSING_FILES:
                self.waitdlg.setMessage(self.__tr("Processing page %1...").arg(page_num))

            elif status == fax.STATUS_DIALING:
                self.waitdlg.setMessage(self.__tr("Dialing %1...").arg(phone_num))

            elif status == fax.STATUS_CONNECTING:
                self.waitdlg.setMessage(self.__tr("Connecting to %1...").arg(phone_num))

            elif status == fax.STATUS_SENDING:
                self.waitdlg.setMessage(self.__tr("Sending page %1 to %2...").arg(page_num).arg(phone_num))

            elif status == fax.STATUS_CLEANUP:
                self.waitdlg.setMessage(self.__tr("Cleaning up..."))

            elif status in (fax.STATUS_ERROR, fax.STATUS_BUSY, fax.STATUS_COMPLETED):
                self.busy = False
                self.send_fax_timer.stop()

                if self.waitdlg is not None:
                    self.waitdlg.hide()
                    self.waitdlg.close()
                    self.waitdlg = None

                if status  == fax.STATUS_ERROR:
                    self.FailureUI(self.__tr("<b>Fax send error.</b><p>"))
                    service.sendEvent(self.sock, EVENT_FAX_JOB_FAIL, device_uri=self.device_uri)

                elif status == fax.STATUS_BUSY:
                    self.FailureUI(self.__tr("<b>Fax device is busy.</b><p>Please try again later."))
                    service.sendEvent(self.sock, EVENT_FAX_JOB_FAIL, device_uri=self.device_uri)

                elif status == fax.STATUS_COMPLETED:
                    self.SuccessUI()
                    service.sendEvent(self.sock, EVENT_END_FAX_JOB, device_uri=self.device_uri)

                    self.fileListView.clear()
                    del self.file_list[:]
                    self.UpdateFileList()
                    self.CheckSendButtons()

                    self.addCoverpagePushButton.setEnabled(coverpages_enabled)
                    self.editCoverpagePushButton.setEnabled(False)



    # ************************************** File and event handling
    def delFileButton_clicked(self):
        try:
            path = self.fileListView.currentItem().path
        except AttributeError:
            return
        else:
            temp = self.file_list[:]
            index = 0
            for p, t, d, x, g in temp:
                if p == path:
                    del self.file_list[index]

                    if t == 'application/hplip-fax-coverpage':
                        self.addCoverpagePushButton.setEnabled(coverpages_enabled)
                        self.editCoverpagePushButton.setEnabled(False)

                    self.UpdateFileList()
                    break

                index += 1

            self.CheckSendButtons()


    def addFilePushButton_clicked(self):
        self.processFile(self.filename, self.filename)
        self.CheckSendButtons()

    def upFileButton_clicked(self):
        try:
            path = self.fileListView.currentItem().path
        except AttributeError:
            return
        else:
            temp = self.file_list[:]
            index = 0
            for p, t, d, x, c in temp:
                if p == path:
                    self.file_list_move_up(p)
                    self.UpdateFileList(index-1)
                    break

                index += 1


    def downFileButton_clicked(self):
        try:
            path = self.fileListView.currentItem().path
        except AttributeError:
            return
        else:
            temp = self.file_list[:]
            index = 0
            for p, t, d, x, c in temp:
                if p == path:
                    self.file_list_move_down(p)
                    self.UpdateFileList(index+1)
                    break

                index += 1

    def file_list_move_up(self, p):
        for i in range(1, len(self.file_list)):
            if self.file_list[i][0] == p:
                self.file_list[i-1], self.file_list[i] = \
                    self.file_list[i], self.file_list[i-1]

    def file_list_move_down(self, p):
        for i in range(len(self.file_list)-2, -1, -1):
            if self.file_list[i][0] == p:
                self.file_list[i], self.file_list[i+1] = \
                    self.file_list[i+1], self.file_list[i]                 

    def fileEdit_textChanged(self,a0):
        self.filename = str(self.fileEdit.text())
        self.enableAddFileButton()

    def browsePushButton_clicked(self):
        self.filename = str(self.fileEdit.text())

        if self.filename and os.path.isdir(self.filename):
            d = self.filename
        else:
            d = os.path.expanduser("~")

        s = str(QFileDialog.getOpenFileName(d, self.__tr("All files (*)"), self,
                                              "openfile", self.caption()))

        if s and os.path.exists(s):
            self.fileEdit.setText(s)
            self.enableAddFileButton()


    def enableAddFileButton(self):
        self.addFilePushButton.setEnabled(bool(self.filename and
                                               os.path.exists(self.filename) and 
                                               os.path.isfile(self.filename)))

    def allowableTypesPushButton_clicked(self):
        x = {}
        for a in self.allowable_mime_types:
            x[a] = self.MIME_TYPES_DESC.get(a, ('Unknown', 'n/a'))

        log.debug(x)
        dlg = FaxAllowableTypesDlg(x, self)
        dlg.exec_loop()


    # Event handler for adding files from a external print job (not during fax send thread)
    def addFileFromJob(self, event, title, username, job_id=0, job_size=0):
        QApplication.setOverrideCursor(QApplication.waitCursor)
        self.busy = True

        try:
            if self.waitdlg is None:
                self.waitdlg = WaitForm(0, self.__tr("Receiving fax data..."), self.add_fax_canceled, self, modal=1)
                self.waitdlg.show()

            log.debug("Transfering job %d (%d bytes)" % (job_id, job_size))
            fax_dir = os.path.expanduser("~/hpfax")

            if not os.path.exists(fax_dir):
                os.mkdir(fax_dir)

            fax_file = os.path.expanduser(os.path.join(fax_dir, "hpfax-%d.g3" % job_id))
            fd = file(fax_file, 'w')
            bytes_read = 0
            header_read = False
            total_pages = 0

            #if self.waitdlg is not None:
            #    self.waitdlg.setMessage(self.__tr("Receiving fax data..."))

            while True:
                qApp.processEvents()
                log.debug("Transfering fax data...")

                fields, data, result_code = \
                    msg.xmitMessage(self.sock, "FaxGetData", None,
                                         {"username": username,
                                          "job-id": job_id,
                                         })

                log.debug(repr(data)), len(data)

                if data and result_code == ERROR_SUCCESS:
                    fd.write(data)
                    bytes_read += len(data)

                    self.waitdlg.setMessage(self.__tr("Read %1 of fax data...").arg(utils.format_bytes(bytes_read)))

                    if not header_read and len(data) >= fax.FILE_HEADER_SIZE:
                        mg, version, total_pages, hort_dpi, vert_dpi, page_size, \
                            resolution, encoding, reserved1, reserved2 = \
                            struct.unpack(">8sBIHHBBBII", data[:fax.FILE_HEADER_SIZE])

                        log.debug("Magic=%s Ver=%d Pages=%d hDPI=%d vDPI=%d Size=%d Res=%d Enc=%d" %
                                  (mg, version, total_pages, hort_dpi, vert_dpi, page_size, resolution, encoding))

                        header_read = True

                else:
                    break # Done

            fd.close()

            if self.waitdlg is not None:
                self.waitdlg.hide()
                self.waitdlg.close()
                self.waitdlg = None

            log.debug("Transfered %d bytes" % bytes_read)

            if total_pages > 0:
                mime_type = job_types.get(job_id, "application/hplip-fax")
                mime_type_desc = self.MIME_TYPES_DESC.get(mime_type, ('Unknown', 'n/a'))[0]
                log.debug("%s (%s)" % (mime_type, mime_type_desc))
                self.file_list.append((fax_file, mime_type, mime_type_desc, title, total_pages))
            else:
                self.FailureUI("<b>Render Failure:</b><p>Rendered document contains no data.")

            self.UpdateFileList()
            self.document_num += 1
            self.fileEdit.setText("")
            self.CheckSendButtons()

        finally:
            self.busy = False
            QApplication.restoreOverrideCursor()


    def add_fax_canceled(self):
        pass

    # **************************************

    def addFile(self, path, title, mime_type, mime_type_desc, pages):
        self.file_list.append((path, mime_type, mime_type_desc, title, pages))

        self.UpdateFileList()
        self.document_num += 1
        self.fileEdit.setText("")
        self.CheckSendButtons()

    def decode_fax_header(self, header):
        try:
            return struct.unpack(">8sBIHHBBBII", header)
        except struct.error:
            return -1, -1, -1, -1, -1, -1, -1, -1, -1, -1


    def processFile(self, path, title): # Process an arbitrary file ("Add file...")
        path = os.path.realpath(path)

        if os.path.exists(path):
            mime_type = magic.mime_type(path)
            log.debug(mime_type)
            mime_type_desc = mime_type

            log.debug(mime_type)

            if mime_type == 'application/hplip-fax':
                mime_type_desc = self.MIME_TYPES_DESC[mime_type][0]


                fax_file_fd = file(path, 'r')
                header = fax_file_fd.read(fax.FILE_HEADER_SIZE)

                mg, version, pages, hort_dpi, vert_dpi, page_size, \
                    resolution, encoding, reserved1, reserved2 = self.decode_fax_header(header)

                if mg != 'hplip_g3':
                    log.error("Invalid file header. Bad magic.")
                    self.WarningUI(self.__tr("<b>Invalid HPLIP Fax file.</b><p>Bad magic!"))
                    return

                self.addFile(path, title, mime_type, mime_type_desc, pages)
            else:
                log.debug(repr(mime_type))
                try:
                    mime_type_desc = self.MIME_TYPES_DESC[mime_type][0]
                except KeyError:
                    self.WarningUI(self.__tr("<b>You are trying to add a file that cannot be directly faxed with this utility.</b><p>To print this file, use the print command in the application that created it."))
                    return
                else:
                    log.debug("Adding file: title='%s' file=%s mime_type=%s mime_desc=%s)" % (title, path, mime_type, mime_type_desc))

                    all_pages = True 
                    page_range = ''
                    page_set = 0
                    nup = 1

                    cups.resetOptions()

                    if mime_type in ["application/x-cshell",
                                     "application/x-perl",
                                     "application/x-python",
                                     "application/x-shell",
                                     "text/plain",] and self.prettyprint:

                        cups.addOption('prettyprint')

                    if nup > 1:
                        cups.addOption('number-up=%d' % nup)

                    cups.addOption('scaling=100')

                    self.cups_printers = cups.getPrinters()

                    printer_state = cups.IPP_PRINTER_STATE_STOPPED
                    for p in self.cups_printers:
                        if p.name == self.current_printer:
                            printer_state = p.state

                    log.debug("Printer state = %d" % printer_state)

                    if printer_state == cups.IPP_PRINTER_STATE_IDLE:
                        sent_job_id = cups.printFile(self.current_printer, path, os.path.basename(path))
                        job_types[sent_job_id] = mime_type # save for later
                        log.debug("Job ID=%d" % sent_job_id)  

                        QApplication.setOverrideCursor(QApplication.waitCursor)

                        self.waitdlg = WaitForm(0, self.__tr("Processing fax file..."), None, self, modal=1) # self.add_fax_canceled
                        self.waitdlg.show()

                    else:
                        self.FailureUI(self.__tr("<b>Printer '%1' is in a stopped or error state.</b><p>Check the printer queue in CUPS and try again.").arg(self.current_printer))
                        cups.resetOptions()
                        return

                    cups.resetOptions()
                    QApplication.restoreOverrideCursor()

        else:
            self.FailureUI(self.__tr("<b>Unable to add file '%1' to file list.</b><p>Check the file name and try again.".arg(path)))


    def UpdateFileList(self, j=0):
        self.fileListView.clear()
        temp = self.file_list[:]
        temp.reverse()

        total_pages = 0

        if j<0: j=0
        if j>len(temp)-1: j=len(temp)-1

        k, selected = len(temp)-1, False
        for path, mime_type, mime_type_desc, title, pages in temp:

            if pages == 0:
                str_pages = '?'
            else:
                str_pages = str(pages)

            i = FileListViewItem(self.fileListView, title, mime_type_desc, path, str_pages)
            total_pages += pages

            if k == j and not selected:
                self.fileListView.setCurrentItem(i)
                selected = True

            k -= 1

        self.fileListView.setColumnText(2, self.__tr("Pages (Total=%1)").arg(total_pages))

        self.delFileButton.setEnabled(self.fileListView.childCount() > 0)
        self.upFileButton.setEnabled(self.fileListView.childCount() > 1)
        self.downFileButton.setEnabled(self.fileListView.childCount() > 1)


    # ************************************** Coverpages

    def showCoverPageDlg(self):
        dlg = CoverpageForm(self.cover_page_name, self)
        dlg = CoverpageForm(self.cover_page_name, self)
        dlg.messageTextEdit.setText(self.cover_page_message)
        dlg.regardingTextEdit.setText(self.cover_page_re)

        if dlg.exec_loop() == QDialog.Accepted:

            self.cover_page_func, cover_page_png = dlg.data
            self.cover_page_message = str(dlg.messageTextEdit.text())
            self.cover_page_re = str(dlg.regardingTextEdit.text())
            self.cover_page_name = dlg.coverpage_name
            return True

        return False

    def addCoverpagePushButton_clicked(self):
        if self.showCoverPageDlg():
            self.file_list.insert(0, ('coverpage', "application/hplip-fax-coverpage", 
                self.__tr("HP Fax Coverpage"), self.__tr("Cover Page"), 1))

            self.UpdateFileList()
            self.document_num += 1
            self.CheckSendButtons()

            self.addCoverpagePushButton.setEnabled(False)
            self.editCoverpagePushButton.setEnabled(True)

    def editCoverpagePushButton_clicked(self):
        self.showCoverPageDlg()


    # ************************************** Misc

    def closeEvent(self, event):
        if self.dev is not None and self.dev.isSendFaxActive():
            self.FailureUI(self.__tr("<b>Send fax is active.</b><p>Please wait for operation to complete."))
        else:
            event.accept()


    def settingsPushButton_clicked(self):
        try:
            self.dev.open()

            try:
                result_code, fax_num = self.dev.getPML(pml.OID_FAX_LOCAL_PHONE_NUM)
            except Error:
                log.error("PML failure.")
                self.FailureUI(self.__tr("<p><b>Operation failed. Device busy.</b>"))
                return

            fax_num = str(fax_num)

            try:
                result_code, name = self.dev.getPML(pml.OID_FAX_STATION_NAME)
            except Error:
                log.error("PML failure.")
                self.FailureUI(self.__tr("<p><b>Operation failed. Device busy.</b>"))
                return

            name = str(name)

            dlg = FaxSettingsForm(self.dev, fax_num, name, self)
            dlg.exec_loop()

        finally:
            self.dev.close()


    def checkBoxPrettyPrinting_toggled(self,a0):
        self.prettyprint = bool(a0)


    def SuccessUI(self):
        QMessageBox.information(self,
                             self.caption(),
                             self.__tr("<p><b>Fax send completed successfully.</b>"),
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
        return qApp.translate("FaxSendJobForm", s, c)

    def __trUtf8(self,s,c = None):
        return qApp.translate("FaxSendJobForm", s, c, QApplication.UnicodeUTF8)
