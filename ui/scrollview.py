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

# Qt
from qt import *


class ScrollView(QScrollView):
    def __init__(self,parent = None,name = None,fl = 0):
        QScrollView.__init__(self,parent,name,fl)
        self.items = {}
        self.enableClipper(True)
        self.viewport().setPaletteBackgroundColor(qApp.palette().color(QPalette.Active, QColorGroup.Base))
        self.cur_device = None
        self.cur_printer = None
        self.item_margin = 2
        self.y = 0

    def getWidget(self):
        widget = QWidget(self.viewport(),"widget")
        widget.setPaletteBackgroundColor(qApp.palette().color(QPalette.Active, QColorGroup.Base))
        widget.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        widget.resize(self.visibleWidth(), self.size().height())
        widget.setMinimumWidth(self.visibleWidth())
        widget.resize(self.viewport().size().width(), self.size().height())
        return widget

    def viewportResizeEvent(self, e):
        QScrollView.viewportResizeEvent(self, e)

        total_height = 0
        for w in self.items:
            self.items[w].resize(e.size().width(), self.items[w].size().height())
            self.items[w].setMinimumWidth(e.size().width())
            total_height += (self.items[w].size().height() + self.item_margin)

        self.resizeContents(e.size().width(), total_height)

    def onDeviceChange(self, cur_device=None):
        if cur_device is not None:
            self.cur_device = cur_device

        if self.cur_device is not None and self.cur_device.supported:
            self.cur_printer = self.cur_device.cups_printers[0]

            QApplication.setOverrideCursor(QApplication.waitCursor)
            try:
                try:
                    self.fillControls()
                except Exception, e:
                    log.exception()
            finally:
                QApplication.restoreOverrideCursor()
        
        else:
            self.y = 0
            self.clear()

    def fillControls(self):
        self.y = 0
        self.clear()

    def onPrinterChange(self, printer_name):
        if printer_name == self.cur_printer:
            return
        
        self.cur_printer = str(printer_name)
        
        if self.cur_device is not None and self.cur_device.supported:
            QApplication.setOverrideCursor(QApplication.waitCursor)
            try:
                try:
                    self.fillControls()
                except Exception, e:
                    log.exception()
            finally:
                QApplication.restoreOverrideCursor()
        
        else:
            self.y = 0
            self.clear()

    def addControl(self, widget, key):
        key = "c:" + key
        try:
            self.items[key]
        except KeyError:
            self.items[key] = widget
            widget.setMinimumWidth(self.visibleWidth())
            widget.adjustSize()
            self.addChild(widget, 0, self.y)
            self.y += (widget.size().height() + self.item_margin)
            self.resizeContents(self.visibleWidth(), self.y)

            widget.show()
        else:
            log.error("ERROR: Duplicate control name: %s" % key)

    def clear(self):
        if len(self.items):
            for x in self.items:
                self.removeChild(self.items[x])
                self.items[x].hide()

            self.items.clear()

    def addGroupHeading(self, group, heading, read_only=False):
        widget = self.getWidget()
        layout = QGridLayout(widget,1,1,5,10,"layout10")

        self.textLabel2 = QLabel(widget,"textLabel2")
        #layout.addWidget(self.textLabel2,0,0)
        self.textLabel2.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred,0,0,
            self.textLabel2.sizePolicy().hasHeightForWidth()))
        
        layout.addMultiCellWidget(self.textLabel2,0,0,0,3)

        line = QFrame(widget,"line")
        #line.setFrameShadow(QFrame.Sunken)
        line.setFrameShape(QFrame.HLine)
        #line.setPaletteBackgroundColor(qApp.palette().color(QPalette.Active, QColorGroup.Foreground))
        layout.addMultiCellWidget(line,1,1,0,3)

        if read_only:
            self.textLabel2.setText(self.__tr("<b>%1 (read only)</b>").arg(heading))
        else:
            self.textLabel2.setText(QString("<b>%1</b>").arg(heading))

        self.addControl(widget, "g:"+group)

    def __tr(self,s,c = None):
        return qApp.translate("DevMgr4",s,c)
