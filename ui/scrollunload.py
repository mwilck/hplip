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
from base import utils, magic
from pcard import photocard

# Qt
from qt import *
from scrollview import ScrollView, PixmapLabelButton
from imagepropertiesdlg import ImagePropertiesDlg

# Std Lib
import os.path, os

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


class ScrollUnloadView(ScrollView):
    def __init__(self, toolbox_hosted=True, parent = None, form=None, name = None,fl = 0):
        ScrollView.__init__(self, parent, name, fl)
        #print "ScrollUnloadView.__init__()"
        self.toolbox_hosted = toolbox_hosted
        self.form = form

        self.image_icon_map = {'tiff' : 'tif.png',
                                'bmp'  : 'bmp.png',
                                'jpeg' : 'jpg.png',
                                'gif'  : 'gif.png',
                                'unknown' : 'unknown.png',
                                }

        self.video_icon_map = {'unknown' : 'movie.png',
                                'mpeg'    : 'mpg.png',
                                }
                                
        QTimer.singleShot(0, self.fillControls)
        

    def fillControls(self):
        ScrollView.fillControls(self)

        if 0:
            self.addGroupHeading("error", self.__tr("ERROR: Photo Card Failed to Mount Properly. Please check device and card and try again."))

        self.addGroupHeading("files_to_unload", self.__tr("Select File(s) to Unload from Photo Card"))
        self.addIconList()

        self.addGroupHeading("folder", self.__tr("Unload Folder"))
        self.addFolder()

        #self.addGroupHeading("options", self.__tr("Options"))


        self.addGroupHeading("space1", "")

        if self.toolbox_hosted:
            s = self.__tr("<< Functions")
        else:
            s = self.__tr("Close")

        self.unloadButton = self.addActionButton("bottom_nav", self.__tr("Unload File(s)"), 
                                self.unloadButton_clicked, 'download-small.png', 'download-small-disabled.png', 
                                s, self.funcButton_clicked)

        self.unloadButton.setEnabled(False)

        self.maximizeControl()   


    def onDeviceChange(self, cur_device=None):
        if cur_device is not None:
            log.debug("ScrollUnloadView.onDeviceChange(%s)" % cur_device.device_uri)
            self.cur_device = cur_device
        else:
            log.debug("ScrollUnloadView.onDeviceChange(None)")

        # TODO: Print a message telling users to use USB mass storage if possible
        QTimer.singleShot(0, self.mountCard)

        
    def mountCard(self):
        self.pc = None

        if self.cur_device is not None and self.cur_device.supported:

            QApplication.setOverrideCursor(QApplication.waitCursor)

            try:
                self.pc = photocard.PhotoCard(None, self.cur_device.device_uri, self.cur_printer)
            except Error, e:
                log.error("An error occured: %s" % e[0])
                #self.form.FailureUI(self.__tr("<p><b>Unable to mount photocard.</b><p>Could not connect to device."))
                self.cleanup(EVENT_PCARD_UNABLE_TO_MOUNT)
                return False

            if self.pc.device.device_uri is None and self.cur_printer:
                log.error("Printer '%s' not found." % self.cur_printer)
                #self.form.FailureUI(self.__tr("<p><b>Unable to mount photocard.</b><p>Device not found."))
                self.cleanup(EVENT_PCARD_JOB_FAIL)
                return False

            if self.pc.device.device_uri is None and self.cur_device.device_uri:
                log.error("Malformed/invalid device-uri: %s" % self.device_uri)
                self.form.FailureUI(self.__tr("<p><b>Unable to mount photocard.</b><p>Malformed/invalid device-uri."))
                self.cleanup(EVENT_PCARD_JOB_FAIL)
                return False
            else:
                try:
                    self.pc.mount()
                except Error:
                    log.error("Unable to mount photo card on device. Check that device is powered on and photo card is correctly inserted.")
                    #self.form.FailureUI(self.__tr("<p><b>Unable to mount photocard.</b><p>Check that device is powered on and photo card is correctly inserted."))
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

                if user_cfg.last_used.working_dir and \
                    os.path.exists(user_cfg.last_used.working_dir):

                    self.unload_dir = user_cfg.last_used.working_dir
                else:
                    self.unload_dir = os.path.normpath(os.path.expanduser('~'))

                os.chdir(self.unload_dir)
                self.UnloadDirectoryEdit.setText(self.unload_dir)

                self.unload_list = self.pc.get_unload_list()

                self.total_number = 0
                self.total_size = 0

                self.removal_option = 1 # remove selected

                self.updateSelectionStatus()

                if self.pc.write_protect:
                    self.removal_option = 0 # leave all files on card

                # Item map disambiguates between files of the same
                # name that are on the pcard in more than one location
                self.item_map = {}

                QApplication.restoreOverrideCursor()

        else:
            log.debug("Unsupported device")
            self.y = 0
            self.clear()
            return False

        self.busy = False

        QTimer.singleShot(0, self.updateIconView)

        self.display_update_timer = QTimer(self, "DisplayUpdateTimer")
        self.connect(self.display_update_timer, SIGNAL('timeout()'), self.updateDisplay)

        self.display_update_timer.start(1000)

        return True



    def addIconList(self):
        widget = self.getWidget()

        layout32 = QGridLayout(widget,1,1,5,10,"layout32")

        spacer34 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout32.addItem(spacer34,2,2)

        self.selectAllPushButton = PixmapLabelButton(widget, 'ok_small.png', None)

        layout32.addWidget(self.selectAllPushButton,2,0)

        self.ShowThumbnailsButton = PixmapLabelButton(widget, 'thumbnail.png', None)

        layout32.addWidget(self.ShowThumbnailsButton,2,3)

        self.IconView = QIconView(widget,"IconView")
        self.IconView.setResizePolicy(QIconView.AutoOneFit)
        self.IconView.setSelectionMode(QIconView.Multi)
        self.IconView.setResizeMode(QIconView.Adjust)
        self.IconView.setMaxItemWidth(200)
        self.IconView.setAutoArrange(0)
        self.IconView.setItemsMovable(1)

        layout32.addMultiCellWidget(self.IconView,0,0,0,3)

        self.selectNonePushButton = PixmapLabelButton(widget, 'folder_remove.png', None)

        layout32.addWidget(self.selectNonePushButton,2,1)

        self.selectionStatusText = QLabel(widget,"selectionStatusText")
        layout32.addMultiCellWidget(self.selectionStatusText,1,1,0,3)
        self.selectAllPushButton.setText(self.__tr("Select All"))
        self.selectNonePushButton.setText(self.__tr("Select None"))
        self.ShowThumbnailsButton.setText(self.__tr("Show Thumbnails"))

        self.connect(self.selectAllPushButton,SIGNAL("clicked()"),self.selectAllPushButton_clicked)
        self.connect(self.selectNonePushButton,SIGNAL("clicked()"),self.selectNonePushButton_clicked)
        self.connect(self.IconView,SIGNAL("doubleClicked(QIconViewItem*)"),self.IconView_doubleClicked)
        self.connect(self.IconView,SIGNAL("rightButtonClicked(QIconViewItem*,const QPoint&)"),self.IconView_rightButtonClicked)
        self.connect(self.ShowThumbnailsButton,SIGNAL("clicked()"),self.ShowThumbnailsButton_clicked)

        self.addWidget(widget, "file_list", maximize=True)


    def selectAllPushButton_clicked(self):
        self.IconView.selectAll(1)

    def selectNonePushButton_clicked(self):
        self.IconView.selectAll(0)

    def IconView_doubleClicked(self, a0):
        return self.PopupProperties()

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

    def ShowThumbnailsButton_clicked(self):
        self.ShowThumbnailsButton.setEnabled(False)
        self.updateIconView(first_load=False)

    def updateDisplay(self):
        if not self.busy:
            self.total_number = 0
            self.total_size = 0
            i = self.IconView.firstItem()

            while i is not None:

                if i.isSelected():
                    self.total_number += 1
                    self.total_size += i.size

                i = i.nextItem()

            self.updateSelectionStatus()
        
        self.updateUnloadButton()
            
    def updateUnloadButton(self):
        self.unloadButton.setEnabled(not self.busy and self.total_number and os.path.exists(self.unload_dir))
        #qApp.processEvents()

    def updateSelectionStatus(self):
        if self.total_number == 0:
            s = self.__tr("No files selected")

        elif self.total_number == 1:
            s = self.__tr("1 file selected, %1").arg(utils.format_bytes(self.total_size, True))

        else:
            s = self.__tr("%1 files selected, %2").arg(self.total_number).arg(utils.format_bytes(self.total_size, True))

        self.selectionStatusText.setText(s)


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
            self.form.FailureUI(self.__tr("<p><b>No thumbnail found in image.</b>"))

        item.thumbnail_set = True

    def Properties(self, item):
        if item is not None:
            if not item.exif_info:
                item.exif_info = self.pc.get_exif_path(item.path)

            ImagePropertiesDlg(item.filename, item.dirname,
                                '/'.join([item.mime_type, item.mime_subtype]),
                                utils.format_bytes(item.size, True),
                                item.exif_info, self).exec_loop()


    def updateIconView(self, first_load=True):
        QApplication.setOverrideCursor(QApplication.waitCursor)
        self.busy = True
        self.first_load = first_load
        

        if first_load:
            self.IconView.clear()

        self.num_items = len(self.unload_list)

        self.pb = QProgressBar()
        self.pb.setTotalSteps(self.num_items)
        self.form.statusBar().addWidget(self.pb)
        self.pb.show()
        
        self.item_num = 0

        self.load_timer = QTimer(self, "LoadTimer")
        self.connect(self.load_timer, SIGNAL('timeout()'), self.continueLoadIconView)
        self.load_timer.start(0)
    
    
    def continueLoadIconView(self):
        global progress_dlg
        
        if self.item_num == self.num_items:
            
            self.load_timer.stop()
            self.disconnect(self.load_timer, SIGNAL('timeout()'), self.continueLoadIconView)
            self.load_timer = None
            del self.load_timer

            self.pb.hide()
            self.form.statusBar().removeWidget(self.pb)

            self.IconView.adjustItems()
            self.busy = False
            QApplication.restoreOverrideCursor()
            return

        f = self.unload_list[self.item_num]
        log.debug(f)
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






    def addFolder(self):
        widget = self.getWidget()
        layout38 = QGridLayout(widget,1,1,5,10,"layout38")

        self.UnloadDirectoryEdit = QLineEdit(widget,"UnloadDirectoryEdit")
        layout38.addWidget(self.UnloadDirectoryEdit,0,0)

        self.UnloadDirectoryBrowseButton = PixmapLabelButton(widget, 'folder_open.png', None)
        layout38.addWidget(self.UnloadDirectoryBrowseButton,0,1)

        self.UnloadDirectoryBrowseButton.setText(self.__tr("Browse..."))
        self.connect(self.UnloadDirectoryBrowseButton,SIGNAL("clicked()"),self.UnloadDirectoryBrowseButton_clicked)
        self.connect(self.UnloadDirectoryEdit,SIGNAL("textChanged(const QString&)"),self.UnloadDirectoryEdit_textChanged)        
        
        self.bg = self.UnloadDirectoryEdit.paletteBackgroundColor()

        self.addWidget(widget, "folder")
        
    def UnloadDirectoryEdit_textChanged(self, dir):
        self.unload_dir = str(dir)
        
        if not os.path.exists(self.unload_dir):
            self.UnloadDirectoryEdit.setPaletteBackgroundColor(QColor(0xff, 0x99, 0x99))
        else:
            self.UnloadDirectoryEdit.setPaletteBackgroundColor(self.bg)

    def UnloadDirectoryBrowseButton_clicked(self):
        old_dir = self.unload_dir
        self.unload_dir = unicode(QFileDialog.getExistingDirectory(self.unload_dir, self))

        if not len(self.unload_dir):
            return
        
        elif not utils.is_path_writable(self.unload_dir):
            self.form.FailureUI(self.__tr("<p><b>The unload directory path you entered is not valid.</b><p>The directory must exist and you must have write permissions."))
            self.unload_dir = old_dir
        
        else:
            self.UnloadDirectoryEdit.setText(self.unload_dir)
            os.chdir(self.unload_dir)
            user_cfg.last_used.working_dir = self.unload_dir
  


    def unloadButton_clicked(self):
        was_cancelled = False
        self.busy = True
        self.unloadButton.setEnabled(False)
        self.unload_dir = unicode(self.UnloadDirectoryEdit.text())
        dir_error = False

        try:
            try:
                os.chdir(self.unload_dir)
            except OSError:
                log.error("Directory not found: %s" % self.unload_dir)
                dir_error = True

            if dir_error or not utils.is_path_writable(self.unload_dir):
                self.form.FailureUI(self.__tr("<p><b>The unload directory path is not valid.</b><p>Please enter a new path and try again."))
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
                self.form.FailureUI(self.__tr("<p><b>No files are selected to unload.</b><p>Please select one or more files to unload and try again."))
                return

            self.pb = QProgressBar()
            self.pb.setTotalSteps(total_size)
            self.form.statusBar().addWidget(self.pb)
            self.pb.show()
            
            qApp.processEvents()

            if self.removal_option == 0:
                total_size, total_time, was_cancelled = \
                    self.pc.unload(unload_list, self.updateStatusProgressBar, None, True)

            elif self.removal_option == 1: # remove selected
                total_size, total_time, was_cancelled = \
                    self.pc.unload(unload_list, self.updateStatusProgressBar, None, False)

            else: # remove all
                total_size, total_time, was_cancelled = \
                    self.pc.unload(unload_list, self.updateStatusProgressBar, None, False)
                # TODO: Remove remainder of files

            self.pb.hide()
            self.form.statusBar().removeWidget(self.pb)

            self.pc.device.sendEvent(EVENT_PCARD_FILES_TRANSFERED)

            if self.removal_option != 0: # remove selected or remove all
                self.unload_list = self.pc.get_unload_list()
                self.total_number = 0
                self.total_size = 0
                self.item_map = {}
                #self.load_icon_view(first_load=True)
                self.updateIconView()

            if was_cancelled:
                self.form.FailureUI(self.__tr("<b>Unload cancelled at user request.</b>"))
            else:
                #self.funcButton_clicked()
                pass

        finally:
            self.busy = False
            
    def updateStatusProgressBar(self, src, trg, size):
        self.pb.setProgress(self.pb.progress() + size)
        qApp.processEvents()


    def cleanup(self, error=0):
        if self.pc is not None:
            if error > 0:
                self.pc.device.sendEvent(error, typ='error')

    def funcButton_clicked(self):
        if self.toolbox_hosted:
            self.form.SwitchFunctionsTab("funcs")
        else:
            self.form.close()

    def __tr(self,s,c = None):
        return qApp.translate("DevMgr4",s,c)