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

from base.g import *
from base import utils, device, msg
from prnt import cups
from pcard import photocard

import sys
import os, os.path
import socket

from qt import *
from unloadform_base import UnloadForm_base
from imagepropertiesdlg import ImagePropertiesDlg

progress_dlg = None

class IconViewItem(QIconViewItem):
    def __init__(self, parent, dirname, fname, path, pixmap, mime_type, mime_subtype, size, exif_info={}):
        QIconViewItem.__init__(self, parent, fname, pixmap)
        self.mime_type = mime_type
        self.mime_subtype = mime_subtype
        self.path = path
        self.dirname = dirname
        self.filename = fname
        self.exif_info = exif_info
        self.size = size
        self.thumbnail_set = False


class UnloadForm(UnloadForm_base):
    def __init__(self, bus='usb,par', device_uri=None, printer_name=None,
                 parent=None, name=None, fl=0):

        UnloadForm_base.__init__(self,parent,name,fl)
        self.pc = None
        self.device_uri = device_uri
        self.printer_name = printer_name
        self.init_failed = False

        icon = QPixmap(os.path.join(prop.image_dir, 'HPmenu.png'))
        self.setIcon(icon)

        if self.device_uri and self.printer_name:
            log.error("You may not specify both a printer (-p) and a device (-d).")
            self.device_uri, self.printer_name = None, None

        if not self.device_uri and not self.printer_name:
            probed_devices = device.probeDevices(None, bus=bus, filter='pcard')
            cups_printers = cups.getPrinters()
            log.debug(probed_devices)
            log.debug(cups_printers)
            max_deviceid_size, x, devices = 0, 0, {}

            for d in probed_devices:
                if d.startswith('hp:'):
                    printers = []
                    for p in cups_printers:
                        if p.device_uri == d:
                            printers.append(p.name)
                    devices[x] = (d, printers)
                    x += 1
                    max_deviceid_size = max(len(d), max_deviceid_size)

            if x == 0:
                from nodevicesform import NoDevicesForm
                self.failure(self.__tr("<p><b>No devices found that support photo card access.</b><p>Please make sure your device is properly installed and try again."))
                self.init_failed = True

            elif x == 1:
                log.info(utils.bold("Using device: %s" % devices[0][0]))
                self.device_uri = devices[0][0]

            else:
                from choosedevicedlg import ChooseDeviceDlg
                dlg = ChooseDeviceDlg(devices)
                if dlg.exec_loop() == QDialog.Accepted:
                    self.device_uri = dlg.device_uri
                else:
                    self.init_failed = True

        QTimer.singleShot(0, self.initialUpdate)


    def initialUpdate(self):
        if self.init_failed:
            self.cleanup(EVENT_PCARD_UNABLE_TO_MOUNT)
            return

        QApplication.setOverrideCursor(QApplication.waitCursor)

        try:
            self.pc = photocard.PhotoCard(None, self.device_uri, self.printer_name)
        except Error, e:
            log.error("An error occured: %s" % e[0])
            self.failure(self.__tr("<p><b>Unable to mount photocard.</b><p>Could not connect to device."))
            self.cleanup(EVENT_PCARD_UNABLE_TO_MOUNT)
            return

        if self.pc.device.device_uri is None and self.printer_name:
            log.error("Printer '%s' not found." % self.printer_name)
            self.failure(self.__tr("<p><b>Unable to mount photocard.</b><p>Device not found."))
            self.cleanup(EVENT_PCARD_JOB_FAIL)
            return

        if self.pc.device.device_uri is None and self.device_uri:
            log.error("Malformed/invalid device-uri: %s" % self.device_uri)
            self.failure(self.__tr("<p><b>Unable to mount photocard.</b><p>Malformed/invalid device-uri."))
            self.cleanup(EVENT_PCARD_JOB_FAIL)
            return

        try:
            self.pc.mount()
        except Error:
            log.error("Unable to mount photo card on device. Check that device is powered on and photo card is correctly inserted.")
            self.failure(self.__tr("<p><b>Unable to mount photocard.</b><p>Check that device is powered on and photo card is correctly inserted."))
            self.pc.umount()
            self.cleanup(EVENT_PCARD_UNABLE_TO_MOUNT)
            return

        self.device_uri = self.pc.device.device_uri
        user_cfg.last_used.device_uri = self.device_uri

        self.pc.device.sendEvent(EVENT_START_PCARD_JOB)

        disk_info = self.pc.info()
        self.pc.write_protect = disk_info[8]

        if self.pc.write_protect:
            log.warning("Photo card is write protected.")

        log.info("Photocard on device %s mounted" % self.pc.device_uri)

        if not self.pc.write_protect:
            log.info("DO NOT REMOVE PHOTO CARD UNTIL YOU EXIT THIS PROGRAM")

        self.unload_dir = os.path.normpath(os.path.expanduser('~'))
        os.chdir(self.unload_dir)
        self.UnloadDirectoryEdit.setText(self.unload_dir)

        self.unload_list = self.pc.get_unload_list()
        self.DeviceText.setText(self.pc.device.device_uri)

        self.image_icon_map = {'tiff' : 'tif.png',
                                'bmp'  : 'bmp.png',
                                'jpeg' : 'jpg.png',
                                'gif'  : 'gif.png',
                                'unknown' : 'unknown.png',
                                }
        self.video_icon_map = {'unknown' : 'movie.png',
                                'mpeg'    : 'mpg.png',
                                }

        self.total_number = 0
        self.total_size = 0

        self.removal_option = 0

        self.UpdateStatusBar()

        if self.pc.write_protect:
            self.FileRemovalGroup.setEnabled(False)
            self.LeaveAllRadio.setEnabled(False)
            self.RemoveSelectedRadio.setEnabled(False)

        # Item map disambiguates between files of the same
        # name that are on the pcard in more than one location
        self.item_map = {}

        QApplication.restoreOverrideCursor()

        self.display_update_timer = QTimer(self, "DisplayUpdateTimer")
        self.connect(self.display_update_timer, SIGNAL('timeout()'), self.DisplayUpdate)

        self.display_update_timer.start(1000)
        self.busy = False

        self.load_icon_view(first_load=True)

    def closeEvent(self, event):
        if self.pc is not None:
            self.pc.device.sendEvent(EVENT_END_PCARD_JOB)

        event.accept()


    def CancelButton_clicked(self):
        self.cleanup()


    def cleanup(self, error=0):
        if self.pc is not None:
            if error > 0:
                self.pc.device.sendEvent(error, typ='error')

        self.close()


    def success(self):
        QMessageBox.information(self,
                             self.caption(),
                             self.__tr("<p><b>The operation completed successfully.</b>"),
                              QMessageBox.Ok,
                              QMessageBox.NoButton,
                              QMessageBox.NoButton)

    def failure(self, error_text):
        QMessageBox.critical(self,
                             self.caption(),
                             error_text,
                              QMessageBox.Ok,
                              QMessageBox.NoButton,
                              QMessageBox.NoButton)


    def load_icon_view(self, first_load):
        QApplication.setOverrideCursor(QApplication.waitCursor)
        self.busy = True
        self.first_load = first_load

        if first_load:
            self.IconView.clear()

        self.num_items = len(self.unload_list)

        self.pb = QProgressBar()
        self.pb.setTotalSteps(self.num_items)
        self.statusBar().addWidget(self.pb)
        self.pb.show()

        self.item_num = 0

        self.load_timer = QTimer(self, "ScanTimer")
        self.connect(self.load_timer, SIGNAL('timeout()'), self.continue_load_icon_view)
        self.load_timer.start(0)

    def continue_load_icon_view(self):

        if self.item_num == self.num_items:
            self.load_timer.stop()
            self.disconnect(self.load_timer, SIGNAL('timeout()'), self.continue_load_icon_view)
            self.load_timer = None
            del self.load_timer

            self.pb.hide()
            self.statusBar().removeWidget(self.pb)

            self.IconView.adjustItems()
            self.busy = False
            QApplication.restoreOverrideCursor()
            return

        f = self.unload_list[self.item_num]

        self.item_num += 1
        path, size = f[0], f[1]

        self.pb.setProgress(self.item_num)

        typ, subtyp = self.pc.classify_file(path).split('/')

        if not self.first_load and typ == 'image' and subtyp == 'jpeg':

            exif_info = self.pc.get_exif_path(path)

            if len(exif_info) > 0:

                if 'JPEGThumbnail' in exif_info:
                    pixmap = QPixmap()
                    pixmap.loadFromData(exif_info['JPEGThumbnail'], "JPEG")

                    self.resizePixmap(pixmap)

                    del exif_info['JPEGThumbnail']
                    dname, fname=os.path.split(path)
                    x = self.item_map[fname]

                    if len(x) == 1:
                        item = self.IconView.findItem(fname, 0)
                    else:
                        i = x.index(path)
                        if i == 0:
                            item = self.IconView.findItem(fname, 0)
                        else:
                            item = self.IconView.findItem(fname + " (%d)" % (i+1), 0)

                    if item is not None:
                        item.setPixmap(pixmap)
                        item.thumbnail_set = True

                    return

                #elif 'TIFFThumbnail' in exif_info:
                    # can't handle TIFF in Qt?
                #    del exif_info['TIFFThumbnail']
                #    if first_load:
                #        IconViewItem( self.IconView, filename,
                #                      QPixmap( os.path.join( prop.image_dir, 'tif.png' ) ),
                #                      typ, subtyp, size, exif_info )
                #    else:
                #        pass

                #    continue


        elif self.first_load:
            if typ == 'image':
                f = os.path.join(prop.image_dir, self.image_icon_map.get(subtyp, 'unknown.png'))
            elif typ == 'video':
                f = os.path.join(prop.image_dir, self.video_icon_map.get(subtyp, 'movie.png'))
            elif typ == 'audio':
                f = os.path.join(prop.image_dir, 'sound.png')
            else:
                f = os.path.join(prop.image_dir, 'unknown.png')

            dirname, fname=os.path.split(path)
            num = 1
            try:
                self.item_map[fname]
            except:
                self.item_map[fname] = [path]
            else:
                self.item_map[fname].append(path)
                num = len(self.item_map[fname])

            if num == 1:
                IconViewItem(self.IconView, dirname, fname, path, QPixmap(f),
                              typ, subtyp, size)
            else:
                IconViewItem(self.IconView, dirname, fname + " (%d)" % num,
                              path, QPixmap(f), typ, subtyp, size)


    def resizePixmap(self, pixmap):
        w, h = pixmap.width(), pixmap.height()

        if h > 128 or w > 128:
            ww, hh = w - 128, h - 128
            if ww >= hh:
                pixmap.resize(128, int(float((w-ww))/w*h))
            else:
                pixmap.resize(int(float((h-hh))/h*w), 128)



    def UpdateStatusBar(self):
        if self.total_number == 0:
            self.statusBar().message(self.__tr("No files selected"))
        elif self.total_number == 1:
            self.statusBar().message(self.__tr("1 file selected, %s" % utils.format_bytes(self.total_size, True)))
        else:
            self.statusBar().message(self.__tr("%d files selected, %s" % (self.total_number, utils.format_bytes(self.total_size, True))))

    def SelectAllButton_clicked(self):
        self.IconView.selectAll(1)

    def SelectNoneButton_clicked(self):
        self.IconView.selectAll(0)

    def IconView_doubleClicked(self, a0):
        #self.Display( a0 )
        pass

    def UnloadDirectoryBrowseButton_clicked(self):
        old_dir = self.unload_dir
        self.unload_dir = unicode(QFileDialog.getExistingDirectory(self.unload_dir, self))

        if not len(self.unload_dir):
            return
        elif not utils.is_path_writable(self.unload_dir):
            self.failure(self.__tr("<p><b>The unload directory path you entered is not valid.</b><p>The directory must exist and you must have write permissions."))
            self.unload_dir = old_dir
        else:
            self.UnloadDirectoryEdit.setText(self.unload_dir)
            os.chdir(self.unload_dir)

    def UnloadButton_clicked(self):
        was_cancelled = False
        self.busy = True
        self.unload_dir = unicode(self.UnloadDirectoryEdit.text())
        dir_error = False

        try:
            try:
                os.chdir(self.unload_dir)
            except OSError:
                log.error("Directory not found: %s" % self.unload_dir)
                dir_error = True

            if dir_error or not utils.is_path_writable(self.unload_dir):
                self.failure(self.__tr("<p><b>The unload directory path is not valid.</b><p>Please enter a new path and try again."))
                return

            unload_list = []
            i = self.IconView.firstItem()
            total_size = 0
            while i is not None:

                if i.isSelected():
                    unload_list.append((i.path, i.size, i.mime_type, i.mime_subtype))
                    total_size += i.size
                i = i.nextItem()

            if total_size == 0:
                self.failure(self.__tr("<p><b>No files are selected to unload.</b><p>Please select one or more files to unload and try again."))
                return

            global progress_dlg
            progress_dlg = QProgressDialog(self.__tr("Unloading Files..."), self.__tr("Cancel"),
                                           total_size, self, 'progress', True)
            progress_dlg.setMinimumDuration(0)
            progress_dlg.show()

            if self.removal_option == 0:
                total_size, total_time, was_cancelled = \
                    self.pc.unload(unload_list, self.UpdateUnloadProgressDlg, None, True)

            elif self.removal_option == 1: # remove selected
                total_size, total_time, was_cancelled = \
                    self.pc.unload(unload_list, self.UpdateUnloadProgressDlg, None, False)

            else: # remove all
                total_size, total_time, was_cancelled = \
                    self.pc.unload(unload_list, self.UpdateUnloadProgressDlg, None, False)
                # TODO: Remove remainder of files

            progress_dlg.close()

            self.pc.device.sendEvent(EVENT_PCARD_FILES_TRANSFERED)

            if self.removal_option != 0: # remove selected or remove all
                self.unload_list = self.pc.get_unload_list()
                self.total_number = 0
                self.total_size = 0
                self.item_map = {}
                self.load_icon_view(first_load=True)

            if was_cancelled:
                self.failure(self.__tr("<b>Unload cancelled at user request.</b>"))
            else:
                self.success()

        finally:
            self.busy = False


    def UpdateUnloadProgressDlg(self, src, trg, size):
        global progress_dlg
        progress_dlg.setProgress(progress_dlg.progress() + size)
        progress_dlg.setLabelText(src)
        qApp.processEvents()

        return progress_dlg.wasCancelled()

    def IconView_rightButtonClicked(self, item, pos):
        popup = QPopupMenu(self)
        popup.insertItem("Properties", self.PopupProperties)

        if item is not None and \
            item.mime_type == 'image' and \
            item.mime_subtype == 'jpeg' and \
            self.pc.get_exif_path(item.path) and \
            not item.thumbnail_set:

            popup.insertItem("Show Thumbnail", self.showThumbNail)
        popup.popup(pos)


    def PopupDisplay(self):
        self.Display(self.IconView.currentItem())

    def PopupProperties(self):
        self.Properties(self.IconView.currentItem())

    def showThumbNail(self):
        item = self.IconView.currentItem()
        exif_info = self.pc.get_exif_path(item.path)

        if len(exif_info) > 0:
            if 'JPEGThumbnail' in exif_info:
                pixmap = QPixmap()
                pixmap.loadFromData(exif_info['JPEGThumbnail'], "JPEG")
                self.resizePixmap(pixmap)
                del exif_info['JPEGThumbnail']
                item.setPixmap(pixmap)

                self.IconView.adjustItems()

        else:
            self.failure(self.__tr("<p><b>No thumbnail found in image.</b>"))

        item.thumbnail_set = True

    def Display(self, item):
        pass
        # cp over file (does this even make sense to do this at this point?)
        # display with imagemagick?

    def Properties(self, item):
        if item is not None:
            if not item.exif_info:
                item.exif_info = self.pc.get_exif_path(item.path)

            ImagePropertiesDlg(item.filename, item.dirname,
                                '/'.join([item.mime_type, item.mime_subtype]),
                                utils.format_bytes(item.size, True),
                                item.exif_info, self).exec_loop()


    def IconView_selectionChanged(self):
        pass


    def DisplayUpdate(self):
        if not self.busy:
            self.total_number = 0
            self.total_size = 0
            i = self.IconView.firstItem()

            while i is not None:

                if i.isSelected():
                    self.total_number += 1
                    self.total_size += i.size

                i = i.nextItem()

            self.UpdateStatusBar()


    def IconView_clicked(self,a0,a1):
        pass

    def IconView_clicked(self,a0):
        pass

    def IconView_currentChanged(self,a0):
        pass

    def FileRemovalGroup_clicked(self, a0):
        self.removal_option = a0

    def ShowThumbnailsButton_clicked(self):
        self.ShowThumbnailsButton.setEnabled(False)
        self.load_icon_view(first_load=False)


    def __tr(self,s,c = None):
        return qApp.translate("UnloadForm",s,c)



