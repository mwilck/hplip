# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/makecopiesform_base.ui'
#
# Created: Thu Jun 15 10:57:54 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class MakeCopiesForm_base(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("MakeCopiesForm_base")


        MakeCopiesForm_baseLayout = QGridLayout(self,1,1,11,6,"MakeCopiesForm_baseLayout")

        self.pushButton2 = QPushButton(self,"pushButton2")

        MakeCopiesForm_baseLayout.addWidget(self.pushButton2,1,1)
        spacer1 = QSpacerItem(431,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        MakeCopiesForm_baseLayout.addItem(spacer1,1,0)

        self.tabWidget2 = QTabWidget(self,"tabWidget2")

        self.tab = QWidget(self.tabWidget2,"tab")
        tabLayout = QGridLayout(self.tab,1,1,11,6,"tabLayout")

        self.textLabel3_2_2_2_2 = QLabel(self.tab,"textLabel3_2_2_2_2")

        tabLayout.addMultiCellWidget(self.textLabel3_2_2_2_2,0,0,0,1)

        self.makeCopiesPushButton = QPushButton(self.tab,"makeCopiesPushButton")

        tabLayout.addMultiCellWidget(self.makeCopiesPushButton,6,6,0,1)
        spacer7 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        tabLayout.addItem(spacer7,5,0)
        spacer8 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        tabLayout.addItem(spacer8,5,1)

        self.qualityButtonGroup = QButtonGroup(self.tab,"qualityButtonGroup")

        self.radioButton1 = QRadioButton(self.qualityButtonGroup,"radioButton1")
        self.radioButton1.setGeometry(QRect(11,21,200,20))

        self.radioButton2 = QRadioButton(self.qualityButtonGroup,"radioButton2")
        self.radioButton2.setGeometry(QRect(11,47,200,20))

        self.radioButton3 = QRadioButton(self.qualityButtonGroup,"radioButton3")
        self.radioButton3.setGeometry(QRect(11,73,200,20))

        self.radioButton4 = QRadioButton(self.qualityButtonGroup,"radioButton4")
        self.radioButton4.setGeometry(QRect(11,99,200,20))

        self.radioButton5 = QRadioButton(self.qualityButtonGroup,"radioButton5")
        self.radioButton5.setGeometry(QRect(11,125,200,20))

        tabLayout.addWidget(self.qualityButtonGroup,4,0)

        self.groupBox5 = QGroupBox(self.tab,"groupBox5")
        self.groupBox5.setColumnLayout(0,Qt.Vertical)
        self.groupBox5.layout().setSpacing(6)
        self.groupBox5.layout().setMargin(11)
        groupBox5Layout = QGridLayout(self.groupBox5.layout())
        groupBox5Layout.setAlignment(Qt.AlignTop)

        layout7 = QHBoxLayout(None,0,6,"layout7")

        self.textLabel1 = QLabel(self.groupBox5,"textLabel1")
        layout7.addWidget(self.textLabel1)

        self.numberCopiesSpinBox = QSpinBox(self.groupBox5,"numberCopiesSpinBox")
        self.numberCopiesSpinBox.setMinValue(1)
        layout7.addWidget(self.numberCopiesSpinBox)

        groupBox5Layout.addLayout(layout7,0,0)

        tabLayout.addWidget(self.groupBox5,4,1)

        self.line1_2_2_2_2 = QFrame(self.tab,"line1_2_2_2_2")
        self.line1_2_2_2_2.setFrameShape(QFrame.HLine)
        self.line1_2_2_2_2.setFrameShadow(QFrame.Sunken)
        self.line1_2_2_2_2.setFrameShape(QFrame.HLine)

        tabLayout.addMultiCellWidget(self.line1_2_2_2_2,1,1,0,1)

        self.groupBox2 = QGroupBox(self.tab,"groupBox2")
        self.groupBox2.setColumnLayout(0,Qt.Vertical)
        self.groupBox2.layout().setSpacing(6)
        self.groupBox2.layout().setMargin(11)
        groupBox2Layout = QGridLayout(self.groupBox2.layout())
        groupBox2Layout.setAlignment(Qt.AlignTop)

        self.contrastTextLabel = QLabel(self.groupBox2,"contrastTextLabel")
        self.contrastTextLabel.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred,0,0,self.contrastTextLabel.sizePolicy().hasHeightForWidth()))

        groupBox2Layout.addWidget(self.contrastTextLabel,0,1)
        spacer9 = QSpacerItem(181,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox2Layout.addItem(spacer9,0,2)
        spacer10 = QSpacerItem(181,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox2Layout.addItem(spacer10,0,0)

        self.contrastSlider = QSlider(self.groupBox2,"contrastSlider")
        self.contrastSlider.setMinValue(-5)
        self.contrastSlider.setMaxValue(5)
        self.contrastSlider.setOrientation(QSlider.Horizontal)

        groupBox2Layout.addMultiCellWidget(self.contrastSlider,1,1,0,2)

        tabLayout.addMultiCellWidget(self.groupBox2,2,2,0,1)

        self.groupBox3 = QGroupBox(self.tab,"groupBox3")
        self.groupBox3.setColumnLayout(0,Qt.Vertical)
        self.groupBox3.layout().setSpacing(6)
        self.groupBox3.layout().setMargin(11)
        groupBox3Layout = QGridLayout(self.groupBox3.layout())
        groupBox3Layout.setAlignment(Qt.AlignTop)

        self.reductionTextLabel = QLabel(self.groupBox3,"reductionTextLabel")
        self.reductionTextLabel.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred,0,0,self.reductionTextLabel.sizePolicy().hasHeightForWidth()))

        groupBox3Layout.addMultiCellWidget(self.reductionTextLabel,0,1,2,2)

        self.reductionSlider = QSlider(self.groupBox3,"reductionSlider")
        self.reductionSlider.setOrientation(QSlider.Horizontal)

        groupBox3Layout.addMultiCellWidget(self.reductionSlider,2,2,0,3)

        self.fitToPageCheckBox = QCheckBox(self.groupBox3,"fitToPageCheckBox")

        groupBox3Layout.addMultiCellWidget(self.fitToPageCheckBox,0,1,0,1)
        spacer11 = QSpacerItem(91,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox3Layout.addItem(spacer11,1,1)
        spacer12 = QSpacerItem(151,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox3Layout.addItem(spacer12,1,3)

        tabLayout.addMultiCellWidget(self.groupBox3,3,3,0,1)
        self.tabWidget2.insertTab(self.tab,QString.fromLatin1(""))

        self.tab_2 = QWidget(self.tabWidget2,"tab_2")
        tabLayout_2 = QGridLayout(self.tab_2,1,1,11,6,"tabLayout_2")
        spacer13 = QSpacerItem(20,150,QSizePolicy.Minimum,QSizePolicy.Expanding)
        tabLayout_2.addItem(spacer13,8,0)

        self.line1_2_2_2 = QFrame(self.tab_2,"line1_2_2_2")
        self.line1_2_2_2.setFrameShape(QFrame.HLine)
        self.line1_2_2_2.setFrameShadow(QFrame.Sunken)
        self.line1_2_2_2.setFrameShape(QFrame.HLine)

        tabLayout_2.addWidget(self.line1_2_2_2,1,0)

        self.line10 = QFrame(self.tab_2,"line10")
        self.line10.setFrameShape(QFrame.HLine)
        self.line10.setFrameShadow(QFrame.Sunken)
        self.line10.setFrameShape(QFrame.HLine)

        tabLayout_2.addWidget(self.line10,3,0)

        layout18 = QHBoxLayout(None,0,6,"layout18")

        self.textLabel4 = QLabel(self.tab_2,"textLabel4")
        layout18.addWidget(self.textLabel4)

        self.printerNameComboBox = QComboBox(0,self.tab_2,"printerNameComboBox")
        self.printerNameComboBox.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,QSizePolicy.Fixed,0,0,self.printerNameComboBox.sizePolicy().hasHeightForWidth()))
        layout18.addWidget(self.printerNameComboBox)

        tabLayout_2.addLayout(layout18,2,0)

        self.textLabel3_2_2_2 = QLabel(self.tab_2,"textLabel3_2_2_2")

        tabLayout_2.addWidget(self.textLabel3_2_2_2,0,0)

        layout17 = QHBoxLayout(None,0,6,"layout17")

        self.textLabel2_2 = QLabel(self.tab_2,"textLabel2_2")
        layout17.addWidget(self.textLabel2_2)

        self.StateText = QLabel(self.tab_2,"StateText")
        self.StateText.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred,0,0,self.StateText.sizePolicy().hasHeightForWidth()))
        self.StateText.setFrameShape(QLabel.NoFrame)
        layout17.addWidget(self.StateText)

        self.refreshToolButton = QToolButton(self.tab_2,"refreshToolButton")
        self.refreshToolButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.refreshToolButton.sizePolicy().hasHeightForWidth()))
        self.refreshToolButton.setMinimumSize(QSize(32,32))
        self.refreshToolButton.setMaximumSize(QSize(32,32))
        layout17.addWidget(self.refreshToolButton)

        tabLayout_2.addLayout(layout17,7,0)

        layout8 = QHBoxLayout(None,0,6,"layout8")

        self.textLabel10 = QLabel(self.tab_2,"textLabel10")
        layout8.addWidget(self.textLabel10)

        self.CommentText = QLabel(self.tab_2,"CommentText")
        self.CommentText.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred,0,0,self.CommentText.sizePolicy().hasHeightForWidth()))
        layout8.addWidget(self.CommentText)

        tabLayout_2.addLayout(layout8,6,0)

        layout20 = QHBoxLayout(None,0,6,"layout20")

        self.textLabel9 = QLabel(self.tab_2,"textLabel9")
        layout20.addWidget(self.textLabel9)

        self.LocationText = QLabel(self.tab_2,"LocationText")
        self.LocationText.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred,0,0,self.LocationText.sizePolicy().hasHeightForWidth()))
        layout20.addWidget(self.LocationText)

        tabLayout_2.addLayout(layout20,5,0)

        layout15 = QHBoxLayout(None,0,6,"layout15")

        self.textLabel2 = QLabel(self.tab_2,"textLabel2")
        layout15.addWidget(self.textLabel2)

        self.DeviceURIText = QLabel(self.tab_2,"DeviceURIText")
        self.DeviceURIText.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred,0,0,self.DeviceURIText.sizePolicy().hasHeightForWidth()))
        self.DeviceURIText.setFrameShape(QLabel.NoFrame)
        layout15.addWidget(self.DeviceURIText)

        tabLayout_2.addLayout(layout15,4,0)
        self.tabWidget2.insertTab(self.tab_2,QString.fromLatin1(""))

        MakeCopiesForm_baseLayout.addMultiCellWidget(self.tabWidget2,0,0,0,1)

        self.languageChange()

        self.resize(QSize(497,546).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.pushButton2,SIGNAL("clicked()"),self.reject)
        self.connect(self.makeCopiesPushButton,SIGNAL("clicked()"),self.makeCopiesPushButton_clicked)
        self.connect(self.qualityButtonGroup,SIGNAL("clicked(int)"),self.qualityButtonGroup_clicked)
        self.connect(self.reductionSlider,SIGNAL("valueChanged(int)"),self.reductionSlider_valueChanged)
        self.connect(self.contrastSlider,SIGNAL("valueChanged(int)"),self.contrastSlider_valueChanged)
        self.connect(self.fitToPageCheckBox,SIGNAL("clicked()"),self.fitToPageCheckBox_clicked)


    def languageChange(self):
        self.setCaption(self.__tr("HP Device Manager - Make Copies"))
        self.pushButton2.setText(self.__tr("Close"))
        self.textLabel3_2_2_2_2.setText(self.__tr("<b>Make copies.</b>"))
        self.makeCopiesPushButton.setText(self.__tr("Make Copies"))
        self.qualityButtonGroup.setTitle(self.__tr("Quality:"))
        self.radioButton1.setText(self.__tr("Fast"))
        self.radioButton2.setText(self.__tr("Draft"))
        self.radioButton3.setText(self.__tr("Normal"))
        self.radioButton4.setText(self.__tr("Presentation"))
        self.radioButton5.setText(self.__tr("Best"))
        self.groupBox5.setTitle(self.__tr("Number of Copies:"))
        self.textLabel1.setText(self.__tr("Number of Copies:"))
        self.groupBox2.setTitle(self.__tr("Contrast:"))
        self.contrastTextLabel.setText(self.__tr("+0"))
        self.groupBox3.setTitle(self.__tr("Enlargement/Reduction:"))
        self.reductionTextLabel.setText(self.__tr("400%"))
        self.fitToPageCheckBox.setText(self.__tr("Fit to page"))
        self.tabWidget2.changeTab(self.tab,self.__tr("Copy"))
        self.textLabel4.setText(self.__tr("Name:"))
        self.textLabel3_2_2_2.setText(self.__tr("<b>Device information/status and  output queue name.</b>"))
        self.textLabel2_2.setText(self.__tr("Status:"))
        self.StateText.setText(QString.null)
        self.refreshToolButton.setText(QString.null)
        QToolTip.add(self.refreshToolButton,self.__tr("Refresh status"))
        self.textLabel10.setText(self.__tr("Comment:"))
        self.CommentText.setText(QString.null)
        self.textLabel9.setText(self.__tr("Location:"))
        self.LocationText.setText(QString.null)
        self.textLabel2.setText(self.__tr("Device URI:"))
        self.DeviceURIText.setText(QString.null)
        self.tabWidget2.changeTab(self.tab_2,self.__tr("Device"))


    def makeCopiesPushButton_clicked(self):
        print "MakeCopiesForm_base.makeCopiesPushButton_clicked(): Not implemented yet"

    def qualityButtonGroup_clicked(self,a0):
        print "MakeCopiesForm_base.qualityButtonGroup_clicked(int): Not implemented yet"

    def reductionSlider_valueChanged(self,a0):
        print "MakeCopiesForm_base.reductionSlider_valueChanged(int): Not implemented yet"

    def contrastSlider_valueChanged(self,a0):
        print "MakeCopiesForm_base.contrastSlider_valueChanged(int): Not implemented yet"

    def fitToPageCheckBox_clicked(self):
        print "MakeCopiesForm_base.fitToPageCheckBox_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("MakeCopiesForm_base",s,c)
