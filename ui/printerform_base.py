# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'printerform_base.ui'
#
# Created: Wed Jan 11 14:42:39 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class PrinterForm_base(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("PrinterForm_base")


        PrinterForm_baseLayout = QGridLayout(self,1,1,11,6,"PrinterForm_baseLayout")
        spacer18 = QSpacerItem(430,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        PrinterForm_baseLayout.addItem(spacer18,3,0)

        self.pushButton5 = QPushButton(self,"pushButton5")

        PrinterForm_baseLayout.addWidget(self.pushButton5,3,1)

        self.printPushButton = QPushButton(self,"printPushButton")
        self.printPushButton.setEnabled(0)

        PrinterForm_baseLayout.addWidget(self.printPushButton,3,2)

        self.tabWidget3 = QTabWidget(self,"tabWidget3")

        self.tab = QWidget(self.tabWidget3,"tab")
        tabLayout = QGridLayout(self.tab,1,1,11,6,"tabLayout")

        self.groupBox5 = QGroupBox(self.tab,"groupBox5")
        self.groupBox5.setColumnLayout(0,Qt.Vertical)
        self.groupBox5.layout().setSpacing(6)
        self.groupBox5.layout().setMargin(11)
        groupBox5Layout = QGridLayout(self.groupBox5.layout())
        groupBox5Layout.setAlignment(Qt.AlignTop)

        layout4 = QHBoxLayout(None,0,6,"layout4")

        self.textLabel3 = QLabel(self.groupBox5,"textLabel3")
        layout4.addWidget(self.textLabel3)

        self.copiesSpinBox = QSpinBox(self.groupBox5,"copiesSpinBox")
        self.copiesSpinBox.setMaxValue(100)
        self.copiesSpinBox.setMinValue(1)
        layout4.addWidget(self.copiesSpinBox)

        groupBox5Layout.addLayout(layout4,0,0)

        self.collateCheckBox = QCheckBox(self.groupBox5,"collateCheckBox")

        groupBox5Layout.addWidget(self.collateCheckBox,1,0)

        self.reverseCheckBox = QCheckBox(self.groupBox5,"reverseCheckBox")

        groupBox5Layout.addMultiCellWidget(self.reverseCheckBox,2,2,0,1)

        tabLayout.addWidget(self.groupBox5,0,0)
        self.tabWidget3.insertTab(self.tab,QString.fromLatin1(""))

        self.tab_2 = QWidget(self.tabWidget3,"tab_2")
        tabLayout_2 = QGridLayout(self.tab_2,1,1,11,6,"tabLayout_2")

        self.pagesButtonGroup = QButtonGroup(self.tab_2,"pagesButtonGroup")
        self.pagesButtonGroup.setColumnLayout(0,Qt.Vertical)
        self.pagesButtonGroup.layout().setSpacing(6)
        self.pagesButtonGroup.layout().setMargin(11)
        pagesButtonGroupLayout = QGridLayout(self.pagesButtonGroup.layout())
        pagesButtonGroupLayout.setAlignment(Qt.AlignTop)

        self.radioButton3 = QRadioButton(self.pagesButtonGroup,"radioButton3")
        self.radioButton3.setChecked(1)

        pagesButtonGroupLayout.addMultiCellWidget(self.radioButton3,0,0,0,1)

        self.radioButton4 = QRadioButton(self.pagesButtonGroup,"radioButton4")

        pagesButtonGroupLayout.addMultiCellWidget(self.radioButton4,1,1,0,1)

        self.line2 = QFrame(self.pagesButtonGroup,"line2")
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Sunken)
        self.line2.setFrameShape(QFrame.HLine)

        pagesButtonGroupLayout.addMultiCellWidget(self.line2,2,2,0,5)
        spacer26 = QSpacerItem(230,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        pagesButtonGroupLayout.addMultiCell(spacer26,0,0,2,5)

        self.pageSetComboBox = QComboBox(0,self.pagesButtonGroup,"pageSetComboBox")

        pagesButtonGroupLayout.addMultiCellWidget(self.pageSetComboBox,4,4,4,5)

        self.textLabel11 = QLabel(self.pagesButtonGroup,"textLabel11")

        pagesButtonGroupLayout.addMultiCellWidget(self.textLabel11,3,4,0,0)

        self.pageRangeEdit = QLineEdit(self.pagesButtonGroup,"pageRangeEdit")
        self.pageRangeEdit.setEnabled(0)

        pagesButtonGroupLayout.addMultiCellWidget(self.pageRangeEdit,1,1,2,5)

        self.textLabel12 = QLabel(self.pagesButtonGroup,"textLabel12")

        pagesButtonGroupLayout.addMultiCellWidget(self.textLabel12,6,6,0,2)
        spacer30 = QSpacerItem(31,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        pagesButtonGroupLayout.addMultiCell(spacer30,6,6,3,4)

        self.nUpComboBox = QComboBox(0,self.pagesButtonGroup,"nUpComboBox")

        pagesButtonGroupLayout.addWidget(self.nUpComboBox,6,5)

        self.line2_2 = QFrame(self.pagesButtonGroup,"line2_2")
        self.line2_2.setFrameShape(QFrame.HLine)
        self.line2_2.setFrameShadow(QFrame.Sunken)
        self.line2_2.setFrameShape(QFrame.HLine)

        pagesButtonGroupLayout.addMultiCellWidget(self.line2_2,5,5,0,5)
        spacer29 = QSpacerItem(140,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        pagesButtonGroupLayout.addMultiCell(spacer29,4,4,1,3)

        tabLayout_2.addWidget(self.pagesButtonGroup,0,0)
        self.tabWidget3.insertTab(self.tab_2,QString.fromLatin1(""))

        self.TabPage = QWidget(self.tabWidget3,"TabPage")
        TabPageLayout = QGridLayout(self.TabPage,1,1,11,6,"TabPageLayout")

        self.orientationButtonGroup = QButtonGroup(self.TabPage,"orientationButtonGroup")
        self.orientationButtonGroup.setColumnLayout(0,Qt.Vertical)
        self.orientationButtonGroup.layout().setSpacing(6)
        self.orientationButtonGroup.layout().setMargin(11)
        orientationButtonGroupLayout = QGridLayout(self.orientationButtonGroup.layout())
        orientationButtonGroupLayout.setAlignment(Qt.AlignTop)

        self.radioButton5 = QRadioButton(self.orientationButtonGroup,"radioButton5")
        self.radioButton5.setChecked(1)

        orientationButtonGroupLayout.addWidget(self.radioButton5,0,0)

        self.radioButton6 = QRadioButton(self.orientationButtonGroup,"radioButton6")

        orientationButtonGroupLayout.addWidget(self.radioButton6,1,0)

        TabPageLayout.addWidget(self.orientationButtonGroup,0,0)

        self.buttonGroup4 = QButtonGroup(self.TabPage,"buttonGroup4")
        self.buttonGroup4.setColumnLayout(0,Qt.Vertical)
        self.buttonGroup4.layout().setSpacing(6)
        self.buttonGroup4.layout().setMargin(11)
        buttonGroup4Layout = QGridLayout(self.buttonGroup4.layout())
        buttonGroup4Layout.setAlignment(Qt.AlignTop)

        self.mirrorCheckBox = QCheckBox(self.buttonGroup4,"mirrorCheckBox")

        buttonGroup4Layout.addWidget(self.mirrorCheckBox,0,0)

        TabPageLayout.addWidget(self.buttonGroup4,0,1)
        self.tabWidget3.insertTab(self.TabPage,QString.fromLatin1(""))

        self.TabPage_2 = QWidget(self.tabWidget3,"TabPage_2")
        TabPageLayout_2 = QGridLayout(self.TabPage_2,1,1,11,6,"TabPageLayout_2")

        self.duplexButtonGroup = QButtonGroup(self.TabPage_2,"duplexButtonGroup")
        self.duplexButtonGroup.setExclusive(1)
        self.duplexButtonGroup.setColumnLayout(0,Qt.Vertical)
        self.duplexButtonGroup.layout().setSpacing(6)
        self.duplexButtonGroup.layout().setMargin(11)
        duplexButtonGroupLayout = QGridLayout(self.duplexButtonGroup.layout())
        duplexButtonGroupLayout.setAlignment(Qt.AlignTop)

        self.radioButton7 = QRadioButton(self.duplexButtonGroup,"radioButton7")
        self.radioButton7.setChecked(1)

        duplexButtonGroupLayout.addWidget(self.radioButton7,0,0)

        self.radioButton8 = QRadioButton(self.duplexButtonGroup,"radioButton8")

        duplexButtonGroupLayout.addWidget(self.radioButton8,1,0)

        self.radioButton9 = QRadioButton(self.duplexButtonGroup,"radioButton9")

        duplexButtonGroupLayout.addWidget(self.radioButton9,2,0)

        TabPageLayout_2.addWidget(self.duplexButtonGroup,0,0)

        self.groupBox7 = QGroupBox(self.TabPage_2,"groupBox7")
        self.groupBox7.setEnabled(0)
        self.groupBox7.setColumnLayout(0,Qt.Vertical)
        self.groupBox7.layout().setSpacing(6)
        self.groupBox7.layout().setMargin(11)
        groupBox7Layout = QGridLayout(self.groupBox7.layout())
        groupBox7Layout.setAlignment(Qt.AlignTop)

        self.manualDuplexCheckBox = QCheckBox(self.groupBox7,"manualDuplexCheckBox")
        self.manualDuplexCheckBox.setEnabled(0)

        groupBox7Layout.addWidget(self.manualDuplexCheckBox,0,0)

        TabPageLayout_2.addWidget(self.groupBox7,1,0)
        self.tabWidget3.insertTab(self.TabPage_2,QString.fromLatin1(""))

        PrinterForm_baseLayout.addMultiCellWidget(self.tabWidget3,2,2,0,2)

        self.groupBox3 = QGroupBox(self,"groupBox3")
        self.groupBox3.setColumnLayout(0,Qt.Vertical)
        self.groupBox3.layout().setSpacing(6)
        self.groupBox3.layout().setMargin(11)
        groupBox3Layout = QGridLayout(self.groupBox3.layout())
        groupBox3Layout.setAlignment(Qt.AlignTop)

        self.textLabel4 = QLabel(self.groupBox3,"textLabel4")

        groupBox3Layout.addMultiCellWidget(self.textLabel4,4,4,0,1)

        self.textLabel5 = QLabel(self.groupBox3,"textLabel5")

        groupBox3Layout.addMultiCellWidget(self.textLabel5,5,5,0,1)

        self.textLabel10 = QLabel(self.groupBox3,"textLabel10")

        groupBox3Layout.addMultiCellWidget(self.textLabel10,3,3,0,1)

        self.printerNameComboBox = QComboBox(0,self.groupBox3,"printerNameComboBox")
        self.printerNameComboBox.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,80,0,self.printerNameComboBox.sizePolicy().hasHeightForWidth()))

        groupBox3Layout.addWidget(self.printerNameComboBox,0,2)

        self.textLabel2 = QLabel(self.groupBox3,"textLabel2")

        groupBox3Layout.addMultiCellWidget(self.textLabel2,0,0,0,1)

        self.line4 = QFrame(self.groupBox3,"line4")
        self.line4.setFrameShape(QFrame.HLine)
        self.line4.setFrameShadow(QFrame.Sunken)
        self.line4.setFrameShape(QFrame.HLine)

        groupBox3Layout.addMultiCellWidget(self.line4,1,2,0,2)

        self.line3 = QFrame(self.groupBox3,"line3")
        self.line3.setFrameShape(QFrame.HLine)
        self.line3.setFrameShadow(QFrame.Sunken)
        self.line3.setFrameShape(QFrame.HLine)

        groupBox3Layout.addMultiCellWidget(self.line3,6,6,0,2)

        self.CommentText = QLabel(self.groupBox3,"CommentText")
        self.CommentText.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred,0,0,self.CommentText.sizePolicy().hasHeightForWidth()))

        groupBox3Layout.addWidget(self.CommentText,5,2)

        self.LocationText = QLabel(self.groupBox3,"LocationText")
        self.LocationText.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred,0,0,self.LocationText.sizePolicy().hasHeightForWidth()))

        groupBox3Layout.addWidget(self.LocationText,4,2)

        self.DeviceURIText = QLabel(self.groupBox3,"DeviceURIText")
        self.DeviceURIText.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred,0,0,self.DeviceURIText.sizePolicy().hasHeightForWidth()))

        groupBox3Layout.addMultiCellWidget(self.DeviceURIText,2,3,2,2)

        self.textLabel7 = QLabel(self.groupBox3,"textLabel7")

        groupBox3Layout.addWidget(self.textLabel7,7,0)

        layout6 = QHBoxLayout(None,0,6,"layout6")

        self.StateText = QLabel(self.groupBox3,"StateText")
        self.StateText.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred,0,0,self.StateText.sizePolicy().hasHeightForWidth()))
        layout6.addWidget(self.StateText)

        self.refreshToolButton = QToolButton(self.groupBox3,"refreshToolButton")
        self.refreshToolButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.refreshToolButton.sizePolicy().hasHeightForWidth()))
        self.refreshToolButton.setMinimumSize(QSize(32,32))
        self.refreshToolButton.setMaximumSize(QSize(32,32))
        layout6.addWidget(self.refreshToolButton)

        groupBox3Layout.addMultiCellLayout(layout6,7,7,1,2)

        PrinterForm_baseLayout.addMultiCellWidget(self.groupBox3,0,0,0,2)

        self.groupBox4 = QGroupBox(self,"groupBox4")
        self.groupBox4.setColumnLayout(0,Qt.Vertical)
        self.groupBox4.layout().setSpacing(6)
        self.groupBox4.layout().setMargin(11)
        groupBox4Layout = QGridLayout(self.groupBox4.layout())
        groupBox4Layout.setAlignment(Qt.AlignTop)

        self.fileListView = QListView(self.groupBox4,"fileListView")
        self.fileListView.addColumn(self.__tr("Name"))
        self.fileListView.addColumn(self.__tr("Type"))
        self.fileListView.addColumn(self.__tr("Path"))
        self.fileListView.setAllColumnsShowFocus(1)

        groupBox4Layout.addMultiCellWidget(self.fileListView,0,2,0,0)

        self.addFileButton = QToolButton(self.groupBox4,"addFileButton")
        self.addFileButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.addFileButton.sizePolicy().hasHeightForWidth()))
        self.addFileButton.setMinimumSize(QSize(32,32))
        self.addFileButton.setMaximumSize(QSize(32,32))

        groupBox4Layout.addWidget(self.addFileButton,0,1)

        self.delFileButton = QToolButton(self.groupBox4,"delFileButton")
        self.delFileButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.delFileButton.sizePolicy().hasHeightForWidth()))
        self.delFileButton.setMinimumSize(QSize(32,32))
        self.delFileButton.setMaximumSize(QSize(32,32))

        groupBox4Layout.addWidget(self.delFileButton,1,1)
        spacer23 = QSpacerItem(20,61,QSizePolicy.Minimum,QSizePolicy.Expanding)
        groupBox4Layout.addItem(spacer23,2,1)

        PrinterForm_baseLayout.addMultiCellWidget(self.groupBox4,1,1,0,2)

        self.languageChange()

        self.resize(QSize(622,654).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.pushButton5,SIGNAL("clicked()"),self.reject)
        self.connect(self.addFileButton,SIGNAL("clicked()"),self.addFileButton_clicked)
        self.connect(self.delFileButton,SIGNAL("clicked()"),self.delFileButton_clicked)
        self.connect(self.fileListView,SIGNAL("currentChanged(QListViewItem*)"),self.fileListView_currentChanged)
        self.connect(self.printerNameComboBox,SIGNAL("highlighted(const QString&)"),self.printerNameComboBox_highlighted)
        self.connect(self.pagesButtonGroup,SIGNAL("clicked(int)"),self.pagesButtonGroup_clicked)
        self.connect(self.printPushButton,SIGNAL("clicked()"),self.printPushButton_clicked)
        self.connect(self.duplexButtonGroup,SIGNAL("clicked(int)"),self.duplexButtonGroup_clicked)
        self.connect(self.orientationButtonGroup,SIGNAL("clicked(int)"),self.orientationButtonGroup_clicked)
        self.connect(self.refreshToolButton,SIGNAL("clicked()"),self.refreshToolButton_clicked)


    def languageChange(self):
        self.setCaption(self.__tr("HP Device Manager - Print"))
        self.pushButton5.setText(self.__tr("Close"))
        QToolTip.add(self.pushButton5,QString.null)
        self.printPushButton.setText(self.__tr("Print"))
        QToolTip.add(self.printPushButton,QString.null)
        self.groupBox5.setTitle(self.__tr("Copies"))
        self.textLabel3.setText(self.__tr("Copies:"))
        QToolTip.add(self.copiesSpinBox,self.__tr("Number of copies"))
        self.collateCheckBox.setText(self.__tr("Collate copies"))
        self.reverseCheckBox.setText(self.__tr("Reverse print order"))
        self.tabWidget3.changeTab(self.tab,self.__tr("Copies"))
        self.pagesButtonGroup.setTitle(self.__tr("Pages"))
        self.radioButton3.setText(self.__tr("All pages"))
        self.radioButton4.setText(self.__tr("Page range:"))
        self.pageSetComboBox.clear()
        self.pageSetComboBox.insertItem(self.__tr("All pages"))
        self.pageSetComboBox.insertItem(self.__tr("Even pages"))
        self.pageSetComboBox.insertItem(self.__tr("Odd pages"))
        self.textLabel11.setText(self.__tr("Page set:"))
        QToolTip.add(self.pageRangeEdit,self.__tr("Enter pages or ranges of pages separated by commas (e.g., 1-2,4,6-7)"))
        self.textLabel12.setText(self.__tr("Pages per sheet (N-up):"))
        self.nUpComboBox.clear()
        self.nUpComboBox.insertItem(self.__tr("1"))
        self.nUpComboBox.insertItem(self.__tr("2"))
        self.nUpComboBox.insertItem(self.__tr("4"))
        self.nUpComboBox.insertItem(self.__tr("8"))
        self.nUpComboBox.insertItem(self.__tr("16"))
        self.tabWidget3.changeTab(self.tab_2,self.__tr("Pages"))
        self.orientationButtonGroup.setTitle(self.__tr("Orientation"))
        self.radioButton5.setText(self.__tr("Portrait"))
        self.radioButton6.setText(self.__tr("Landscape"))
        self.buttonGroup4.setTitle(self.__tr("Mirror"))
        self.mirrorCheckBox.setText(self.__tr("Enable mirror printing"))
        self.tabWidget3.changeTab(self.TabPage,self.__tr("Orientation"))
        self.duplexButtonGroup.setTitle(self.__tr("Automatic Duplex"))
        self.radioButton7.setText(self.__tr("Off"))
        self.radioButton8.setText(self.__tr("Long edge (standard)"))
        self.radioButton9.setText(self.__tr("Short edge (flip)"))
        self.groupBox7.setTitle(self.__tr("Manual Duplex"))
        self.manualDuplexCheckBox.setText(self.__tr("Manual duplex"))
        self.tabWidget3.changeTab(self.TabPage_2,self.__tr("Duplex"))
        self.groupBox3.setTitle(self.__tr("Printer"))
        self.textLabel4.setText(self.__tr("Location:"))
        self.textLabel5.setText(self.__tr("Comment:"))
        self.textLabel10.setText(self.__tr("Device URI:"))
        QToolTip.add(self.printerNameComboBox,self.__tr("CUPS printer name"))
        self.textLabel2.setText(self.__tr("Name:"))
        self.CommentText.setText(QString.null)
        self.LocationText.setText(QString.null)
        self.DeviceURIText.setText(QString.null)
        self.textLabel7.setText(self.__tr("Status:"))
        self.StateText.setText(QString.null)
        self.refreshToolButton.setText(QString.null)
        QToolTip.add(self.refreshToolButton,self.__tr("Refresh status"))
        self.groupBox4.setTitle(self.__tr("File(s)"))
        self.fileListView.header().setLabel(0,self.__tr("Name"))
        self.fileListView.header().setLabel(1,self.__tr("Type"))
        self.fileListView.header().setLabel(2,self.__tr("Path"))
        QToolTip.add(self.fileListView,self.__tr("List of files to print"))
        self.addFileButton.setText(QString.null)
        self.addFileButton.setTextLabel(self.__tr("Add file to list"))
        self.delFileButton.setText(QString.null)
        self.delFileButton.setTextLabel(self.__tr("Remove file from list"))


    def addFileButton_clicked(self):
        print "PrinterForm_base.addFileButton_clicked(): Not implemented yet"

    def delFileButton_clicked(self):
        print "PrinterForm_base.delFileButton_clicked(): Not implemented yet"

    def fileListView_currentChanged(self,a0):
        print "PrinterForm_base.fileListView_currentChanged(QListViewItem*): Not implemented yet"

    def printerNameComboBox_highlighted(self,a0):
        print "PrinterForm_base.printerNameComboBox_highlighted(const QString&): Not implemented yet"

    def pagesButtonGroup_clicked(self,a0):
        print "PrinterForm_base.pagesButtonGroup_clicked(int): Not implemented yet"

    def printPushButton_clicked(self):
        print "PrinterForm_base.printPushButton_clicked(): Not implemented yet"

    def duplexButtonGroup_clicked(self,a0):
        print "PrinterForm_base.duplexButtonGroup_clicked(int): Not implemented yet"

    def orientationButtonGroup_clicked(self,a0):
        print "PrinterForm_base.orientationButtonGroup_clicked(int): Not implemented yet"

    def refreshToolButton_clicked(self):
        print "PrinterForm_base.refreshToolButton_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("PrinterForm_base",s,c)
