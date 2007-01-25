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
# Authors: Don Welch, Pete Parks
#

from __future__ import generators

# Std Lib
import sys, time, os, gzip

# Local
from base.g import *
from base import device, status, msg, maint, utils, service, pml
from prnt import cups
from base.codes import *

# Qt
from qt import *

# Main form
from devmgr4_base import DevMgr4_base

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
from nodevicesform import NoDevicesForm
from aboutdlg import AboutDlg
from cleaningform import CleaningForm
from cleaningform2 import CleaningForm2
from waitform import WaitForm
from faxsettingsform import FaxSettingsForm
from informationform import InformationForm

# all in seconds
MIN_AUTO_REFRESH_RATE = 5
MAX_AUTO_REFRESH_RATE = 60
DEF_AUTO_REFRESH_RATE = 5


class JobListViewItem(QListViewItem):
    def __init__(self, parent, printer, job_id, state, user, title):
        QListViewItem.__init__(self, parent, printer, str(job_id), state, user, title)
        self.job_id = job_id
        self.printer = printer

class QPixmapLabelButton(QPushButton):
    def __init__(self, parent=None, pixmap=None, disabled_pixmap=None, name=''):
        QPushButton.__init__(self, parent, name)
        self.pixmap = pixmap
        self.disabled_pixmap = disabled_pixmap
        self.pixmap_width, self.pixmap_height = self.pixmap.width(), self.pixmap.height()

    def drawButtonLabel(self, painter):
        button_width, button_height = self.width(), self.height()

        adj = 0
        if self.isDown():
            adj = 1


        if self.isEnabled():
            painter.setPen(Qt.black)
            weight = QFont.Bold
        else:
            painter.setPen(Qt.gray)
            weight = QFont.Normal

        f = QFont() #"helvetica", 12, weight)
        f.setWeight(weight)
        painter.setFont(f)

        text_rect = painter.boundingRect(0, 0, 1000, 1000, Qt.AlignLeft, self.text())
        text_width, text_height = text_rect.right() - text_rect.left(), text_rect.bottom() - text_rect.top()

        button_width_center = button_width/2
        button_height_center = button_height/2
        combined_width_center = (self.pixmap_width + text_width + 10)/2


        if self.isEnabled():
            painter.drawPixmap(button_width_center - combined_width_center + adj, button_height_center - self.pixmap_height/2 + adj, self.pixmap)
        else:
            painter.drawPixmap(button_width_center - combined_width_center + adj, button_height_center - self.pixmap_height/2 + adj, self.disabled_pixmap)


        painter.drawText(button_width_center - combined_width_center + self.pixmap_width + 10 + adj, 
                         button_height_center - text_height/2 + adj, 1000, 1000, Qt.AlignLeft, self.text())



class ScrollToolView(QScrollView):
    def __init__(self,parent = None,name = None,fl = 0):
        QScrollView.__init__(self,parent,name,fl)
        self.items = {}
        self.setStaticBackground(True)
        self.enableClipper(True)
        self.viewport().setPaletteBackgroundColor(qApp.palette().color(QPalette.Active, QColorGroup.Base))
        self.row_height = 120

    def viewportResizeEvent(self, e):
        for x in self.items:
            self.items[x].resize(e.size().width(), self.row_height)

    def addItem(self, name, title, pix, text, button_text, button_func):
        num_items = len(self.items)
        LayoutWidget = QWidget(self.viewport(),"layoutwidget")
        LayoutWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))
        LayoutWidget.setGeometry(QRect(0, 0, self.width(), self.row_height))
        LayoutWidget.setPaletteBackgroundColor(qApp.palette().color(QPalette.Active, QColorGroup.Base))
        self.addChild(LayoutWidget)

        if num_items:
            self.moveChild(LayoutWidget, 0, self.row_height*num_items)

        layout = QGridLayout(LayoutWidget,1,1,10,10,"layout")

        pushButton = QPushButton(LayoutWidget,"pushButton")
        pushButton.setSizePolicy(QSizePolicy(QSizePolicy.Maximum,QSizePolicy.Fixed,0,0,
                                 pushButton.sizePolicy().hasHeightForWidth()))

        self.connect(pushButton,SIGNAL("clicked()"), button_func) 

        layout.addWidget(pushButton,2,2)
        textLabel = QLabel(LayoutWidget,"textLabel")
        layout.addWidget(textLabel,1,1)

        pixmap = QLabel(LayoutWidget,"pixmapLabel2")
        pixmap.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,
                             pixmap.sizePolicy().hasHeightForWidth()))
        pixmap.setMinimumSize(QSize(32,32))
        pixmap.setMaximumSize(QSize(32,32))
        pixmap.setPixmap(pix)
        pixmap.setScaledContents(1)
        layout.addWidget(pixmap,1,0)

        textLabel2 = QLabel(LayoutWidget,"textLabel2")
        textLabel2.setAlignment(QLabel.WordBreak | QLabel.AlignTop)
        textLabel2.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Expanding))
        layout.addWidget(textLabel2,2,1)

        if num_items:
            line = QFrame(LayoutWidget,"line")
            line.setFrameShadow(QFrame.Sunken)
            line.setFrameShape(QFrame.HLine)
            line.setPaletteBackgroundColor(qApp.palette().color(QPalette.Active, QColorGroup.Foreground))
            layout.addMultiCellWidget(line,0,0,0,2)        

        textLabel.setText(title)
        textLabel2.setText(text)
        pushButton.setText(button_text)
        self.resizeContents(self.width(), num_items*self.row_height*2)

        LayoutWidget.show()

        try:
            self.items[name]
        except KeyError:
            self.items[name] = LayoutWidget
        else:
            print "ERROR: Duplicate button name:", name

    def clear(self):
        if len(self.items):
            for x in self.items:
                self.removeChild(self.items[x])
                self.items[x].hide()

            self.items.clear()
            self.resizeContents(self.width(), 0)


