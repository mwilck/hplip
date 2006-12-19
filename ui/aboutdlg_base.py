# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'aboutdlg_base.ui'
#
# Created: Wed Nov 8 15:54:17 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class AboutDlg_base(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("AboutDlg_base")


        AboutDlg_baseLayout = QGridLayout(self,1,1,11,6,"AboutDlg_baseLayout")

        self.textLabel1 = QLabel(self,"textLabel1")

        AboutDlg_baseLayout.addMultiCellWidget(self.textLabel1,0,0,0,3)
        spacer15 = QSpacerItem(340,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        AboutDlg_baseLayout.addMultiCell(spacer15,7,7,0,2)

        self.pushButton15 = QPushButton(self,"pushButton15")

        AboutDlg_baseLayout.addWidget(self.pushButton15,7,3)

        self.pyPixmap = QLabel(self,"pyPixmap")
        self.pyPixmap.setMinimumSize(QSize(200,62))
        self.pyPixmap.setMaximumSize(QSize(200,62))
        self.pyPixmap.setScaledContents(1)

        AboutDlg_baseLayout.addWidget(self.pyPixmap,6,0)

        self.osiPixmap = QLabel(self,"osiPixmap")
        self.osiPixmap.setMinimumSize(QSize(75,65))
        self.osiPixmap.setMaximumSize(QSize(75,65))
        self.osiPixmap.setScaledContents(1)

        AboutDlg_baseLayout.addMultiCellWidget(self.osiPixmap,6,6,1,2)
        spacer5 = QSpacerItem(20,50,QSizePolicy.Minimum,QSizePolicy.Expanding)
        AboutDlg_baseLayout.addItem(spacer5,5,2)
        spacer4 = QSpacerItem(20,50,QSizePolicy.Minimum,QSizePolicy.Expanding)
        AboutDlg_baseLayout.addItem(spacer4,5,0)

        self.textLabel2 = QLabel(self,"textLabel2")

        AboutDlg_baseLayout.addMultiCellWidget(self.textLabel2,4,4,0,3)

        self.textLabel3 = QLabel(self,"textLabel3")

        AboutDlg_baseLayout.addMultiCellWidget(self.textLabel3,3,3,0,3)

        layout1 = QHBoxLayout(None,0,6,"layout1")

        self.textLabel4 = QLabel(self,"textLabel4")
        layout1.addWidget(self.textLabel4)

        self.VersionText = QLabel(self,"VersionText")
        layout1.addWidget(self.VersionText)

        AboutDlg_baseLayout.addMultiCellLayout(layout1,2,2,0,3)
        spacer6 = QSpacerItem(20,21,QSizePolicy.Minimum,QSizePolicy.Expanding)
        AboutDlg_baseLayout.addItem(spacer6,1,1)

        self.languageChange()

        self.resize(QSize(525,371).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.pushButton15,SIGNAL("clicked()"),self.close)


    def languageChange(self):
        self.setCaption(self.__tr("HP Device Manager - About"))
        self.textLabel1.setText(self.__tr("<font size=\"+3\"><p align=\"center\">HP Linux Imaging and Printing (HPLIP)</p></font>"))
        self.pushButton15.setText(self.__tr("OK"))
        self.textLabel2.setText(self.__tr("<b>Authors and Contributors:</b>\n"
"David Suffield, Don Welch, Shiyun Yie, Raghothama Cauligi, John Oleinik, Cory Meisch, Foster Nuffer, Pete Parks, Jacqueline Pitter, David Paschal, \n"
"Steve DeRoos, Mark Overton, Aaron Albright, Smith Kennedy, John Hosszu, Chris Wiesner, Henrique M. Holschuh, Till Kamppeter, John Hosszu"))
        self.textLabel3.setText(self.__tr("<b>License and Copyright:</b>\n"
"(c) Copyright 2006 Hewlett-Packard Development Company, L.P. This software is licensed under the GNU General Public License (GPL), BSD, and MIT licenses. See the software sources for details."))
        self.textLabel4.setText(self.__tr("<b>Software Version:</b>"))
        self.VersionText.setText(self.__tr("0.0.0"))


    def __tr(self,s,c = None):
        return qApp.translate("AboutDlg_base",s,c)
