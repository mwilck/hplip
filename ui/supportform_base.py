# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/dwelch/linux-imaging-and-printing/src/ui/supportform_base.ui'
#
# Created: Tue Sep 13 11:53:43 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class SupportForm_base(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("SupportForm_base")


        SupportForm_baseLayout = QGridLayout(self,1,1,11,6,"SupportForm_baseLayout")

        self.pushButton4 = QPushButton(self,"pushButton4")

        SupportForm_baseLayout.addWidget(self.pushButton4,1,1)
        spacer19 = QSpacerItem(810,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        SupportForm_baseLayout.addItem(spacer19,1,0)

        self.tabWidget2 = QTabWidget(self,"tabWidget2")

        self.tab = QWidget(self.tabWidget2,"tab")
        tabLayout = QGridLayout(self.tab,1,1,11,6,"tabLayout")

        self.textLabel6 = QLabel(self.tab,"textLabel6")
        self.textLabel6.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter)

        tabLayout.addWidget(self.textLabel6,4,0)

        self.hpinktjetButton = QPushButton(self.tab,"hpinktjetButton")
        self.hpinktjetButton.setPaletteForegroundColor(QColor(0,0,255))
        hpinktjetButton_font = QFont(self.hpinktjetButton.font())
        hpinktjetButton_font.setFamily("Courier 10 Pitch")
        hpinktjetButton_font.setUnderline(1)
        self.hpinktjetButton.setFont(hpinktjetButton_font)
        self.hpinktjetButton.setCursor(QCursor(13))

        tabLayout.addWidget(self.hpinktjetButton,3,0)

        self.textLabel2 = QLabel(self.tab,"textLabel2")
        self.textLabel2.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter)

        tabLayout.addWidget(self.textLabel2,2,0)

        self.textLabel2_2 = QLabel(self.tab,"textLabel2_2")

        tabLayout.addWidget(self.textLabel2_2,0,0)

        self.line2_3 = QFrame(self.tab,"line2_3")
        self.line2_3.setFrameShape(QFrame.HLine)
        self.line2_3.setFrameShadow(QFrame.Sunken)
        self.line2_3.setFrameShape(QFrame.HLine)

        tabLayout.addWidget(self.line2_3,1,0)
        spacer3 = QSpacerItem(20,51,QSizePolicy.Minimum,QSizePolicy.Expanding)
        tabLayout.addItem(spacer3,5,0)
        self.tabWidget2.insertTab(self.tab,QString.fromLatin1(""))

        self.tab_2 = QWidget(self.tabWidget2,"tab_2")
        tabLayout_2 = QGridLayout(self.tab_2,1,1,11,6,"tabLayout_2")

        self.line2_3_2 = QFrame(self.tab_2,"line2_3_2")
        self.line2_3_2.setFrameShape(QFrame.HLine)
        self.line2_3_2.setFrameShadow(QFrame.Sunken)
        self.line2_3_2.setFrameShape(QFrame.HLine)

        tabLayout_2.addWidget(self.line2_3_2,1,0)

        self.textLabel2_2_2 = QLabel(self.tab_2,"textLabel2_2_2")

        tabLayout_2.addWidget(self.textLabel2_2_2,0,0)

        self.textLabel2_3 = QLabel(self.tab_2,"textLabel2_3")
        self.textLabel2_3.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter)

        tabLayout_2.addWidget(self.textLabel2_3,2,0)

        self.hpinktjetButton_2 = QPushButton(self.tab_2,"hpinktjetButton_2")
        self.hpinktjetButton_2.setPaletteForegroundColor(QColor(0,0,255))
        hpinktjetButton_2_font = QFont(self.hpinktjetButton_2.font())
        hpinktjetButton_2_font.setFamily("Courier 10 Pitch")
        hpinktjetButton_2_font.setUnderline(1)
        self.hpinktjetButton_2.setFont(hpinktjetButton_2_font)
        self.hpinktjetButton_2.setCursor(QCursor(13))

        tabLayout_2.addWidget(self.hpinktjetButton_2,3,0)
        spacer5 = QSpacerItem(20,91,QSizePolicy.Minimum,QSizePolicy.Expanding)
        tabLayout_2.addItem(spacer5,4,0)
        self.tabWidget2.insertTab(self.tab_2,QString.fromLatin1(""))

        self.TabPage = QWidget(self.tabWidget2,"TabPage")
        TabPageLayout = QGridLayout(self.TabPage,1,1,11,6,"TabPageLayout")

        self.line2 = QFrame(self.TabPage,"line2")
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Sunken)
        self.line2.setFrameShape(QFrame.HLine)

        TabPageLayout.addWidget(self.line2,1,0)

        self.linuxprintingButton = QPushButton(self.TabPage,"linuxprintingButton")
        self.linuxprintingButton.setPaletteForegroundColor(QColor(0,0,255))
        linuxprintingButton_font = QFont(self.linuxprintingButton.font())
        linuxprintingButton_font.setFamily("Courier 10 Pitch")
        linuxprintingButton_font.setUnderline(1)
        self.linuxprintingButton.setFont(linuxprintingButton_font)
        self.linuxprintingButton.setCursor(QCursor(13))

        TabPageLayout.addWidget(self.linuxprintingButton,3,0)

        self.textLabel4 = QLabel(self.TabPage,"textLabel4")
        self.textLabel4.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter)

        TabPageLayout.addWidget(self.textLabel4,2,0)

        self.textLabel1 = QLabel(self.TabPage,"textLabel1")

        TabPageLayout.addWidget(self.textLabel1,0,0)

        self.textLabel6_2 = QLabel(self.TabPage,"textLabel6_2")
        self.textLabel6_2.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter)

        TabPageLayout.addWidget(self.textLabel6_2,5,0)
        spacer6 = QSpacerItem(20,51,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout.addItem(spacer6,4,0)
        self.tabWidget2.insertTab(self.TabPage,QString.fromLatin1(""))

        self.TabPage_2 = QWidget(self.tabWidget2,"TabPage_2")

        self.line2_2 = QFrame(self.TabPage_2,"line2_2")
        self.line2_2.setGeometry(QRect(11,40,773,16))
        self.line2_2.setFrameShape(QFrame.HLine)
        self.line2_2.setFrameShadow(QFrame.Sunken)
        self.line2_2.setFrameShape(QFrame.HLine)

        self.linuxprintingButton_2 = QPushButton(self.TabPage_2,"linuxprintingButton_2")
        self.linuxprintingButton_2.setGeometry(QRect(11,94,773,28))
        self.linuxprintingButton_2.setPaletteForegroundColor(QColor(0,0,255))
        linuxprintingButton_2_font = QFont(self.linuxprintingButton_2.font())
        linuxprintingButton_2_font.setFamily("Courier 10 Pitch")
        linuxprintingButton_2_font.setUnderline(1)
        self.linuxprintingButton_2.setFont(linuxprintingButton_2_font)
        self.linuxprintingButton_2.setCursor(QCursor(13))

        self.textLabel1_2 = QLabel(self.TabPage_2,"textLabel1_2")
        self.textLabel1_2.setGeometry(QRect(11,11,384,23))

        self.textLabel4_2 = QLabel(self.TabPage_2,"textLabel4_2")
        self.textLabel4_2.setGeometry(QRect(11,49,773,39))
        self.textLabel4_2.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter)

        self.textLabel6_2_2 = QLabel(self.TabPage_2,"textLabel6_2_2")
        self.textLabel6_2_2.setGeometry(QRect(10,260,773,39))
        self.textLabel6_2_2.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter)
        self.tabWidget2.insertTab(self.TabPage_2,QString.fromLatin1(""))

        SupportForm_baseLayout.addMultiCellWidget(self.tabWidget2,0,0,0,1)

        self.languageChange()

        self.resize(QSize(821,409).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.pushButton4,SIGNAL("clicked()"),self.accept)
        self.connect(self.hpinktjetButton,SIGNAL("clicked()"),self.hpinktjetButton_clicked)
        self.connect(self.linuxprintingButton,SIGNAL("clicked()"),self.linuxprintingButton_clicked)
        self.connect(self.linuxprintingButton_2,SIGNAL("clicked()"),self.linuxprintingButton_2_clicked)
        self.connect(self.hpinktjetButton_2,SIGNAL("clicked()"),self.hpinktjetButton_2_clicked)


    def languageChange(self):
        self.setCaption(self.__tr("HP Device Manager - Support Information"))
        self.pushButton4.setText(self.__tr("Close"))
        self.textLabel6.setText(self.__tr("On this HP sponsored website, you will find FAQs, open discussion forums, installation instructions, a product support table, and other support materials."))
        self.hpinktjetButton.setText(self.__tr("http://hpinkjet.sourceforge.net"))
        self.textLabel2.setText(self.__tr("HPLIP is free, open source software distributed under the MIT, BSD, and GPL licenses.  <b><i>HP does not provide formal consumer or commercial support for this software. </i></b><p>Support is provided informally through a series of resources on the website:"))
        self.textLabel2_2.setText(self.__tr("<b>HP Sponsored Support</b>"))
        self.tabWidget2.changeTab(self.tab,self.__tr("HP"))
        self.textLabel2_2_2.setText(self.__tr("<b>README File</b>"))
        self.textLabel2_3.setText(self.__tr("A readme file was shipped with your version of HPLIP. This file contains the product support table, a troubleshooting guide, and other support resources."))
        self.hpinktjetButton_2.setText(self.__tr("hplip_readme.html"))
        self.tabWidget2.changeTab(self.tab_2,self.__tr("README File"))
        self.linuxprintingButton.setText(self.__tr("http://linuxprinting.org"))
        self.textLabel4.setText(self.__tr("General Linux printing assistance is also available from open discussion forums, documentation, access to PPD files, etc. from:"))
        self.textLabel1.setText(self.__tr("<b>linuxprinting.org</b>"))
        self.textLabel6_2.setText(self.__tr("NOTE: Linuxprinting.org is operated through the generous efforts of Grant Taylor and Till Kamppeter and is not affiliated with HP."))
        self.tabWidget2.changeTab(self.TabPage,self.__tr("linuxprinting.org"))
        self.linuxprintingButton_2.setText(self.__tr("http://cups.org"))
        self.textLabel1_2.setText(self.__tr("<b>CUPS</b>"))
        self.textLabel4_2.setText(self.__tr("Information about CUPS (Common UNIX Printing System) is available at cups.org. This website also contains forums and other support resources for printing on Linux:"))
        self.textLabel6_2_2.setText(self.__tr("NOTE: CUPS and the CUPS website is owned and operated by Easy Software Products and is not affiliated with HP."))
        self.tabWidget2.changeTab(self.TabPage_2,self.__tr("CUPS"))


    def hpinktjetButton_clicked(self):
        print "SupportForm_base.hpinktjetButton_clicked(): Not implemented yet"

    def linuxprintingButton_clicked(self):
        print "SupportForm_base.linuxprintingButton_clicked(): Not implemented yet"

    def linuxprintingButton_2_clicked(self):
        print "SupportForm_base.linuxprintingButton_2_clicked(): Not implemented yet"

    def hpinktjetButton_2_clicked(self):
        print "SupportForm_base.hpinktjetButton_2_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("SupportForm_base",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = SupportForm_base()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