class ScrollSuppliesView(QScrollView):
    def __init__(self,parent = None,name = None,fl = 0):
        QScrollView.__init__(self,parent,name,fl)
        self.items = {}
        self.setStaticBackground(True)
        self.enableClipper(True)
        self.viewport().setPaletteBackgroundColor(qApp.palette().color(QPalette.Active, QColorGroup.Base))

        self.pix_black = QPixmap(os.path.join(prop.image_dir, 'icon_black.png'))
        self.pix_blue = QPixmap(os.path.join(prop.image_dir, 'icon_blue.png'))
        self.pix_cyan = QPixmap(os.path.join(prop.image_dir, 'icon_cyan.png'))
        self.pix_grey = QPixmap(os.path.join(prop.image_dir, 'icon_grey.png'))
        self.pix_magenta = QPixmap(os.path.join(prop.image_dir, 'icon_magenta.png'))
        self.pix_photo = QPixmap(os.path.join(prop.image_dir, 'icon_photo.png'))
        self.pix_photo_cyan = QPixmap(os.path.join(prop.image_dir, 'icon_photo_cyan.png'))
        self.pix_photo_magenta = QPixmap(os.path.join(prop.image_dir, 'icon_photo_magenta.png'))
        self.pix_photo_yellow = QPixmap(os.path.join(prop.image_dir, 'icon_photo_yellow.png'))
        self.pix_tricolor = QPixmap(os.path.join(prop.image_dir, 'icon_tricolor.png'))
        self.pix_yellow = QPixmap(os.path.join(prop.image_dir, 'icon_yellow.png'))
        self.pix_battery = QPixmap(os.path.join(prop.image_dir, 'icon_battery.png'))
        self.pix_photo_cyan_and_photo_magenta = QPixmap(os.path.join(prop.image_dir, 'icon_photo_magenta_and_photo_cyan.png'))
        self.pix_magenta_and_yellow = QPixmap(os.path.join(prop.image_dir, 'icon_magenta_and_yellow.png'))
        self.pix_black_and_cyan = QPixmap(os.path.join(prop.image_dir, 'icon_black_and_cyan.png'))
        self.pix_light_gray_and_photo_black = QPixmap(os.path.join(prop.image_dir, 'icon_light_grey_and_photo_black.png'))
        self.pix_light_gray = QPixmap(os.path.join(prop.image_dir, 'icon_light_grey.png'))
        self.pix_photo_gray = QPixmap(os.path.join(prop.image_dir, 'icon_photo_black.png'))

        self.TYPE_TO_PIX_MAP = {AGENT_TYPE_BLACK: self.pix_black,
                               AGENT_TYPE_CMY: self.pix_tricolor,
                               AGENT_TYPE_KCM: self.pix_photo,
                               AGENT_TYPE_GGK: self.pix_grey,
                               AGENT_TYPE_YELLOW: self.pix_yellow,
                               AGENT_TYPE_MAGENTA: self.pix_magenta,
                               AGENT_TYPE_CYAN: self.pix_cyan,
                               AGENT_TYPE_CYAN_LOW: self.pix_photo_cyan,
                               AGENT_TYPE_YELLOW_LOW: self.pix_photo_yellow,
                               AGENT_TYPE_MAGENTA_LOW: self.pix_photo_magenta,
                               AGENT_TYPE_BLUE: self.pix_blue,
                               AGENT_TYPE_KCMY_CM: self.pix_grey,
                               AGENT_TYPE_LC_LM: self.pix_photo_cyan_and_photo_magenta,
                               AGENT_TYPE_Y_M: self.pix_magenta_and_yellow,
                               AGENT_TYPE_C_K: self.pix_black_and_cyan,
                               AGENT_TYPE_LG_PK: self.pix_light_gray_and_photo_black,
                               AGENT_TYPE_LG: self.pix_light_gray,
                               AGENT_TYPE_G: self.pix_grey,
                               AGENT_TYPE_PG: self.pix_photo_gray,                             
                               }

        self.row_height = 100

    def viewportResizeEvent(self, e):
        for x in self.items:
            self.items[x].resize(e.size().width(), self.row_height)

    def getIcon(self, agent_kind, agent_type):
        if agent_kind in (AGENT_KIND_SUPPLY,
                          AGENT_KIND_HEAD,
                          AGENT_KIND_HEAD_AND_SUPPLY,
                          AGENT_KIND_TONER_CARTRIDGE):

            return self.TYPE_TO_PIX_MAP[agent_type] 

        elif agent_kind == AGENT_KIND_INT_BATTERY:
                return self.pix_battery


    def createBarGraph(self, percent, agent_type, w=100, h=18):
        fw = w/100*percent
        px = QPixmap(w, h)
        pp = QPainter(px)
        pp.setBackgroundMode(Qt.OpaqueMode)
        pp.setPen(Qt.black)

        pp.setBackgroundColor(Qt.white)

        # erase the background
        b = QBrush(QColor(Qt.white))
        pp.fillRect(0, 0, w, h, b)

        # fill in the bar
        if agent_type in (AGENT_TYPE_BLACK, AGENT_TYPE_UNSPECIFIED):
            b = QBrush(QColor(Qt.black))
            pp.fillRect(0, 0, fw, h, b)
        elif agent_type == AGENT_TYPE_CMY:
            h3 = h/3
            b = QBrush(QColor(Qt.cyan))
            pp.fillRect(0, 0, fw, h3, b)
            b = QBrush(QColor(Qt.magenta))
            pp.fillRect(0, h3, fw, 2*h3, b)
            b = QBrush(QColor(Qt.yellow))
            pp.fillRect(0, 2*h3, fw, h, b)
        elif agent_type == AGENT_TYPE_KCM:
            h3 = h/3
            b = QBrush(QColor(Qt.cyan).light())
            pp.fillRect(0, 0, fw, h3, b)
            b = QBrush(QColor(Qt.magenta).light())
            pp.fillRect(0, h3, fw, 2*h3, b)
            b = QBrush(QColor(Qt.yellow).light())
            pp.fillRect(0, 2*h3, fw, h, b)
        elif agent_type == AGENT_TYPE_GGK:
            b = QBrush(QColor(Qt.gray))
            pp.fillRect(0, 0, fw, h, b)
        elif agent_type == AGENT_TYPE_YELLOW:
            b = QBrush(QColor(Qt.yellow))
            pp.fillRect(0, 0, fw, h, b)
        elif agent_type == AGENT_TYPE_MAGENTA:
            b = QBrush(QColor(Qt.magenta))
            pp.fillRect(0, 0, fw, h, b)
        elif agent_type == AGENT_TYPE_CYAN:
            b = QBrush(QColor(Qt.cyan))
            pp.fillRect(0, 0, fw, h, b)
        elif agent_type == AGENT_TYPE_CYAN_LOW:
            b = QBrush(QColor(225, 246, 255))
            pp.fillRect(0, 0, fw, h, b)
        elif agent_type == AGENT_TYPE_YELLOW_LOW:
            b = QBrush(QColor(255, 253, 225))
            pp.fillRect(0, 0, fw, h, b)
        elif agent_type == AGENT_TYPE_MAGENTA_LOW:
            b = QBrush(QColor(255, 225, 240))
            pp.fillRect(0, 0, fw, h, b)
        elif agent_type == AGENT_TYPE_BLUE:
            b = QBrush(QColor(0, 0, 255))
            pp.fillRect(0, 0, fw, h, b)
        elif agent_type == AGENT_TYPE_LG:
            b = QBrush(QColor(192, 192, 192))
            pp.fillRect(0, 0, fw, h, b)
        elif agent_type == AGENT_TYPE_PG:
            b = QBrush(QColor(128, 128, 128))
            pp.fillRect(0, 0, fw, h, b)

        # draw black frame
        pp.drawRect(0, 0, w, h)

        if percent > 75 and agent_type in \
          (AGENT_TYPE_BLACK, AGENT_TYPE_UNSPECIFIED, AGENT_TYPE_BLUE):
            pp.setPen(Qt.white)

        # 75% ticks
        w1 = 3*w/4
        h6 = h/6
        pp.drawLine(w1, 0, w1, h6)
        pp.drawLine(w1, h, w1, h-h6)

        if percent > 50 and agent_type in \
          (AGENT_TYPE_BLACK, AGENT_TYPE_UNSPECIFIED, AGENT_TYPE_BLUE):
            pp.setPen(Qt.white)

        # 50% ticks
        w2 = w/2
        h4 = h/4
        pp.drawLine(w2, 0, w2, h4)
        pp.drawLine(w2, h, w2, h-h4)

        if percent > 25 and agent_type in \
          (AGENT_TYPE_BLACK, AGENT_TYPE_UNSPECIFIED, AGENT_TYPE_BLUE):
            pp.setPen(Qt.white)

        # 25% ticks
        w4 = w/4
        pp.drawLine(w4, 0, w4, h6)
        pp.drawLine(w4, h, w4, h-h6)

        return px   


    def addItem(self, name, title_text, part_num_text, status_text, 
                agent_kind, agent_type, percent):

        num_items = len(self.items)
        LayoutWidget = QWidget(self.viewport(), name)
        LayoutWidget.setGeometry(QRect(0, 0, self.width(), self.row_height))
        LayoutWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))
        LayoutWidget.setPaletteBackgroundColor(qApp.palette().color(QPalette.Active, QColorGroup.Base))
        self.addChild(LayoutWidget)

        if num_items:
            self.moveChild(LayoutWidget, 0, self.row_height*num_items)

        layout = QGridLayout(LayoutWidget,1,1,10,10,"layout")
        textStatus = QLabel(LayoutWidget,"textStatus")
        layout.addWidget(textStatus,1,2)
        pixmapLevel = QLabel(LayoutWidget,"pixmapLevel")
        pixmapLevel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,
            pixmapLevel.sizePolicy().hasHeightForWidth()))

        pixmapLevel.setMinimumSize(QSize(100,20))
        pixmapLevel.setMaximumSize(QSize(100,20))
        layout.addWidget(pixmapLevel,2,2)
        textTitle = QLabel(LayoutWidget,"textTitle")
        layout.addWidget(textTitle,1,1)
        textPartNo = QLabel(LayoutWidget,"textPartNo")
        layout.addWidget(textPartNo,2,1)
        pixmapIcon = QLabel(LayoutWidget,"pixmapIcon")
        pixmapIcon.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,
            pixmapIcon.sizePolicy().hasHeightForWidth()))

        pixmapIcon.setMinimumSize(QSize(32,32))
        pixmapIcon.setMaximumSize(QSize(32,32))
        layout.addWidget(pixmapIcon,1,0)

        if num_items:
            line = QFrame(LayoutWidget,"line")
            line.setFrameShadow(QFrame.Sunken)
            line.setFrameShape(QFrame.HLine)
            line.setPaletteBackgroundColor(qApp.palette().color(QPalette.Active, QColorGroup.Foreground))
            layout.addMultiCellWidget(line,0,0,0,2)

        textTitle.setText(title_text)
        textPartNo.setText(part_num_text)
        textStatus.setText(status_text)

        # Bar graph level
        if agent_kind in (AGENT_KIND_SUPPLY,
                          #AGENT_KIND_HEAD,
                          AGENT_KIND_HEAD_AND_SUPPLY,
                          AGENT_KIND_TONER_CARTRIDGE,
                          AGENT_KIND_MAINT_KIT,
                          AGENT_KIND_ADF_KIT,
                          AGENT_KIND_INT_BATTERY,
                          AGENT_KIND_DRUM_KIT,
                          ):

            pixmapLevel.setPixmap(self.createBarGraph(percent, agent_type))

        # Color icon
        if agent_kind in (AGENT_KIND_SUPPLY,
                          AGENT_KIND_HEAD,
                          AGENT_KIND_HEAD_AND_SUPPLY,
                          AGENT_KIND_TONER_CARTRIDGE,
                          #AGENT_KIND_MAINT_KIT,
                          #AGENT_KIND_ADF_KIT,
                          AGENT_KIND_INT_BATTERY,
                          #AGENT_KIND_DRUM_KIT,
                          ):

            pix = self.getIcon(agent_kind, agent_type)

            if pix is not None:
                pixmapIcon.setPixmap(pix)

        self.resizeContents(self.width(), num_items*self.row_height*2)
        LayoutWidget.show()

        try:
            self.items[name]
        except KeyError:
            self.items[name] = LayoutWidget


    def clear(self):
        if len(self.items):
            for x in self.items:
                self.removeChild(self.items[x])
                self.items[x].hide()

            self.items.clear()
            self.resizeContents(self.width(), 0)



