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
from prnt import cups

# Qt
from qt import *
from scrollview import ScrollView, PixmapLabelButton
from allowabletypesdlg import AllowableTypesDlg

# Std Lib
import os.path, os


class RangeValidator(QValidator):
    def __init__(self, parent=None, name=None):
        QValidator.__init__(self, parent, name)

    def validate(self, input, pos):
        for x in str(input)[pos-1:]:
            if x not in '0123456789,- ':
                return QValidator.Invalid, pos

        return QValidator.Acceptable, pos


class ScrollPrintView(ScrollView):
    def __init__(self, toolbox_hosted=True, parent = None, form=None, name = None,fl = 0):
        ScrollView.__init__(self,parent,name,fl)
        
        self.toolbox_hosted = toolbox_hosted
        self.form = form
        self.file_list = []
        self.pages_button_group = 0
        
        self.allowable_mime_types = cups.getAllowableMIMETypes()
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
        }
        

    def fillControls(self):
        ScrollView.fillControls(self)
        
        self.addPrinterFaxList()
        self.addGroupHeading("files_to_print", "File(s) to Print")
        self.addFileList()
        self.addGroupHeading("options", "Print Options")
        self.addCopies()
        self.addPageRange()
        self.addPageSet()
        self.addGroupHeading("space1", "")
        
        if self.toolbox_hosted:
            s = self.__tr("<< Functions")
        else:
            s = self.__tr("Close")
            
        self.printButton = self.addActionButton("bottom_nav", self.__tr("Print File(s)"), 
                                self.printButton_clicked, s, self.funcButton_clicked)
                                
        self.printButton.setEnabled(False)
        
        self.maximizeControl()
        
        
    def addFileList(self):
        widget = self.getWidget()
        
        
