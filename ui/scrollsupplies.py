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
from prnt import cups

# Qt
from qt import *
from scrollview import ScrollView

# Std Lib
import os.path, os



class ScrollSuppliesView(ScrollView):
    def __init__(self,parent = None,name = None,fl = 0):
        ScrollView.__init__(self,parent,name,fl)

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
        self.pix_black_and_yellow = QPixmap(os.path.join(prop.image_dir, 'icon_black_and_yellow.png'))
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
                               AGENT_TYPE_C_M: self.pix_photo_cyan_and_photo_magenta,
                               AGENT_TYPE_K_Y: self.pix_black_and_yellow,
                               }

    def fillControls(self):
        ScrollView.fillControls(self)
        
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

                self.addItem("agent %d" % a, "<b>"+agent_desc+"</b>",
                                          agent_sku, agent_health_desc, 
                                          agent_kind, agent_type, agent_level)                                


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

        widget = self.getWidget()
        layout1 = QGridLayout(widget,1,1,10,5,"layout1")

        spacer1 = QSpacerItem(31,20,QSizePolicy.Preferred,QSizePolicy.Minimum)
        layout1.addItem(spacer1,0,3)

        barGraph = QLabel(widget,"barGraph")
        barGraph.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,
            barGraph.sizePolicy().hasHeightForWidth()))

        barGraph.setMinimumSize(QSize(100,18))
        barGraph.setMaximumSize(QSize(100,18))
        barGraph.setScaledContents(1)
        layout1.addMultiCellWidget(barGraph,0,0,4,5)

        titleText = QLabel(widget,"titleText")
        layout1.addMultiCellWidget(titleText,0,0,0,2)

        line1 = QFrame(widget,"line1")
        line1.setFrameShape(QFrame.HLine)
        layout1.addMultiCellWidget(line1,2,2,0,5)

        spacer2 = QSpacerItem(190,20,QSizePolicy.Preferred,QSizePolicy.Minimum)
        layout1.addMultiCell(spacer2,1,1,2,4)

        statusText = QLabel(widget,"statusText")
        layout1.addWidget(statusText,1,5)

        icon = QLabel(widget,"icon")
        icon.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,
            icon.sizePolicy().hasHeightForWidth()))

        icon.setMinimumSize(QSize(32,32))
        icon.setMaximumSize(QSize(32,32))
        icon.setScaledContents(1)
        layout1.addWidget(icon,1,0)

        partNumText = QLabel(widget,"partNumText")
        partNumText.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred,0,0,
            partNumText.sizePolicy().hasHeightForWidth()))

        partNumText.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter)
        layout1.addWidget(partNumText,1,1)                

        titleText.setText(title_text)
        partNumText.setText(part_num_text)
        statusText.setText(status_text)

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

            barGraph.setPixmap(self.createBarGraph(percent, agent_type))

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
                icon.setPixmap(pix)

        self.addControl(widget, name)


    def __tr(self,s,c = None):
        return qApp.translate("DevMgr4",s,c)

