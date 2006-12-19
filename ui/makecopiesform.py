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

import os, Queue

from base.g import *
from prnt import cups, printable_areas
from base import device, utils, pml, service
from copier import copier

from qt import *
from makecopiesform_base import MakeCopiesForm_base
from waitform import WaitForm


##try:
##    import Image
##    import PSDraw
##except ImportError:
##    imaging_avail = False
##else:
##    imaging_avail = True
##    
##import scanext

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
                #x = []
                #for z in self.cups_printers:
                #    if z.device_uri in probed_devices:
                #        x.append(z)
                
                from choosedevicedlg import ChooseDeviceDlg
                #dlg = ChoosePrinterDlg(self.cups_printers, ['hp'])
                #dlg = ChoosePrinterDlg(x, ['hp'])
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
        
##        if not imaging_avail:
##            self.FailureUI(self.__tr("<b>The PIL (Python Imaging Library) is not installed.</b><p>Make copies requires that the PIL be installed. Please install the PIL and try again."))
##            self.close()
##            return
        
        self.printer_list = []

##        self.dev = device.Device(device_uri=self.device_uri, 
##                                 printer_name=self.printer_name, 
##                                 hpssd_sock=self.sock)

        self.dev = copier.PMLCopyDevice(device_uri=self.device_uri, 
                                        printer_name=self.printer_name, 
                                        hpssd_sock=self.sock)

        if self.dev.copy_type == COPY_TYPE_NONE:
            self.FailureUI(self.__tr("<b>Sorry, make copies functionality is not implemented for this device.</b>"))
            self.close()
            return
            
        self.scan_style = self.dev.mq.get('scan-style', SCAN_STYLE_FLATBED)
        self.copy_type = self.dev.mq.get('copy-type', COPY_TYPE_DEVICE)
        
        #log.debug(self.scan_style)
        
        if self.scan_style == SCAN_STYLE_SCROLLFED:
            self.fitToPageCheckBox.setEnabled(False)
            self.fit_to_page = pml.COPIER_FIT_TO_PAGE_DISABLED
        
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
                
            
        
    def EventUI(self, event_code, event_type, error_string_short,
                error_string_long, retry_timeout, job_id,
                device_uri):

        log.debug("Event: device_uri=%s code=%d type=%s string=%s timeout=%d id=%d uri=%s" %
                 (device_uri, event_code, event_type,  
                  error_string_short, retry_timeout, job_id, device_uri))

        if device_uri == self.dev.device_uri:
            self.StateText.setText(error_string_short)
        

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

                #cups.openPPD(p.name)
                #self.UpdateDuplex()
                #cups.closePPD()
                break
        
        
    #def callback(self, x, y):
    #    update_spinner()
    
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
                
        
        
        
##        log.debug(scanext.init())
##        
##        try:
##            scanner = scanext.open(self.device_uri.replace('hp:/', 'hpaio:/'))
##        except scanext.error, e:
##            log.error(e)
##            self.FailureUI(e)
##            return
##        
##        try:
##            #if 1:
##            tech_class = self.dev.tech_class
##            print tech_class
##            
##            paper_data = None
##            
##            
##            #return
##            
##            scanner.mode = 'Color'
##            scanner.compression = "JPEG"
##            scanner.jpeg_compression_factor = 10
##            scanner.brightness = 10
##            dpi = 300
##            scanner.resolution = dpi
##            
##            cups.openPPD(self.current_printer)
##            
##            page_name, page_width_pt, page_height_pt, page_left_pt, page_bottom_pt, page_right_pt, page_top_pt = \
##                cups.getPPDPageSize()
##                
##            print "Page size (PPD)(pt)=", page_name, page_width_pt, page_height_pt, page_left_pt, page_bottom_pt, page_right_pt, page_top_pt
##            cups.closePPD()
##
##            #return
##            try:
##                paper_data_set = printable_areas.data[tech_class]
##            except KeyError:
##                # Hack to handle DJGenericVIP vs. GenericVIP issue
##                paper_data_set = printable_areas.data.get(tech_class.replace("DJ", ""), None)
##
##            #print paper_data_set
##            
##            try:
##                paper_data = paper_data_set[page_name]
##            except:
##                page_name = page_name.title()
##                paper_data = paper_data_set.get(page_name, (8.5000, 11.0000, 0.1250, 0.1250, 8.2500, 10.3750))
##                
##            print paper_data
##            
##            #                                          W     H     L    B     R     T
##            # Page size (PPD)(pt)=             Letter 612.0 792.0 18.0 36.0  594.0 783.0
##            # Page size (printable_areas)(pt)= Letter 612.0 792.0  9.0 36.0   9.0   9.0
##            
##            media_width_in, media_height_in, page_left_in, page_top_in, page_width_in, page_height_in = paper_data
##            
##            
##            page_right_in = media_width_in - (page_left_in + page_width_in)
##            page_bottom_in = media_height_in - (page_top_in + page_height_in)
##            
##            page_left_pt = page_left_in * 72.0
##            page_right_pt = page_right_in * 72.0
##            page_bottom_pt = page_bottom_in * 72.0
##            page_top_pt = page_top_in * 72.0
##            
##            print "Page size (printable_areas)(pt)=", page_name, page_width_pt, page_height_pt, page_left_pt, page_bottom_pt, page_right_pt, page_top_pt
##            
##            (mode, last_frame, (scan_width_px, scan_height_px), depth, bytes_per_line) = \
##                scanner.get_parameters()
##            
##            #print params
##            #log.debug(params)
##            print "Scan (px)=", mode, last_frame, scan_width_px, scan_height_px, depth, bytes_per_line
##            
##            scanner.start()
##            
##            im = scanner.snap(callback=self.callback)
##            #im.save("test.jpg")
##            print
##            print im.size
##            print im.mode
##            print im.format
##            #print im.info
##            
##            page_left_px = page_left_pt / 72.0 * dpi
##            page_right_px = page_right_pt / 72.0 * dpi
##            page_top_px = page_top_pt / 72.0 * dpi
##            page_bottom_px = page_bottom_pt / 72.0 * dpi
##            page_width_px = (page_right_pt - page_left_pt) / 72.0 * dpi # px
##            page_height_px = (page_top_pt - page_bottom_pt) / 72.0 * dpi # px
##            
##            print "Page (px) =", page_width_px, page_height_px, page_left_px, page_top_px, page_right_px, page_bottom_px
##            
##            print_width_px = page_right_px - page_left_px
##            print_height_px = page_top_px - page_bottom_px
##            
##            print "Print (px) =", print_width_px, print_height_px
##            
##            #cropped_im = im.crop((0, 0, int(width), int(height))) # left, top, right, bottom 
##            cropped_im = im.crop((int(page_left_px), int(page_bottom_px), int(print_width_px), int(print_height_px)))
##            cropped_im.load()
##            print cropped_im.size
##            cropped_im.save("test.jpg", "JPEG")
##
##            if print_width_px > print_height_px:
##                scale = 256.0/print_width_px
##                thumb_xsize = 256
##                thumb_ysize = int(print_height_px * scale)
##            else:
##                scale = 256.0/print_height_px
##                thumb_ysize = 256
##                thumb_xsize = int(print_width_px * scale)
##                
##            print thumb_xsize, thumb_ysize
##            
##            thumb = cropped_im.copy()
##            thumb.thumbnail((thumb_xsize, thumb_ysize), Image.ANTIALIAS)
##            
##            #image = QImage()
##            pixmap = QPixmap()
##            s = thumb.convert("RGB").tostring("jpeg", "RGB")
##            pixmap.loadFromData(QByteArray(s))
##            
##            self.thumbnailPixmap.setPixmap(pixmap)
##            
##            
##            
##            #import cStringIO
##            
##            #temp_file_fd = cStringIO.StringIO()
##            #temp_file_fd, temp_file_name = utils.make_temp_file()
##            #fd = file("test.ps", "w")
##            
##            #ps = PSDraw.PSDraw(fd)
##    
##            #ps.begin_document()
##            #ps.setfont("Helvetica-Narrow-Bold", 18)
##            #ps.text((letter[0], letter[3]+24), title)
##            #ps.setfont("Helvetica-Narrow-Bold", 8)
##            #ps.text((letter[0], letter[1]-30), VERSION)
##            #letter = ( 1.0*72, 1.0*72, 7.5*72, 10.0*72 )
##            #letter = (0.0, 0.0, 8.5*72, 11.0*72)
##            
##            #ps.image(letter, im, dpi=dpi)
##            #ps.end_document()
##            
##            #fd.close()
##            
##
##            #sys.exit(0)
##            #return
##            
##            cups.resetOptions()
##            cups.addOption('ppi=%d' % dpi)
##            cups.addOption('scaling=%d' % 100)
##            
##            self.cups_printers = cups.getPrinters()
##            #log.debug(self.cups_printers)
##            
##            printer_state = cups.IPP_PRINTER_STATE_STOPPED
##            for p in self.cups_printers:
##                if p.name == self.current_printer:
##                    printer_state = p.state
##                    
##            log.debug("Printer state = %d" % printer_state)
##            
##            if printer_state == cups.IPP_PRINTER_STATE_IDLE:
##                sent_job_id = cups.printFile(self.current_printer, "test.jpg", "test.jpg")
##                #job_types[sent_job_id] = mime_type # save for later
##                log.debug("Job ID=%d" % sent_job_id)  
##
##                #QApplication.setOverrideCursor(QApplication.waitCursor)
##
##                #self.waitdlg = WaitForm(0, self.__tr("Processing fax file..."), None, self, modal=1)
##                #self.waitdlg.show()
##              
##            else:
##                self.FailureUI(self.__tr("<b>Printer '%1' is in a stopped or error state.</b><p>Check the printer queue in CUPS and try again.").arg(self.current_printer))
##                cups.resetOptions()
##                return
##                
##            cups.resetOptions()            
##            
##            #self.dev.printFile("test.jpg", direct=False, raw=False, remove=False)
##            #self.dev.printFile("test.ps", direct=False, raw=False, remove=False)
##            #self.dev.printData(self, temp_file_fd.getvalue(), direct=False, raw=False)
##            #self.dev.printData(temp_file_fd.getvalue(), direct=False, raw=False)
##            
##        
##        finally:
##            scanner.close()
##            del scanner
##            scanext.exit()
    
    
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
