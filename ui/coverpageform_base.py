# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'coverpageform_base.ui'
#
# Created: Thu Dec 15 10:32:31 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class CoverpageForm_base(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("CoverpageForm_base")


        CoverpageForm_baseLayout = QGridLayout(self,1,1,11,6,"CoverpageForm_baseLayout")

        self.line1_2 = QFrame(self,"line1_2")
        self.line1_2.setFrameShape(QFrame.HLine)
        self.line1_2.setFrameShadow(QFrame.Sunken)
        self.line1_2.setFrameShape(QFrame.HLine)

        CoverpageForm_baseLayout.addMultiCellWidget(self.line1_2,1,1,0,2)
        spacer7 = QSpacerItem(161,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        CoverpageForm_baseLayout.addItem(spacer7,7,0)

        self.pushButton10 = QPushButton(self,"pushButton10")

        CoverpageForm_baseLayout.addWidget(self.pushButton10,7,1)

        self.pushButton9 = QPushButton(self,"pushButton9")

        CoverpageForm_baseLayout.addWidget(self.pushButton9,7,2)

        self.textLabel5 = QLabel(self,"textLabel5")

        CoverpageForm_baseLayout.addMultiCellWidget(self.textLabel5,0,0,0,2)

        self.groupBox2 = QGroupBox(self,"groupBox2")
        self.groupBox2.setColumnLayout(0,Qt.Vertical)
        self.groupBox2.layout().setSpacing(6)
        self.groupBox2.layout().setMargin(11)
        groupBox2Layout = QGridLayout(self.groupBox2.layout())
        groupBox2Layout.setAlignment(Qt.AlignTop)

        layout4 = QVBoxLayout(None,0,6,"layout4")

        self.coverpagePixmap = QLabel(self.groupBox2,"coverpagePixmap")
        self.coverpagePixmap.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.coverpagePixmap.sizePolicy().hasHeightForWidth()))
        self.coverpagePixmap.setMinimumSize(QSize(164,228))
        self.coverpagePixmap.setMaximumSize(QSize(164,228))
        self.coverpagePixmap.setFrameShape(QLabel.Box)
        self.coverpagePixmap.setFrameShadow(QLabel.Plain)
        self.coverpagePixmap.setScaledContents(1)
        layout4.addWidget(self.coverpagePixmap)

        groupBox2Layout.addLayout(layout4,0,2)
        spacer10 = QSpacerItem(121,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox2Layout.addItem(spacer10,0,0)
        spacer9 = QSpacerItem(110,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox2Layout.addItem(spacer9,0,4)

        self.prevCoverpageButton = QToolButton(self.groupBox2,"prevCoverpageButton")
        self.prevCoverpageButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.prevCoverpageButton.sizePolicy().hasHeightForWidth()))
        self.prevCoverpageButton.setMinimumSize(QSize(32,32))
        self.prevCoverpageButton.setMaximumSize(QSize(32,32))

        groupBox2Layout.addWidget(self.prevCoverpageButton,0,1)

        self.nextCoverpageButton = QToolButton(self.groupBox2,"nextCoverpageButton")
        self.nextCoverpageButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.nextCoverpageButton.sizePolicy().hasHeightForWidth()))
        self.nextCoverpageButton.setMinimumSize(QSize(32,32))
        self.nextCoverpageButton.setMaximumSize(QSize(32,32))

        groupBox2Layout.addWidget(self.nextCoverpageButton,0,3)

        CoverpageForm_baseLayout.addMultiCellWidget(self.groupBox2,2,2,0,2)

        layout7 = QVBoxLayout(None,0,6,"layout7")

        self.textLabel3 = QLabel(self,"textLabel3")
        layout7.addWidget(self.textLabel3)

        self.messageTextEdit = QTextEdit(self,"messageTextEdit")
        layout7.addWidget(self.messageTextEdit)

        CoverpageForm_baseLayout.addMultiCellLayout(layout7,6,6,0,2)

        self.line9 = QFrame(self,"line9")
        self.line9.setFrameShape(QFrame.HLine)
        self.line9.setFrameShadow(QFrame.Sunken)
        self.line9.setFrameShape(QFrame.HLine)

        CoverpageForm_baseLayout.addMultiCellWidget(self.line9,5,5,0,2)

        layout9 = QHBoxLayout(None,0,6,"layout9")

        self.textLabel6 = QLabel(self,"textLabel6")
        layout9.addWidget(self.textLabel6)

        self.regardingTextEdit = QLineEdit(self,"regardingTextEdit")
        layout9.addWidget(self.regardingTextEdit)

        CoverpageForm_baseLayout.addMultiCellLayout(layout9,4,4,0,2)

        self.languageChange()

        self.resize(QSize(478,574).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.pushButton10,SIGNAL("clicked()"),self.reject)
        self.connect(self.pushButton9,SIGNAL("clicked()"),self.accept)
        self.connect(self.prevCoverpageButton,SIGNAL("clicked()"),self.prevCoverpageButton_clicked)
        self.connect(self.nextCoverpageButton,SIGNAL("clicked()"),self.nextCoverpageButton_clicked)

        self.setTabOrder(self.regardingTextEdit,self.messageTextEdit)
        self.setTabOrder(self.messageTextEdit,self.pushButton10)
        self.setTabOrder(self.pushButton10,self.pushButton9)


    def languageChange(self):
        self.setCaption(self.__tr("HP Device Manager - Coverpages"))
        self.pushButton10.setText(self.__tr("Cancel"))
        self.pushButton9.setText(self.__tr("OK"))
        self.textLabel5.setText(self.__tr("<b>Choose coverpage and enter optional message.<b>"))
        self.groupBox2.setTitle(self.__tr("Choose Coverpage"))
        self.prevCoverpageButton.setText(QString.null)
        self.prevCoverpageButton.setAccel(QString.null)
        self.nextCoverpageButton.setText(QString.null)
        self.textLabel3.setText(self.__tr("Optional Message <i>(Maximum 2000 characters)</i>:"))
        self.textLabel6.setText(self.__tr("Regarding:"))


    def coverpageListBox_currentChanged(self,a0):
        print "CoverpageForm_base.coverpageListBox_currentChanged(QListBoxItem*): Not implemented yet"

    def prevCoverpageButton_clicked(self):
        print "CoverpageForm_base.prevCoverpageButton_clicked(): Not implemented yet"

    def nextCoverpageButton_clicked(self):
        print "CoverpageForm_base.nextCoverpageButton_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("CoverpageForm_base",s,c)