class IconViewItem(QIconViewItem):
    def __init__(self, parent, text, pixmap, device_uri, is_avail=True):
        QIconViewItem.__init__(self, parent, text, pixmap)
        self.device_uri = device_uri
        self.is_avail = is_avail



class devmgr4(DevMgr4_base):
    def __init__(self, hpiod_sock, hpssd_sock, 
                 cleanup=None, initial_device_uri=None,
                 parent=None, name=None, fl = 0):

        DevMgr4_base.__init__(self, parent, name, fl)

        icon = QPixmap(os.path.join(prop.image_dir, 'HPmenu.png'))
        self.setIcon(icon)

        log.debug("Initializing toolbox UI")
        self.cleanup = cleanup
        self.hpiod_sock = hpiod_sock
        self.hpssd_sock = hpssd_sock

        TabPageLayout = QGridLayout(self.FunctionsTab,1,1,11,6)

        self.ConfigureFeaturesButton = QPushButton(self.FunctionsTab)
        TabPageLayout.addWidget(self.ConfigureFeaturesButton,7,1)

        spacer1 = QSpacerItem(321,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TabPageLayout.addItem(spacer1,7,0)

        spacer2 = QSpacerItem(20,80,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout.addItem(spacer2,6,1)

        self.ScanButton = QPixmapLabelButton(self.FunctionsTab, QPixmap(os.path.join(prop.image_dir, "scan_icon.png")), 
            QPixmap(os.path.join(prop.image_dir, "scan_icon_disabled.png")))

        self.ScanButton.setMinimumSize(QSize(0,42))
        self.ScanButton.setEnabled(0)

        TabPageLayout.addMultiCellWidget(self.ScanButton,2,2,0,1)

        self.PCardButton = QPixmapLabelButton(self.FunctionsTab, QPixmap(os.path.join(prop.image_dir, "pcard_icon.png")), 
            QPixmap(os.path.join(prop.image_dir, "pcard_icon_disabled.png")))

        self.PCardButton.setMinimumSize(QSize(0,42))        
        self.PCardButton.setEnabled(0)

        TabPageLayout.addMultiCellWidget(self.PCardButton,3,3,0,1)

        self.SendFaxButton = QPixmapLabelButton(self.FunctionsTab, QPixmap(os.path.join(prop.image_dir, "fax_icon.png")), 
            QPixmap(os.path.join(prop.image_dir, "fax_icon_disabled.png")))

        self.SendFaxButton.setMinimumSize(QSize(0,42))
        self.SendFaxButton.setEnabled(0)

        TabPageLayout.addMultiCellWidget(self.SendFaxButton,4,4,0,1)

        self.MakeCopiesButton = QPixmapLabelButton(self.FunctionsTab, QPixmap(os.path.join(prop.image_dir, "makecopies_icon.png")), 
            QPixmap(os.path.join(prop.image_dir, "makecopies_icon_disabled.png")) )

        self.MakeCopiesButton.setMinimumSize(QSize(0,42))
        self.MakeCopiesButton.setEnabled(0)

        TabPageLayout.addMultiCellWidget(self.MakeCopiesButton,5,5,0,1)
        spacer3 = QSpacerItem(20,90,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout.addItem(spacer3, 0, 0)

        self.PrintButton = QPixmapLabelButton(self.FunctionsTab, QPixmap(os.path.join(prop.image_dir, "print_icon.png")), 
            QPixmap(os.path.join(prop.image_dir, "print_icon_disabled.png")))

        self.PrintButton.setMinimumSize(QSize(0,42))
        self.PrintButton.setEnabled(0)

        TabPageLayout.addMultiCellWidget(self.PrintButton,1,1,0,1)


        self.connect(self.PrintButton,SIGNAL("clicked()"),self.PrintButton_clicked)
        self.connect(self.ScanButton,SIGNAL("clicked()"),self.ScanButton_clicked)
        self.connect(self.PCardButton,SIGNAL("clicked()"),self.PCardButton_clicked)
        self.connect(self.SendFaxButton,SIGNAL("clicked()"),self.SendFaxButton_clicked)
        self.connect(self.MakeCopiesButton,SIGNAL("clicked()"),self.MakeCopiesButton_clicked)
        self.connect(self.ConfigureFeaturesButton,SIGNAL("clicked()"),self.ConfigureFeaturesButton_clicked)

        self.ConfigureFeaturesButton.setText(self.__tr("Configure..."))
        self.ScanButton.setText(self.__tr("Scan"))
        self.PCardButton.setText(self.__tr("Photo Card"))
        self.SendFaxButton.setText(self.__tr("Send Fax"))
        self.MakeCopiesButton.setText(self.__tr("Make Copies"))
        self.PrintButton.setText(self.__tr("Print"))

        self.StatusHistoryList.setSorting(-1)
        self.PrintJobList.setSorting(1) # Sort on job ID column
        self.DeviceList.setAutoArrange(False)
        self.StatusHistoryList.setColumnWidth(0, 16)
        self.StatusHistoryList.setColumnText(0, ' ')
        self.StatusHistoryList.setColumnWidthMode(1, QListView.Maximum)
        self.StatusHistoryList.setColumnWidthMode(2, QListView.Maximum)
        self.StatusHistoryList.setColumnWidthMode(3, QListView.Maximum)
        self.StatusHistoryList.setColumnWidthMode(4, QListView.Maximum)
        self.StatusHistoryList.setColumnWidthMode(5, QListView.Maximum)
        self.StatusHistoryList.setColumnWidthMode(6, QListView.Maximum)

        self.PrintJobList.setColumnWidth(0, 150)
        self.PrintJobList.setColumnWidthMode(0, QListView.Maximum)
        self.PrintJobList.setColumnWidth(1, 60)
        self.PrintJobList.setColumnWidthMode(1, QListView.Maximum)
        self.PrintJobList.setColumnWidth(2, 80)
        self.PrintJobList.setColumnWidthMode(2, QListView.Maximum)
        self.PrintJobList.setColumnWidth(3, 100)
        self.PrintJobList.setColumnWidthMode(3, QListView.Maximum)
        self.PrintJobList.setColumnWidth(4, 200)
        self.PrintJobList.setColumnWidthMode(4, QListView.Maximum)

        self.initial_device_uri = initial_device_uri

        self.warning_pix = QPixmap(os.path.join(prop.image_dir, "warning.png"))
        self.error_pix = QPixmap(os.path.join(prop.image_dir, "error.png"))
        self.ok_pix = QPixmap(os.path.join(prop.image_dir, "ok.png"))
        self.lowink_pix = QPixmap(os.path.join(prop.image_dir, 'inkdrop.png'))
        self.lowtoner_pix = QPixmap(os.path.join(prop.image_dir, 'toner.png'))
        self.busy_pix = QPixmap(os.path.join(prop.image_dir, 'busy.png'))
        self.lowpaper_pix = QPixmap(os.path.join(prop.image_dir, 'paper.png'))

        self.warning_pix_small = QPixmap(os.path.join(prop.image_dir, "warning_small.png"))
        self.error_pix_small = QPixmap(os.path.join(prop.image_dir, "error_small.png"))
        self.ok_pix_small = QPixmap(os.path.join(prop.image_dir, "ok_small.png"))
        self.lowink_pix_small = QPixmap(os.path.join(prop.image_dir, 'inkdrop_small.png'))
        self.lowtoner_pix_small = QPixmap(os.path.join(prop.image_dir, 'toner_small.png'))
        self.busy_pix_small = QPixmap(os.path.join(prop.image_dir, 'busy_small.png'))
        self.lowpaper_pix_small = QPixmap(os.path.join(prop.image_dir, 'paper_small.png'))

        self.blank_lcd = os.path.join(prop.image_dir, "panel_lcd.xpm")
        self.Panel.setPixmap(QPixmap(self.blank_lcd))

        # pixmaps: (inkjet, laserjet)
        self.STATUS_HISTORY_ICONS = { ERROR_STATE_CLEAR : (None, None),
                                      ERROR_STATE_BUSY : (self.busy_pix_small, self.busy_pix_small),
                                      ERROR_STATE_ERROR : (self.error_pix_small, self.error_pix_small),
                                      ERROR_STATE_LOW_SUPPLIES : (self.lowink_pix_small, self.lowtoner_pix_small),
                                      ERROR_STATE_OK : (self.ok_pix_small, self.ok_pix_small),
                                      ERROR_STATE_WARNING : (self.warning_pix_small, self.warning_pix_small),
                                      ERROR_STATE_LOW_PAPER: (self.lowpaper_pix_small, self.lowpaper_pix_small),
                                    }

        self.STATUS_ICONS = { ERROR_STATE_CLEAR : (None, None),
                              ERROR_STATE_BUSY : (self.busy_pix, self.busy_pix),
                              ERROR_STATE_ERROR : (self.error_pix, self.error_pix),
                              ERROR_STATE_LOW_SUPPLIES : (self.lowink_pix, self.lowtoner_pix),
                              ERROR_STATE_OK : (self.ok_pix, self.ok_pix),
                              ERROR_STATE_WARNING : (self.warning_pix, self.warning_pix),
                              ERROR_STATE_LOW_PAPER: (self.lowpaper_pix, self.lowpaper_pix),
                            }

        self.JOB_STATES = { 3 : self.__tr("Pending"),
                            4 : self.__tr("On hold"),
                            5 : self.__tr("Printing"),
                            6 : self.__tr("Stopped"),
                            7 : self.__tr("Canceled"),
                            8 : self.__tr("Aborted"),
                            9 : self.__tr("Completed"),
                           }

        self.email_alerts = utils.to_bool(user_cfg.alerts.email_alerts, False)
        self.email_to_addresses = user_cfg.alerts.email_to_addresses
        self.email_from_address = user_cfg.alerts.email_from_address
        self.auto_refresh = utils.to_bool(user_cfg.refresh.enable, False)

        try:
            self.auto_refresh_rate = int(user_cfg.refresh.rate)
        except ValueError:    
            self.auto_refresh_rate = DEF_AUTO_REFRESH_RATE

        try:
            self.auto_refresh_type = int(user_cfg.refresh.type)
        except ValueError:
            self.auto_refresh_type = 0 # refresh 1 (1=refresh all)

        cmd_print, cmd_scan, cmd_pcard, \
            cmd_copy, cmd_fax, cmd_fab = utils.deviceDefaultFunctions()

        self.cmd_print = user_cfg.commands.prnt or cmd_print
        self.cmd_scan = user_cfg.commands.scan or cmd_scan
        self.cmd_pcard = user_cfg.commands.pcard or cmd_pcard
        self.cmd_copy = user_cfg.commands.cpy or cmd_copy
        self.cmd_fax = user_cfg.commands.fax or cmd_fax
        self.cmd_fab = user_cfg.commands.fab or cmd_fab

        log.debug("HPLIP Version: %s" % sys_cfg.hplip.version)
        log.debug("Print command: %s" % self.cmd_print)
        log.debug("PCard command: %s" % self.cmd_pcard)
        log.debug("Fax command: %s" % self.cmd_fax)
        log.debug("FAB command: %s" % self.cmd_fab)
        log.debug("Copy command: %s " % self.cmd_copy)
        log.debug("Scan command: %s" % self.cmd_scan)
        log.debug("Email alerts: %s" % self.email_alerts)
        log.debug("Email to address(es): %s" % self.email_to_addresses)
        log.debug("Email from address: %s" % self.email_from_address)
        log.debug("Auto refresh: %s" % self.auto_refresh)
        log.debug("Auto refresh rate: %s" % self.auto_refresh_rate)
        log.debug("Auto refresh type: %s" % self.auto_refresh_type)

        if not self.auto_refresh:
            self.autoRefresh.toggle()

        self.cur_device_uri = user_cfg.last_used.device_uri # Device URI
        self.devices = {}    # { Device_URI : device.Device(), ... }
        self.device_vars = {}
        self.num_devices = 0
        self.cur_device = None
        self.rescanning = False

        # Add Scrolling Maintenance (Tools)
        self.ToolList = ScrollToolView(self.MaintTab, "ToolView")
        MaintTabLayout = QGridLayout(self.MaintTab,1,1,11,6,"MaintTabLayout")
        MaintTabLayout.addWidget(self.ToolList,0,0)

        # Add Scrolling Supplies 
        self.SuppliesList = ScrollSuppliesView(self.SuppliesTab, "SuppliesView")
        SuppliesTabLayout = QGridLayout(self.SuppliesTab,1,1,11,6,"SuppliesTabLayout")
        self.SuppliesList.setHScrollBarMode(QScrollView.AlwaysOff)
        SuppliesTabLayout.addWidget(self.SuppliesList,0,0)

        QTimer.singleShot(0, self.InitialUpdate)


    def InitialUpdate(self):
        self.RescanDevices()
        
        self.refresh_timer = QTimer(self, "RefreshTimer")
        self.connect(self.refresh_timer, SIGNAL('timeout()'), self.TimedRefresh)

        if MIN_AUTO_REFRESH_RATE <= self.auto_refresh_rate <= MAX_AUTO_REFRESH_RATE:
            self.refresh_timer.start(self.auto_refresh_rate * 1000)


    def TimedRefresh(self):
        if self.auto_refresh:
            log.debug("Refresh timer...")
            self.CleanupChildren()

            if self.auto_refresh_type == 0:
                self.UpdateDevice()
            else:
                self.RescanDevices()

    def autoRefresh_toggled(self,a0):
        self.auto_refresh = bool(a0)
        self.SaveConfig()


    def closeEvent(self, event):
        self.Cleanup()
        event.accept()


    def RescanDevices(self):
        if not self.rescanning:
            self.deviceRefreshAll.setEnabled(False)
            self.DeviceListRefresh()
            self.deviceRefreshAll.setEnabled(True)
                

    def ActivateDevice(self, device_uri):
        log.debug(utils.bold("Activate: %s %s %s" % ("*"*20, device_uri, "*"*20)))
        d = self.DeviceList.firstItem()
        found = False

        while d is not None:

            if d.device_uri == device_uri:
                found = True
                self.DeviceList.setSelected(d, True)
                break

            d = d.nextItem()

        return found        
                

    def Cleanup(self):
        self.CleanupChildren()
        if self.cleanup is not None:
            self.cleanup()


    def CleanupChildren(self):
        log.debug("Cleaning up child processes.")
        try:
            os.waitpid(-1, os.WNOHANG)
        except OSError:
            pass


    def DeviceList_currentChanged(self, a0):
        if not self.rescanning:
            try:
                self.cur_device_uri = self.DeviceList.currentItem().device_uri
                self.cur_device = self.devices[self.cur_device_uri]
                user_cfg.last_used.device_uri = self.cur_device_uri
            except AttributeError:
                pass

            self.UpdateDevice()


    def DeviceList_rightButtonClicked(self, item, pos):
        popup = QPopupMenu(self)

        if item is not None:
            if self.cur_device.error_state != ERROR_STATE_ERROR:
                popup.insertItem(self.__tr("Print..."), self.PrintButton_clicked)

                if self.cur_device.scan_type:
                    popup.insertItem(self.__tr("Scan..."), self.ScanButton_clicked)

                if self.cur_device.pcard_type:
                    popup.insertItem(self.__tr("Access Photo Cards..."), self.PCardButton_clicked)

                if self.cur_device.fax_type:
                    popup.insertItem(self.__tr("Send Fax..."), self.SendFaxButton_clicked)

                if self.cur_device.copy_type:
                    popup.insertItem(self.__tr("Make Copies..."), self.MakeCopiesButton_clicked)

                popup.insertSeparator()

            if self.cur_device.device_settings_ui is not None:
                popup.insertItem(self.__tr("Device Settings..."), self.deviceSettingsButton_clicked)

            popup.insertItem(self.__tr("Refresh Device"), self.UpdateDevice)

        popup.insertItem(self.__tr("Refresh All"), self.deviceRefreshAll_activated)

        popup.popup(pos)


    def UpdateDevice(self, check_state=True, reread_cups_printers=False):
        if self.cur_device is not None:
            log.debug(utils.bold("Update: %s %s %s" % ("*"*20, self.cur_device_uri, "*"*20)))
            self.setCaption(self.__tr("HP Device Manager - %1").arg(self.cur_device.model_ui))

            if not self.rescanning:
                self.statusBar().message(self.cur_device_uri)

            if self.cur_device.supported and check_state and not self.rescanning:
                QApplication.setOverrideCursor(QApplication.waitCursor)

                try:
                    try:
                        self.cur_device.open()
                    except Error, e:
                        log.warn(e.msg)

                    if self.cur_device.device_state == DEVICE_STATE_NOT_FOUND:
                        self.cur_device.error_state = ERROR_STATE_ERROR
                    else:
                        try:
                            self.cur_device.queryDevice(quick=False, no_fwd=False, reread_cups_printers=reread_cups_printers)
                        except Error, e:
                            log.error("Query device error (%s)." % e.msg)
                            self.cur_device.error_state = ERROR_STATE_ERROR

                finally:
                    self.cur_device.close()
                    QApplication.restoreOverrideCursor()

                log.debug("Device state = %d" % self.cur_device.device_state)
                log.debug("Status code = %d" % self.cur_device.status_code)
                log.debug("Error state = %d" % self.cur_device.error_state)

                icon = self.CreatePixmap()
                self.DeviceList.currentItem().setPixmap(icon)

            if not self.rescanning: 
                self.UpdateHistory()
                self.UpdateTabs()


    def CreatePixmap(self, dev=None):
        if dev is None:
            dev = self.cur_device

        try:
            pix = QPixmap(os.path.join(prop.image_dir, dev.icon))
        except AttributeError:
            pix = QPixmap(os.path.join(prop.image_dir, 'default_printer.png'))

        error_state = dev.error_state
        icon = QPixmap(pix.width(), pix.height())
        p = QPainter(icon)
        p.eraseRect(0, 0, icon.width(), icon.height())
        p.drawPixmap(0, 0, pix)

        try:
            tech_type = dev.tech_type
        except AttributeError:
            tech_type = TECH_TYPE_NONE

        if error_state != ERROR_STATE_CLEAR:
            if tech_type in (TECH_TYPE_COLOR_INK, TECH_TYPE_MONO_INK):
                status_icon = self.STATUS_HISTORY_ICONS[error_state][0] # ink
            else:
                status_icon = self.STATUS_HISTORY_ICONS[error_state][1] # laser

            if status_icon is not None:
                p.drawPixmap(0, 0, status_icon)

        p.end()

        return icon


    def DeviceListRefresh(self):
        log.debug("Rescanning device list...")

        if not self.rescanning:
            self.setCaption(self.__tr("Refreshing Device List - HP Device Manager"))
            self.statusBar().message(self.__tr("Refreshing device list..."))

            self.rescanning = True
            total_changes = 0
            total_steps = 0

            self.cups_devices = device.getSupportedCUPSDevices()

            QApplication.setOverrideCursor(QApplication.waitCursor)

            # TODO: Use Set() when 2.3+ is ubiquitous

            for d in self.cups_devices: # adds
                if d not in self.devices:
                    total_steps += 1
                    total_changes += 1

            updates = []
            for d in self.devices: # removes
                if d not in self.cups_devices:
                    total_steps += 1
                    total_changes += 1
                else:
                    # Don't update current device as it will be updated at end
                    if self.cur_device is not None and self.cur_device_uri != d:
                        updates.append(d) # updates
                        total_steps += 1

            log.debug("total changes = %d" % total_changes)

            step_num = 0
            pb = None

            if total_steps:
                pb = QProgressBar(self.statusBar(), 'ProgressBar')
                pb.setTotalSteps(total_changes + total_steps)
                self.statusBar().addWidget(pb)
                pb.show()

            if total_changes:
                # Item addition (device added to CUPS)
                for d in self.cups_devices: 
                    if d not in self.devices:
                        qApp.processEvents()
                        log.debug("adding: %s" % d)

                        pb.setProgress(step_num)
                        step_num += 1
                        qApp.processEvents()

                        log.debug(utils.bold("Refresh: %s %s %s" % \
                            ("*"*20, d, "*"*20)))

                        try:
                            dev = device.Device(d,
                                                hpiod_sock=self.hpiod_sock,
                                                hpssd_sock=self.hpssd_sock,
                                                callback=self.callback)
                        except Error:
                            log.error("Unexpected error in Device class.")
                            log.exception()
                            return

                        try:
                            try:
                                dev.open()
                            except Error, e:
                                log.warn(e.msg)

                            if dev.device_state == DEVICE_STATE_NOT_FOUND:
                                dev.error_state = ERROR_STATE_ERROR
                            else:
                                dev.queryDevice(quick=True) #, no_fwd=True)

                        finally:
                            dev.close()

                        self.CheckForDeviceSettingsUI(dev)

                        icon = self.CreatePixmap(dev)

                        IconViewItem(self.DeviceList, dev.model_ui,
                                     icon, d)

                        self.devices[d] = dev


                # Item removal (device removed from CUPS)
                for d in self.devices.keys():
                    if d not in self.cups_devices:
                        qApp.processEvents()
                        item = self.DeviceList.firstItem()
                        log.debug("removing: %s" % d)

                        pb.setProgress(step_num)
                        step_num += 1
                        qApp.processEvents()

                        while item is not None:
                            if item.device_uri == d:
                                self.DeviceList.takeItem(item)
                                del self.devices[d]
                                break

                            item = item.nextItem()



            # Item updates
            for d in updates:
                log.debug("updating: %s" % d)
                qApp.processEvents()
                dev = self.devices[d]

                pb.setProgress(step_num)
                step_num += 1
                qApp.processEvents()

                prev_error_state = dev.error_state

                try:
                    try:
                        dev.open()
                    except Error, e:
                        log.warn(e.msg)

                    if dev.device_state == DEVICE_STATE_NOT_FOUND:
                        dev.error_state = ERROR_STATE_ERROR
                    else:
                        dev.queryDevice(quick=True) #, no_fwd=True)

                finally:
                    dev.close()

                if dev.error_state != prev_error_state:
                    item = self.DeviceList.firstItem()

                    while item is not None:
                        if item.device_uri == d:
                            item.setPixmap(self.CreatePixmap(dev))
                            break

                        item = item.nextItem()

            if pb is not None:
                pb.hide()
                self.statusBar().removeWidget(pb)
                pb = None

            if not len(self.cups_devices):
                QApplication.restoreOverrideCursor()
                self.cur_device = None
                self.deviceRescanAction.setEnabled(False)
                self.deviceRemoveAction.setEnabled(False)
                self.rescanning = False
                self.UpdateTabs()
                self.statusBar().message(self.__tr("Press F6 to refresh."))
                dlg = NoDevicesForm(self, "", True)
                dlg.show()
                return

            # Select current item
            self.rescanning = False
            
            if self.cur_device_uri:
                item = self.DeviceList.firstItem()

                while item is not None:
                    qApp.processEvents()
                    if item.device_uri == self.cur_device_uri:
                        self.DeviceList.setCurrentItem(item)
                        self.DeviceList.setSelected(item, True)
                        break

                    item = item.nextItem()

                else:
                    self.cur_device = None
                    self.cur_device_uri = ''

            if not self.cur_device_uri:
                self.cur_device_uri = self.DeviceList.firstItem().device_uri
                self.cur_device = self.devices[self.cur_device_uri]
                self.DeviceList.setCurrentItem(self.DeviceList.firstItem())
                
                user_cfg.last_used.device_uri = self.cur_device_uri

            self.DeviceList.adjustItems()
            self.DeviceList.updateGeometry()

            self.deviceRescanAction.setEnabled(True)
            self.deviceRemoveAction.setEnabled(True)

            QApplication.restoreOverrideCursor()


    def callback(self):
        pass

    def CheckForDeviceSettingsUI(self, dev):
        dev.device_settings_ui = None
        name = '.'.join(['plugins', dev.model])
        log.debug("Attempting to load plugin: %s" % name)
        try:
            mod = __import__(name, globals(), locals(), [])
        except ImportError:
            log.debug("No plugin found.")
            return
        else:
            components = name.split('.')
            for c in components[1:]:
                mod = getattr(mod, c)
            log.debug("Loaded: %s" % repr(mod))
            dev.device_settings_ui = mod.settingsUI

    def UpdateTabs(self):
        self.UpdateFunctionsTab()
        self.UpdateStatusTab()
        self.UpdateSuppliesTab()
        self.UpdateMaintTab()
        self.UpdatePrintJobsTab()
        self.UpdatePanelTab()

    def UpdatePrintJobsTab(self):
        self.PrintJobList.clear()
        num_jobs = 0

        if self.cur_device is not None and \
            self.cur_device.supported:

            jobs = cups.getJobs()

            for j in jobs:
                if j.dest in self.cur_device.cups_printers:

                    JobListViewItem(self.PrintJobList, j.dest, j.id,
                                     self.JOB_STATES[j.state], j.user, j.title)

                    num_jobs += 1

        self.CancelPrintJobButton.setEnabled(num_jobs > 0)


    def PrintJobList_currentChanged(self, item):
        pass


    def PrintJobList_selectionChanged(self, a0):
        pass


    def CancelPrintJobButton_clicked(self):
        item = self.PrintJobList.currentItem()
        if item is not None:
            QApplication.setOverrideCursor(QApplication.waitCursor)
            self.cur_device.cancelJob(item.job_id)
            time.sleep(1)
            QApplication.restoreOverrideCursor()
            
            self.UpdateDevice()

    def UpdatePanelTab(self):
        if self.cur_device is not None:
            dq = self.cur_device.dq

            if dq.get('panel', 0) == 1:
                line1 = dq.get('panel-line1', '')
                line2 = dq.get('panel-line2', '')
                self.Tabs.setTabEnabled(self.PanelTab, True)
            else:
                line1 = self.__tr("Front panel display")
                line2 = self.__tr("not available.")
                self.Tabs.setTabEnabled(self.PanelTab, False)

            pm = QPixmap(self.blank_lcd)

            p = QPainter()
            p.begin(pm)
            p.setPen(QColor(0, 0, 0))
            p.setFont(self.font())

            x, y_line1, y_line2 = 10, 17, 33

            # TODO: Scroll long lines
            p.drawText(x, y_line1, line1)
            p.drawText(x, y_line2, line2)
            p.end()

            self.Panel.setPixmap(pm)

        else:
            self.Panel.setPixmap(QPixmap(self.blank_lcd))


    def UpdateFunctionsTab(self):
        self.ToggleFunctionButtons(self.cur_device is not None and \
            self.cur_device.device_state in (DEVICE_STATE_FOUND, DEVICE_STATE_JUST_FOUND))


    def ToggleFunctionButtons(self, toggle):
        if toggle:
            self.PrintButton.setEnabled(True)
            self.ScanButton.setEnabled(self.cur_device.scan_type)
            self.PCardButton.setEnabled(self.cur_device.pcard_type)
            self.SendFaxButton.setEnabled(self.cur_device.fax_type)
            self.MakeCopiesButton.setEnabled(self.cur_device.copy_type)
            #self.MakeCopiesButton.setEnabled(False)
        else:
            self.PrintButton.setEnabled(False)
            self.ScanButton.setEnabled(False)
            self.PCardButton.setEnabled(False)
            self.SendFaxButton.setEnabled(False)
            self.MakeCopiesButton.setEnabled(False)


    def UpdateHistory(self):
        try:
            self.cur_device.hist = self.cur_device.queryHistory()
            self.cur_device.hist.reverse()
        except Error:
            log.error("History query failed.")
            self.cur_device.last_event = None
            self.cur_device.error_state = ERROR_STATE_ERROR
            self.cur_device.status_code = STATUS_UNKNOWN
        else:
            try:
                self.cur_device.last_event = self.cur_device.hist[-1]
            except IndexError:
                self.cur_device.last_event = None
                self.cur_device.error_state = ERROR_STATE_ERROR
                self.cur_device.status_code = STATUS_UNKNOWN


    def UpdateStatusTab(self):
        self.StatusHistoryList.clear()
        d = self.cur_device

        if d is not None:
            for x in d.hist:
                job_id, code = x[9], x[11]

                if job_id == 0:
                    i = QListViewItem(self.StatusHistoryList, '',
                                       time.strftime("%x", x[:9]),
                                       time.strftime("%H:%M:%S", x[:9]),
                                       '', '', str(code), x[12])

                else:
                    i = QListViewItem(self.StatusHistoryList, '',
                                   time.strftime("%x", x[:9]),
                                   time.strftime("%H:%M:%S", x[:9]),
                                   x[10], str(job_id), str(code), x[12])

                error_state = STATUS_TO_ERROR_STATE_MAP.get(code, ERROR_STATE_CLEAR)

                try:
                    tech_type = d.tech_type
                except AttributeError:
                    tech_type = TECH_TYPE_NONE

                if error_state != ERROR_STATE_CLEAR:
                    if tech_type in (TECH_TYPE_COLOR_INK, TECH_TYPE_MONO_INK):
                        status_pix = self.STATUS_HISTORY_ICONS[error_state][0] # ink
                    else:
                        status_pix = self.STATUS_HISTORY_ICONS[error_state][1] # laser

                    if status_pix is not None:
                        i.setPixmap(0, status_pix)

            if d.last_event is not None:
                self.StatusText.setText(d.last_event[12])
                self.StatusText2.setText(d.last_event[13])

                error_state = STATUS_TO_ERROR_STATE_MAP.get(d.last_event[11], ERROR_STATE_CLEAR)

                if error_state != ERROR_STATE_CLEAR:
                    if tech_type in (TECH_TYPE_COLOR_INK, TECH_TYPE_MONO_INK):
                        status_icon = self.STATUS_ICONS[error_state][0] # ink
                    else:
                        status_icon = self.STATUS_ICONS[error_state][1] # laser

                    if status_icon is not None:
                        self.StatusIcon.setPixmap(status_icon)
                    else:
                        self.StatusIcon.clear()
                else:
                    self.StatusIcon.clear()
        else:
            self.StatusIcon.clear()
            self.StatusText.setText('')
            self.StatusText2.setText('')


    def UpdateSuppliesTab(self):
        self.SuppliesList.clear()

        if self.cur_device is not None and \
            self.cur_device.supported and \
            self.cur_device.status_type != STATUS_TYPE_NONE:

            try:
                self.cur_device.sorted_supplies
            except AttributeError:                
                self.cur_device.sorted_supplies = []

            if not self.cur_device.sorted_supplies:
                a = 1
                while True:
                    try:
                        agent_type = int(self.cur_device.dq['agent%d-type' % a])
                        agent_kind = int(self.cur_device.dq['agent%d-kind' % a])
                    except KeyError:
                        break
                    else:
                        self.cur_device.sorted_supplies.append((a, agent_kind, agent_type))

                    a += 1

                self.cur_device.sorted_supplies.sort(lambda x, y: cmp(x[2], y[2]) or cmp(x[1], y[1]))

            for x in self.cur_device.sorted_supplies:
                a, agent_kind, agent_type = x
                agent_level = int(self.cur_device.dq['agent%d-level' % a])
                agent_sku = str(self.cur_device.dq['agent%d-sku' % a])
                agent_desc = self.cur_device.dq['agent%d-desc' % a]
                agent_health_desc = self.cur_device.dq['agent%d-health-desc' % a]

                self.SuppliesList.addItem("agent %d" % a, "<b>"+agent_desc+"</b>",
                                          agent_sku, agent_health_desc, 
                                          agent_kind, agent_type, agent_level) 


    def UpdateMaintTab(self):
        self.ToolList.clear()

        if self.cur_device is not None and \
            self.cur_device.supported and \
            self.cur_device.device_state in (DEVICE_STATE_FOUND, DEVICE_STATE_JUST_FOUND):

            self.ToolList.addItem( "cups", self.__tr("<b>Configure Print Settings</b>"), 
                QPixmap(os.path.join(prop.image_dir, 'icon_cups.png')), 
                self.__tr("Use this interface to configure printer settings such as print quality, print mode, paper size, etc. (Note: This may not work on all operating systems)"), 
                self.__tr("Configure..."), 
                self.ConfigurePrintSettings_clicked)

            if self.cur_device.device_settings_ui is not None:
                self.ToolList.addItem( "device_settings", self.__tr("<b>Device Settings</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_settings.png')), 
                    self.__tr("Your device has special device settings. You may alter these settings here."), 
                    self.__tr("Device Settings..."), 
                    self.deviceSettingsButton_clicked)
                self.setupDevice.setEnabled(True)
            else:
                self.setupDevice.setEnabled(False)

            if self.cur_device.fax_type:
                self.ToolList.addItem( "fax_settings", self.__tr("<b>Fax Setup</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_fax.png')), 
                    self.__tr("Fax support must be setup before you can send faxes."), 
                    self.__tr("Setup Fax..."), 
                    self.faxSettingsButton_clicked)

                self.ToolList.addItem( "fax_address_book", self.__tr("<b>Fax Address Book</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_fax.png')), 
                    self.__tr("Setup fax phone numbers to use when sending faxes from the PC."), 
                    self.__tr("Fax Address Book..."), 
                    self.faxAddressBookButton_clicked)


            self.ToolList.addItem( "testpage", self.__tr("<b>Print Test Page</b>"), 
                QPixmap(os.path.join(prop.image_dir, 'icon_testpage.png')), 
                self.__tr("Print a test page to test the setup of your printer."), 
                self.__tr("Print Test Page..."), 
                self.PrintTestPageButton_clicked)


            self.ToolList.addItem( "info", self.__tr("<b>View Device Information</b>"), 
                QPixmap(os.path.join(prop.image_dir, 'icon_info.png')), 
                self.__tr("This information is primarily useful for debugging and troubleshooting."), 
                self.__tr("View Information..."), 
                self.viewInformation) 

            if self.cur_device.pq_diag_type:
                self.ToolList.addItem( "pqdiag", self.__tr("<b>Print Quality Diagnostics</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_pq_diag.png')),
                    self.__tr("Your printer can print a test page to help diagnose print quality problems."), 
                    self.__tr("Print Diagnostic Page..."), 
                    self.pqDiag)

            if self.cur_device.fw_download:
                self.ToolList.addItem( "fwdownload", self.__tr("<b>Download Firmware</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'download.png')),
                    self.__tr("Download firmware to your printer (required on some devices after each power-up)."), 
                    self.__tr("Download Firmware..."), 
                    self.downloadFirmware)


            if self.cur_device.clean_type:
                self.ToolList.addItem( "clean", self.__tr("<b>Clean Cartridges</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_clean.png')), 
                    self.__tr("You only need to perform this action if you are having problems with poor printout quality due to clogged ink nozzles."), 
                    self.__tr("Clean Cartridges..."), 
                    self.CleanPensButton_clicked)

            if self.cur_device.align_type:
                self.ToolList.addItem( "align", self.__tr("<b>Align Cartridges</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_align.png')), 
                    self.__tr("This will improve the quality of output when a new cartridge is installed."), 
                    self.__tr("Align Cartridges..."), 
                    self.AlignPensButton_clicked)

            if self.cur_device.color_cal_type:
                self.ToolList.addItem( "colorcal", self.__tr("<b>Perform Color Calibration</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_colorcal.png')), 
                    self.__tr("Use this procedure to optimimize your printer's color output."), 
                    self.__tr("Color Calibration..."), 
                    self.ColorCalibrationButton_clicked)

            if self.cur_device.linefeed_cal_type:
                self.ToolList.addItem( "linefeed", self.__tr("<b>Perform Line Feed Calibration</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_linefeed_cal.png')),
                    self.__tr("Use line feed calibration to optimize print quality (to remove gaps in the printed output)."), 
                    self.__tr("Line Feed Calibration..."), 
                    self.linefeedCalibration) 

            if self.cur_device.embedded_server_type and self.cur_device.bus == 'net':
                self.ToolList.addItem( "ews", self.__tr("<b>Access Embedded Web Page</b>"), 
                    QPixmap(os.path.join(prop.image_dir, 'icon_ews.png')), 
                    self.__tr("You can use your printer's embedded web server to configure, maintain, and monitor the device from a web browser. <i>This feature is only available if the device is connected via the network.</i>"),
                    self.__tr("Open in Browser..."), 
                    self.OpenEmbeddedBrowserButton_clicked)

        self.ToolList.addItem("support",  self.__tr("<b>View Documentation</b>"), 
            QPixmap(os.path.join(prop.image_dir, 'icon_support2.png')), 
            self.__tr("View documentation installed on your system."), 
            self.__tr("View Documentation..."), 
            self.viewSupport) 


    def viewSupportAction_activated(self):
        self.viewSupport()

    def ConfigurePrintSettings_clicked(self):
        d = self.cur_device
        printer_name = d.cups_printers[0]

        if len(d.cups_printers) > 1:
            from chooseprinterdlg import ChoosePrinterDlg2
            dlg = ChoosePrinterDlg2(d.cups_printers)

            if dlg.exec_loop() == QDialog.Accepted:
                printer_name = dlg.printer_name
            else:
                return

        utils.openURL("http://localhost:631/admin/?op=set-printer-options&printer_name=%s" % printer_name)

    def viewInformation(self):
        InformationForm(self.cur_device, self).exec_loop()

    def viewSupport(self):
        f = "file://%s" % os.path.join(sys_cfg.dirs.doc, 'index.html')
        log.debug(f)
        utils.openURL(f)


    def pqDiag(self):
        d = self.cur_device
        ok = False;
        pq_diag = d.pq_diag_type

        try:
            QApplication.setOverrideCursor(QApplication.waitCursor)
            d.open()

            if d.isIdleAndNoError():
                QApplication.restoreOverrideCursor()

                if pq_diag == 1:
                    maint.printQualityDiagType1(d, self.LoadPaperUI)

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


    def linefeedCalibration(self):
        d = self.cur_device
        ok = False;
        linefeed_type = d.linefeed_cal_type

        try:
            QApplication.setOverrideCursor(QApplication.waitCursor)
            d.open()

            if d.isIdleAndNoError():
                QApplication.restoreOverrideCursor()

                if linefeed_type == 1:
                    maint.linefeedCalType1(d, self.LoadPaperUI)

            else:
                self.CheckDeviceUI()

        finally:
            d.close()
            QApplication.restoreOverrideCursor()


    def viewInformation(self):
        InformationForm(self.cur_device, self).exec_loop()

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

            else:
                self.CheckDeviceUI()

        finally:
            d.close()
            QApplication.restoreOverrideCursor()


    def settingsConfigure_activated(self, tab_to_show=0):
        dlg = SettingsDialog(self.hpssd_sock, self)

        dlg.autoRefreshCheckBox.setChecked(self.auto_refresh)
        dlg.AutoRefreshRate.setValue(self.auto_refresh_rate) # min
        dlg.refreshScopeButtonGroup.setButton(self.auto_refresh_type)
        dlg.auto_refresh_type = self.auto_refresh_type

        dlg.EmailCheckBox.setChecked(self.email_alerts)
        dlg.EmailAddress.setText(self.email_to_addresses)
        dlg.senderLineEdit.setText(self.email_from_address)

        dlg.PrintCommand.setText(self.cmd_print)
        dlg.ScanCommand.setText(self.cmd_scan)
        dlg.AccessPCardCommand.setText(self.cmd_pcard)
        dlg.SendFaxCommand.setText(self.cmd_fax)
        dlg.MakeCopiesCommand.setText(self.cmd_copy)


        dlg.TabWidget.setCurrentPage(tab_to_show)

        if dlg.exec_loop() == QDialog.Accepted:

            self.cmd_print = str(dlg.PrintCommand.text())
            self.cmd_scan = str(dlg.ScanCommand.text())
            self.cmd_pcard = str(dlg.AccessPCardCommand.text())
            self.cmd_fax   = str(dlg.SendFaxCommand.text())
            self.cmd_copy  = str(dlg.MakeCopiesCommand.text())


            self.email_alerts = bool(dlg.EmailCheckBox.isChecked())
            self.email_to_addresses = str(dlg.EmailAddress.text())
            self.email_from_address = str(dlg.senderLineEdit.text())

            old_auto_refresh = self.auto_refresh
            self.auto_refresh = bool(dlg.autoRefreshCheckBox.isChecked())
            new_refresh_value = int(dlg.AutoRefreshRate.value())
            self.auto_refresh_type = dlg.auto_refresh_type

            if self.auto_refresh and new_refresh_value != self.auto_refresh_rate:
                    self.auto_refresh_rate = new_refresh_value
                    self.refresh_timer.changeInterval(self.auto_refresh_rate * 1000)

            if old_auto_refresh != self.auto_refresh:
                self.autoRefresh.toggle()

            self.SetAlerts()
            self.SaveConfig()


    def SetAlerts(self):
        service.setAlerts(self.hpssd_sock,
                          self.email_alerts,
                          self.email_to_addresses,
                          self.email_from_address)


    def SaveConfig(self):
        user_cfg.commands.prnt = self.cmd_print
        user_cfg.commands.pcard = self.cmd_pcard
        user_cfg.commands.fax = self.cmd_fax
        user_cfg.commands.scan = self.cmd_scan
        user_cfg.commands.cpy = self.cmd_copy
        user_cfg.alerts.email_to_addresses = self.email_to_addresses
        user_cfg.alerts.email_from_address = self.email_from_address
        user_cfg.alerts.email_alerts = self.email_alerts
        user_cfg.refresh.enable = self.auto_refresh
        user_cfg.refresh.rate = self.auto_refresh_rate
        user_cfg.refresh.type = self.auto_refresh_type


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

        log.debug(utils.bold("Align: %s %s (type=%d) %s" % ("*"*20, self.cur_device_uri, align_type, "*"*20)))

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
        log.debug(utils.bold("Color-cal: %s %s (type=%d) %s" % ("*"*20, self.cur_device_uri, color_cal_type, "*"*20)))

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
        log.debug(utils.bold("Clean: %s %s (type=%d) %s" % ("*"*20, self.cur_device_uri, clean_type, "*"*20)))

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


    def deviceRescanAction_activated(self):
        self.deviceRescanAction.setEnabled(False)
        self.UpdateDevice()
        self.deviceRescanAction.setEnabled(True)


    def deviceRefreshAll_activated(self):
        self.RescanDevices()


    def DeviceList_clicked(self,a0):
        pass


    def OpenEmbeddedBrowserButton_clicked(self):
        utils.openURL("http://%s" % self.cur_device.host)

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
        if self.cur_device.copy_type:
            self.RunCommand(self.cmd_copy)

    def ConfigureFeaturesButton_clicked(self):
        self.settingsConfigure_activated(2)

    def RunCommand(self, cmd, macro_char='%'):
        QApplication.setOverrideCursor(QApplication.waitCursor)

        try:
            self.ToggleFunctionButtons(False)
            if len(cmd) == 0:
                self.FailureUI(self.__tr("<p><b>Unable to run command. No command specified.</b><p>Use <pre>Configure...</pre> to specify a command to run."))
                log.error("No command specified. Use settings to configure commands.")
            else:
                log.debug(utils.bold("Run: %s %s (%s) %s" % ("*"*20, cmd, self.cur_device_uri, "*"*20)))
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


            self.ToggleFunctionButtons(True)

        finally:
            QApplication.restoreOverrideCursor()

    def faxAddressBookButton_clicked(self):
        self.RunCommand(self.cmd_fab)

    def helpAbout(self):
        dlg = AboutDlg(self)
        dlg.VersionText.setText(prop.version)
        dlg.exec_loop()

    def deviceSettingsButton_clicked(self):
        try:
            self.cur_device.open()
            self.cur_device.device_settings_ui(self.cur_device, self)
        finally:
            self.cur_device.close()

    def setupDevice_activated(self):
        self.cur_device.device_settings_ui(self.cur_device, self)

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

    def helpContents(self):
        f = "file://%s" % os.path.join(sys_cfg.dirs.doc, 'index.html')
        log.debug(f)
        utils.openURL(f)

    def deviceInstallAction_activated(self):
        su_sudo = None
        if utils.which('kdesu'):
            su_sudo = 'kdesu -- "%s"'

        elif utils.which('gksu'):
            su_sudo = 'gksu "%s"'

        if su_sudo is None:
            QMessageBox.critical(self,
                                self.caption(),
                                self.__tr("<b>Unable to find an appropriate su/sudo utility to run hp-setup.</b>"),
                                QMessageBox.Ok,
                                QMessageBox.NoButton,
                                QMessageBox.NoButton)
        else:
            if utils.which('hp-setup'):
                c = 'hp-setup -u --username=%s' % prop.username
                cmd = su_sudo % c
            else:
                c = 'python ./setup.py -u --username=%s' % prop.username
                cmd = su_sudo % c

            log.debug(cmd)
            status, output = utils.run(cmd, log_output=True, password_func=None, timeout=1)
            
            self.cur_device_uri = Config(prop.user_config_file).last_used.device_uri
            
            self.RescanDevices()


    def deviceRemoveAction_activated(self):
        if self.cur_device is not None:
            QApplication.setOverrideCursor(QApplication.waitCursor)
            print_uri = self.cur_device.device_uri
            fax_uri = print_uri.replace('hp:', 'hpfax:')

            log.debug(print_uri)
            log.debug(fax_uri)

            self.cups_devices = device.getSupportedCUPSDevices(['hp', 'hpfax'])

            for d in self.cups_devices:
                if d in (print_uri, fax_uri):
                    for p in self.cups_devices[d]:
                        log.debug("Removing %s" % p)
                        cups.delPrinter(p)

            self.cur_device = None
            self.cur_device_uri = ''
            user_cfg.last_used.device_uri = ''

            QApplication.restoreOverrideCursor()

            self.RescanDevices()


    def __tr(self,s,c = None):
        return qApp.translate("DevMgr4",s,c)
