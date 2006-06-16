# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'nodevicesform_base.ui'
#
# Created: Wed May 31 16:32:54 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class NoDevicesForm_base(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("NoDevicesForm_base")


        NoDevicesForm_baseLayout = QGridLayout(self,1,1,11,6,"NoDevicesForm_baseLayout")

        self.Icon = QLabel(self,"Icon")
        self.Icon.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.Icon.sizePolicy().hasHeightForWidth()))
        self.Icon.setFrameShape(QLabel.NoFrame)
        self.Icon.setScaledContents(1)

        NoDevicesForm_baseLayout.addWidget(self.Icon,0,0)

        self.textLabel7 = QLabel(self,"textLabel7")
        self.textLabel7.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter)

        NoDevicesForm_baseLayout.addMultiCellWidget(self.textLabel7,0,0,1,3)

        self.ExitButton = QPushButton(self,"ExitButton")

        NoDevicesForm_baseLayout.addWidget(self.ExitButton,1,3)

        self.CUPSButton = QPushButton(self,"CUPSButton")

        NoDevicesForm_baseLayout.addWidget(self.CUPSButton,1,2)
        spacer43 = QSpacerItem(520,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        NoDevicesForm_baseLayout.addMultiCell(spacer43,1,1,0,1)

        self.languageChange()

        self.resize(QSize(809,222).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.CUPSButton,SIGNAL("clicked()"),self.CUPSButton_clicked)
        self.connect(self.ExitButton,SIGNAL("clicked()"),self.ExitButton_clicked)


    def languageChange(self):
        self.setCaption(self.__tr("HP Device Manager - No Installed HP Devices Found"))
        self.textLabel7.setText(self.__tr("<b>No Installed HP Devices Found.</b><p>To install a device, use <b>hp-setup</b> (in a shell/terminal), the <b>CUPS web interface</b> (open a browser to: http://localhost:631 or press the button below), or the <b>printer installation utility</b> that came with your operating system.\n"
"After setting up a printer, you must press <tt>F6</tt> or chose <tt>Device | Refresh All</tt> for the printer to appear in the HP Device Manager.<p>\n"
"<i>Note: Only devices installed with the hp: CUPS backend will appear in the HP Device Manager.</i><p>"))
        self.ExitButton.setText(self.__tr("OK"))
        self.CUPSButton.setText(self.__tr("CUPS Web Interface"))


    def CUPSButton_clicked(self):
        print "NoDevicesForm_base.CUPSButton_clicked(): Not implemented yet"

    def ExitButton_clicked(self):
        print "NoDevicesForm_base.ExitButton_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("NoDevicesForm_base",s,c)
