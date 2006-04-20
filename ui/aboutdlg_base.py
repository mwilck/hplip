# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'aboutdlg_base.ui'
#
# Created: Wed Mar 1 16:04:21 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class AboutDlg_base(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("AboutDlg_base")


        AboutDlg_baseLayout = QGridLayout(self,1,1,11,6,"AboutDlg_baseLayout")

        self.pushButton15 = QPushButton(self,"pushButton15")

        AboutDlg_baseLayout.addWidget(self.pushButton15,6,2)
        spacer15 = QSpacerItem(481,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        AboutDlg_baseLayout.addMultiCell(spacer15,6,6,0,1)
        spacer14 = QSpacerItem(20,21,QSizePolicy.Minimum,QSizePolicy.Expanding)
        AboutDlg_baseLayout.addItem(spacer14,5,1)

        self.textLabel3 = QLabel(self,"textLabel3")

        AboutDlg_baseLayout.addMultiCellWidget(self.textLabel3,3,3,0,2)

        self.textLabel4 = QLabel(self,"textLabel4")

        AboutDlg_baseLayout.addWidget(self.textLabel4,2,0)

        self.textLabel2 = QLabel(self,"textLabel2")

        AboutDlg_baseLayout.addMultiCellWidget(self.textLabel2,4,4,0,2)

        self.VersionText = QLabel(self,"VersionText")

        AboutDlg_baseLayout.addWidget(self.VersionText,2,1)
        spacer16 = QSpacerItem(20,21,QSizePolicy.Minimum,QSizePolicy.Expanding)
        AboutDlg_baseLayout.addItem(spacer16,1,0)

        self.textLabel1 = QLabel(self,"textLabel1")

        AboutDlg_baseLayout.addMultiCellWidget(self.textLabel1,0,0,0,2)

        self.languageChange()

        self.resize(QSize(465,487).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.pushButton15,SIGNAL("clicked()"),self.close)


    def languageChange(self):
        self.setCaption(self.__tr("HP Device Manager - About"))
        self.pushButton15.setText(self.__tr("OK"))
        self.textLabel3.setText(self.__tr("<b>License and Copyright:</b>\n"
"(c) Copyright 2006 Hewlett-Packard Development Company, L.P. This software is licensed under the GNU General Public License (GPL), BSD, and MIT licenses. See the software sources for details."))
        self.textLabel4.setText(self.__tr("<b>Software Version:</b>"))
        self.textLabel2.setText(self.__tr("<b>Authors and Contributors:</b>\n"
"David Suffield, Don Welch, Shiyun Yie, Raghothama Cauligi, John Oleinik, Cory Meisch, Foster Nuffer, Pete Parks, Jacqueline Pitter, David Paschal, Steve DeRoos, Kathy Hartshorn, Mark Overton, Aaron Albright, Smith Kennedy"))
        self.VersionText.setText(self.__tr("0.0.0"))
        self.textLabel1.setText(self.__tr("<font size=\"+3\"><p align=\"center\">HP Linux Imaging and Printing System (HPLIP)</p></font>"))


    def __tr(self,s,c = None):
        return qApp.translate("AboutDlg_base",s,c)