##        layout20 = QGridLayout(LayoutWidget_8,1,1,11,6,"layout20")
##
##        self.moveUpPushButton = QPushButton(LayoutWidget_8,"moveUpPushButton")
##
##        layout20.addWidget(self.moveUpPushButton,1,2)
##
##        self.listView2 = QListView(LayoutWidget_8,"listView2")
##        self.listView2.addColumn(self.__tr("Name"))
##        self.listView2.addColumn(self.__tr("Type"))
##        self.listView2.addColumn(self.__tr("Path"))
##        self.listView2.setAllColumnsShowFocus(1)
##        self.listView2.setShowSortIndicator(1)
##
##        layout20.addMultiCellWidget(self.listView2,0,0,0,5)
##
##        self.removeFilePushButton = QPushButton(LayoutWidget_8,"removeFilePushButton")
##
##        layout20.addWidget(self.removeFilePushButton,1,1)
##
##        self.moveDownPushButton = QPushButton(LayoutWidget_8,"moveDownPushButton")
##
##        layout20.addWidget(self.moveDownPushButton,1,3)
##        spacer20_3 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
##        layout20.addItem(spacer20_3,1,4)
##
##        self.showTypesPushButton = QPushButton(LayoutWidget_8,"showTypesPushButton")
##
##        layout20.addWidget(self.showTypesPushButton,1,5)
##
##        self.addFilePushButton = QPushButton(LayoutWidget_8,"addFilePushButton")
##
##        layout20.addWidget(self.addFilePushButton,1,0)


        
        
        layout37 = QGridLayout(widget,1,1,5,10,"layout37")
        
        self.addFilePushButton = PixmapLabelButton(widget, 
            "list-add.png", "list-add-disabled.png")

        layout37.addWidget(self.addFilePushButton,2,0)
        
        #self.showTypesPushButton = QPushButton(widget,"showTypesPushButton")
        
        self.showTypesPushButton = PixmapLabelButton(widget, "mimetypes.png", 
            None, name='addFilePushButton')
        
        layout37.addWidget(self.showTypesPushButton,2,3)
        
        self.removeFilePushButton = PixmapLabelButton(widget, 
            "list-remove.png", "list-remove-disabled.png")
        
        layout37.addWidget(self.removeFilePushButton,2,1)
        
        self.fileListView = QListView(widget,"fileListView")
        self.fileListView.addColumn(self.__tr("Name"))
        self.fileListView.addColumn(self.__tr("Type"))
        self.fileListView.addColumn(self.__tr("Path"))
        self.fileListView.setAllColumnsShowFocus(1)
        self.fileListView.setShowSortIndicator(1)
        self.fileListView.setColumnWidth(0, 150)
        self.fileListView.setColumnWidth(1, 75)
        self.fileListView.setColumnWidth(2, 300)
        self.fileListView.setItemMargin(2)
        self.fileListView.setSorting(-1)
        
        layout37.addMultiCellWidget(self.fileListView,1,1,0,3)
        
        spacer26 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout37.addItem(spacer26,2,2)
        
        self.addFilePushButton.setText(self.__tr("Add File..."))
        self.showTypesPushButton.setText(self.__tr("Show Types..."))
        self.removeFilePushButton.setText(self.__tr("Remove File"))
        
        self.removeFilePushButton.setEnabled(False)
        
        self.connect(self.addFilePushButton, SIGNAL("clicked()"), self.addFile_clicked)
        self.connect(self.removeFilePushButton, SIGNAL("clicked()"), self.removeFile_clicked)
        self.connect(self.showTypesPushButton, SIGNAL("clicked()"), self.showFileTypes_clicked)
        self.connect(self.fileListView,SIGNAL("rightButtonClicked(QListViewItem*,const QPoint&, int)"),self.fileListView_rightButtonClicked)

        self.addWidget(widget, "file_list", maximize=True)
        
        
    def fileListView_rightButtonClicked(self, item, pos, col):
        popup = QPopupMenu(self)
        popup.insertItem(QIconSet(QPixmap(os.path.join(prop.image_dir, 'list-add.png'))),
            self.__tr("Add File..."), self.addFile_clicked)
    
        if item is not None:
            popup.insertItem(QIconSet(QPixmap(os.path.join(prop.image_dir,
                'list-remove.png'))), self.__tr("Remove File"), self.removeFile_clicked)
            
        popup.insertSeparator(-1)
        popup.insertItem(QIconSet(QPixmap(os.path.join(prop.image_dir,
                'mimetypes.png'))), self.__tr("Show File Types..."), self.showFileTypes_clicked)
        popup.popup(pos)
        
        
    def addFile(self, path):
        path = os.path.realpath(path)
        if os.path.exists(path):
            mime_type = magic.mime_type(path)
            mime_type_desc = mime_type
            log.debug(mime_type)
            
            try:
                mime_type_desc = self.MIME_TYPES_DESC[mime_type][0]
            except KeyError:
                self.form.WarningUI(self.__tr("<b>You are trying to add a file that cannot be directly printed with this utility.</b><p>To print this file, use the print command in the application that created it."))
            else:
                log.debug("Adding file %s (%s,%s)" % (path, mime_type, mime_type_desc))
                self.file_list.append((path, mime_type, mime_type_desc))
        else:
            self.form.FailureUI(self.__tr("<b>Unable to add file '%s' to file list.</b><p>Check the file name and try again." % path))

        self.UpdateFileList()
        
    def UpdateFileList(self):
        self.fileListView.clear()
        temp = self.file_list[:]
        temp.reverse()
        x = True

        for p, t, d in temp:
            i = QListViewItem(self.fileListView, os.path.basename(p), d, p)
            if x:
                self.fileListView.setSelected(i, True)
                x = False

        non_empty_file_list = self.fileListView.childCount() > 0
        self.printButton.setEnabled(non_empty_file_list)
        self.removeFilePushButton.setEnabled(non_empty_file_list)
        
        
        
    
    def addFile_clicked(self):
        workingDirectory = user_cfg.last_used.working_dir
       
        if not workingDirectory or not os.path.exists(workingDirectory):
            workingDirectory = os.path.expanduser("~")

        log.debug("workingDirectory: %s" % workingDirectory)

        dlg = QFileDialog(workingDirectory, QString.null, None, None, True)

        dlg.setCaption("openfile")
        dlg.setMode(QFileDialog.ExistingFile)
        dlg.show()

        if dlg.exec_loop() == QDialog.Accepted:
                results = dlg.selectedFile()
                workingDirectory = str(dlg.dir().absPath())
                log.debug("results: %s" % results)
                log.debug("workingDirectory: %s" % workingDirectory)
                
                user_cfg.last_used.working_dir = workingDirectory

                if results:
                    self.addFile(str(results))
                    
        
    def removeFile_clicked(self):
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
            
    def showFileTypes_clicked(self):
        x = {}
        for a in self.allowable_mime_types:
            x[a] = self.MIME_TYPES_DESC.get(a, ('Unknown', 'n/a'))

        log.debug(x)
        dlg = AllowableTypesDlg(x, self)
        dlg.exec_loop()
        
        
    def addCopies(self):
        widget = self.getWidget()
        
        layout12 = QHBoxLayout(widget,5,10,"layout12")

        self.textLabel5 = QLabel(widget,"textLabel5")
        layout12.addWidget(self.textLabel5)
        spacer20 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout12.addItem(spacer20)

        self.copiesSpinBox = QSpinBox(widget,"copiesSpinBox")
        layout12.addWidget(self.copiesSpinBox)

        self.copiesDefaultPushButton = QPushButton(widget,"copiesDefaultPushButton")
        layout12.addWidget(self.copiesDefaultPushButton)

        self.textLabel5.setText(self.__tr("Number of copies:"))
        self.copiesDefaultPushButton.setText(self.__tr("Default"))
        
        self.copiesSpinBox.setMaxValue(99)
        self.copiesSpinBox.setMinValue(1)
        self.copiesSpinBox.setValue(1)
        
        self.copiesDefaultPushButton.setEnabled(False)
        
        self.connect(self.copiesDefaultPushButton, SIGNAL("clicked()"), self.copiesDefaultPushButton_clicked)
        self.connect(self.copiesSpinBox, SIGNAL("valueChanged(int)"), self.copiesSpinBox_valueChanged)
        
        self.addWidget(widget, "copies")
        
    def copiesDefaultPushButton_clicked(self):
        self.copiesSpinBox.setValue(1)
        self.copiesDefaultPushButton.setEnabled(False)
        
    def copiesSpinBox_valueChanged(self, i):
        self.copiesDefaultPushButton.setEnabled(i != 1)
    
    def addPageRange(self):
        widget = self.getWidget()
        
        layout39 = QGridLayout(widget,1,1,5,10,"layout39")

        self.pageRangeEdit = QLineEdit(widget,"self.pageRangeEdit")
        self.pageRangeEdit.setEnabled(0)
        layout39.addWidget(self.pageRangeEdit,0,3)
        
        spacer20_2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout39.addItem(spacer20_2,0,1)

        textLabel5_2 = QLabel(widget,"textLabel5_2")
        layout39.addWidget(textLabel5_2,0,0)

        self.pagerangeDefaultPushButton = QPushButton(widget,"pagerangeDefaultPushButton")
        layout39.addWidget(self.pagerangeDefaultPushButton,0,4)

        self.rangeButtonGroup = QButtonGroup(widget,"self.rangeButtonGroup")
        self.rangeButtonGroup.setLineWidth(0)
        self.rangeButtonGroup.setColumnLayout(0,Qt.Vertical)
        self.rangeButtonGroup.layout().setSpacing(0)
        self.rangeButtonGroup.layout().setMargin(0)
        self.rangeButtonGroupLayout = QGridLayout(self.rangeButtonGroup.layout())
        self.rangeButtonGroupLayout.setAlignment(Qt.AlignTop)

        radioButton3_2 = QRadioButton(self.rangeButtonGroup,"radioButton3_2")
        radioButton3_2.setChecked(1)
        self.rangeButtonGroup.insert( radioButton3_2,0)
        self.rangeButtonGroupLayout.addWidget(radioButton3_2,0,0)

        radioButton4_2 = QRadioButton(self.rangeButtonGroup,"radioButton4_2")
        self.rangeButtonGroup.insert( radioButton4_2,1)
        self.rangeButtonGroupLayout.addWidget(radioButton4_2,0,1)
        
        layout39.addWidget(self.rangeButtonGroup,0,2)
        
        self.bg = self.pageRangeEdit.paletteBackgroundColor()
        self.invalid_page_range = False
        
        self.pageRangeEdit.setValidator(RangeValidator(self.pageRangeEdit))
        
        textLabel5_2.setText(self.__tr("Page Range:"))
        radioButton3_2.setText(self.__tr("All pages"))
        radioButton4_2.setText(self.__tr("Page range:"))
        
        self.pagerangeDefaultPushButton.setText(self.__tr("Default"))
        
        self.pagerangeDefaultPushButton.setEnabled(False)
        
        self.connect(self.rangeButtonGroup, SIGNAL("clicked(int)"), self.rangeButtonGroup_clicked)
        self.connect(self.pageRangeEdit,SIGNAL("lostFocus()"),self.pageRangeEdit_lostFocus)
        self.connect(self.pageRangeEdit,SIGNAL("textChanged(const QString&)"),self.pageRangeEdit_textChanged)
        self.connect(self.pagerangeDefaultPushButton, SIGNAL("clicked()"), self.pagerangeDefaultPushButton_clicked)
        
        self.addWidget(widget, "range")
        
    def pagerangeDefaultPushButton_clicked(self):
        self.rangeButtonGroup.setButton(0)
        self.pagerangeDefaultPushButton.setEnabled(False)
        self.pageRangeEdit.setEnabled(False)
        
    def rangeButtonGroup_clicked(self, a0):
        self.pages_button_group = a0
        self.pageRangeEdit.setEnabled(a0 == 1)
        self.pagerangeDefaultPushButton.setEnabled(a0 == 1)
        
    def pageRangeEdit_lostFocus(self):
        x = []
        try:
            x = utils.expand_range(str(self.pageRangeEdit.text()))
        except ValueError:
            log.error("Invalid page range entered.")
            self.invalid_page_range = True
            self.pageRangeEdit.setPaletteBackgroundColor(QColor(0xff, 0x99, 0x99))

        else:
            self.pageRangeEdit.setText(QString(utils.collapse_range(x)))
            self.pageRangeEdit.setPaletteBackgroundColor(self.bg)
            self.invalid_page_range = False

    def pageRangeEdit_textChanged(self,a0):
        x = []
        try:
            x = utils.expand_range(str(self.pageRangeEdit.text()))
        except ValueError:
            self.invalid_page_range = True
            self.pageRangeEdit.setPaletteBackgroundColor(QColor(0xff, 0x99, 0x99))

        else:
            self.pageRangeEdit.setPaletteBackgroundColor(self.bg)
            self.invalid_page_range = False
        
    def addPageSet(self):
        widget = self.getWidget()
        
        layout34 = QHBoxLayout(widget,5,10,"layout34")

        self.textLabel5_4 = QLabel(widget,"textLabel5_4")
        layout34.addWidget(self.textLabel5_4)
        spacer20_4 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout34.addItem(spacer20_4)

        self.pageSetComboBox = QComboBox(0,widget,"pageSetComboBox")
        layout34.addWidget(self.pageSetComboBox)

        self.pagesetDefaultPushButton = QPushButton(widget,"pagesetDefaultPushButton")
        layout34.addWidget(self.pagesetDefaultPushButton)
        
        self.textLabel5_4.setText(self.__tr("Page set:"))
        self.pageSetComboBox.clear()
        self.pageSetComboBox.insertItem(self.__tr("All pages"))
        self.pageSetComboBox.insertItem(self.__tr("Even pages"))
        self.pageSetComboBox.insertItem(self.__tr("Odd pages"))
        self.pagesetDefaultPushButton.setText(self.__tr("Default"))
        
        self.pagesetDefaultPushButton.setEnabled(False)
        
        self.connect(self.pageSetComboBox, SIGNAL("activated(int)"), self.pageSetComboBox_activated)
        self.connect(self.pagesetDefaultPushButton, SIGNAL("clicked()"), self.pagesetDefaultPushButton_clicked)
        
        self.addWidget(widget, "set")
        
    def pagesetDefaultPushButton_clicked(self):
        self.pagesetDefaultPushButton.setEnabled(False)
        self.pageSetComboBox.setCurrentItem(0)
        
    def pageSetComboBox_activated(self, i):
        self.pagesetDefaultPushButton.setEnabled(i != 0)

    def printButton_clicked(self):
        if self.invalid_page_range:
            self.form.FailureUI(self.__tr("<b>Cannot print: Invalid page range: %1</b><p>A valid page range is a list of pages or ranges of pages separated by commas (e.g., 1-2,4,6-7)").arg(self.pageRangeEdit.text()))
            return
            
        try:
            try:
                self.cur_device.open()
            except Error:
                self.form.FailureUI(self.__tr("<b>Cannot print: Device is busy or not available.</b><p>Please check device and try again."))
                return
            
            if self.cur_device.isIdleAndNoError():
                copies = int(self.copiesSpinBox.value())
                all_pages = self.pages_button_group == 0
                page_range = str(self.pageRangeEdit.text())
                page_set = int(self.pageSetComboBox.currentItem())
            
                cups.resetOptions()
                cups.openPPD(self.cur_printer)
                current_options = dict(cups.getOptions())
                cups.closePPD()
                
                nup = int(current_options.get("number-up", 1))
                    
                for p, t, d in self.file_list:
        
                    alt_nup = (nup > 1 and t == 'application/postscript' and utils.which('psnup'))
        
                    if utils.which('lpr'):
                        if alt_nup:
                            cmd = ' '.join(['psnup', '-%d' % nup, ''.join(['"', p, '"']), '| lpr -P', self.cur_printer])
                        else:
                            cmd = ' '.join(['lpr -P', self.cur_printer])
        
                        if copies > 1:
                            cmd = ' '.join([cmd, '-#%d' % copies])
        
                    else:
                        if alt_nup:
                            cmd = ' '.join(['psnup', '-%d' % nup, ''.join(['"', p, '"']), '| lp -c -d', self.cur_printer])
                        else:
                            cmd = ' '.join(['lp -c -d', self.cur_printer])
        
                        if copies > 1:
                            cmd = ' '.join([cmd, '-n%d' % copies])
        
        
                    if not all_pages and len(page_range) > 0:
                        cmd = ' '.join([cmd, '-o page-ranges=%s' % page_range])
        
                    if page_set > 0:
                        if page_set == 1:
                            cmd = ' '.join([cmd, '-o page-set=even'])
                        else:
                            cmd = ' '.join([cmd, '-o page-set=odd'])
        
                    if not alt_nup:
                        cmd = ''.join([cmd, ' "', p, '"'])
        
                    log.debug("Printing: %s" % cmd)
        
                    if os.system(cmd) != 0:
                        log.error("Print command failed.")
                        self.FailureUI(self.__tr("Print command failed."))
            
                if self.toolbox_hosted:
                    self.form.SwitchFunctionsTab("funcs")
                else:
                    self.form.close()
                    
            else:
                self.form.FailureUI(self.__tr("<b>Cannot print: Device is busy or not available.</b><p>Please check device and try again."))
        
        finally:
            self.cur_device.close()
        
    def funcButton_clicked(self):
        if self.toolbox_hosted:
            self.form.SwitchFunctionsTab("funcs")
        else:
            self.form.close()
        
    def __tr(self,s,c = None):
        return qApp.translate("DevMgr4",s,c)
