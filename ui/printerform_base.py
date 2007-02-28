# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/printerform_base.ui'
#
# Created: Fri Feb 9 11:26:18 2007
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
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
        PrinterForm_baseLayout.addItem(spacer18,1,0)

        self.pushButton5 = QPushButton(self,"pushButton5")

        PrinterForm_baseLayout.addWidget(self.pushButton5,1,1)

        self.printPushButton = QPushButton(self,"printPushButton")
        self.printPushButton.setEnabled(0)

        PrinterForm_baseLayout.addWidget(self.printPushButton,1,2)

        self.tabWidget4 = QTabWidget(self,"tabWidget4")

        self.tab = QWidget(self.tabWidget4,"tab")
        tabLayout = QGridLayout(self.tab,1,1,11,6,"tabLayout")

        self.groupBox4 = QGroupBox(self.tab,"groupBox4")
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

        tabLayout.addWidget(self.groupBox4,0,0)
        self.tabWidget4.insertTab(self.tab,QString.fromLatin1(""))

        self.tab_2 = QWidget(self.tabWidget4,"tab_2")
        tabLayout_2 = QGridLayout(self.tab_2,1,1,11,6,"tabLayout_2")

        self.groupBox5 = QGroupBox(self.tab_2,"groupBox5")

        self.textLabel3 = QLabel(self.groupBox5,"textLabel3")
        self.textLabel3.setGeometry(QRect(11,21,48,22))

        self.copiesSpinBox = QSpinBox(self.groupBox5,"copiesSpinBox")
        self.copiesSpinBox.setGeometry(QRect(65,21,50,22))
        self.copiesSpinBox.setMaxValue(100)
        self.copiesSpinBox.setMinValue(1)

        tabLayout_2.addWidget(self.groupBox5,0,0)

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

        pagesButtonGroupLayout.addWidget(self.radioButton4,1,0)

        self.pageRangeEdit = QLineEdit(self.pagesButtonGroup,"pageRangeEdit")
        self.pageRangeEdit.setEnabled(0)

        pagesButtonGroupLayout.addWidget(self.pageRangeEdit,1,1)

        tabLayout_2.addWidget(self.pagesButtonGroup,1,0)

        self.groupBox7_2 = QGroupBox(self.tab_2,"groupBox7_2")
        self.groupBox7_2.setColumnLayout(0,Qt.Vertical)
        self.groupBox7_2.layout().setSpacing(6)
        self.groupBox7_2.layout().setMargin(11)
        groupBox7_2Layout = QGridLayout(self.groupBox7_2.layout())
        groupBox7_2Layout.setAlignment(Qt.AlignTop)
        spacer14 = QSpacerItem(291,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox7_2Layout.addItem(spacer14,0,2)

        self.textLabel11 = QLabel(self.groupBox7_2,"textLabel11")

        groupBox7_2Layout.addWidget(self.textLabel11,0,0)

        self.pageSetComboBox = QComboBox(0,self.groupBox7_2,"pageSetComboBox")

        groupBox7_2Layout.addWidget(self.pageSetComboBox,0,1)

        tabLayout_2.addWidget(self.groupBox7_2,2,0)
        spacer45 = QSpacerItem(20,111,QSizePolicy.Minimum,QSizePolicy.Expanding)
        tabLayout_2.addItem(spacer45,3,0)
        self.tabWidget4.insertTab(self.tab_2,QString.fromLatin1(""))

        self.TabPage = QWidget(self.tabWidget4,"TabPage")
        TabPageLayout = QGridLayout(self.TabPage,1,1,11,6,"TabPageLayout")

        self.groupBox3 = QGroupBox(self.TabPage,"groupBox3")
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

        TabPageLayout.addWidget(self.groupBox3,0,0)
        spacer20 = QSpacerItem(41,211,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout.addItem(spacer20,1,0)
        self.tabWidget4.insertTab(self.TabPage,QString.fromLatin1(""))

        PrinterForm_baseLayout.addMultiCellWidget(self.tabWidget4,0,0,0,2)

        self.languageChange()

        self.resize(QSize(544,536).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.pushButton5,SIGNAL("clicked()"),self.reject)
        self.connect(self.addFileButton,SIGNAL("clicked()"),self.addFileButton_clicked)
        self.connect(self.delFileButton,SIGNAL("clicked()"),self.delFileButton_clicked)
        self.connect(self.fileListView,SIGNAL("currentChanged(QListViewItem*)"),self.fileListView_currentChanged)
        self.connect(self.printerNameComboBox,SIGNAL("highlighted(const QString&)"),self.printerNameComboBox_highlighted)
        self.connect(self.pagesButtonGroup,SIGNAL("clicked(int)"),self.pagesButtonGroup_clicked)
        self.connect(self.printPushButton,SIGNAL("clicked()"),self.printPushButton_clicked)
        self.connect(self.refreshToolButton,SIGNAL("clicked()"),self.refreshToolButton_clicked)
        self.connect(self.pageRangeEdit,SIGNAL("lostFocus()"),self.pageRangeEdit_lostFocus)
        self.connect(self.pageRangeEdit,SIGNAL("textChanged(const QString&)"),self.pageRangeEdit_textChanged)


    def languageChange(self):
        self.setCaption(self.__tr("HP Device Manager - Print"))
        self.pushButton5.setText(self.__tr("Close"))
        QToolTip.add(self.pushButton5,QString.null)
        self.printPushButton.setText(self.__tr("Print"))
        QToolTip.add(self.printPushButton,QString.null)
        self.groupBox4.setTitle(self.__tr("File(s)"))
        self.fileListView.header().setLabel(0,self.__tr("Name"))
        self.fileListView.header().setLabel(1,self.__tr("Type"))
        self.fileListView.header().setLabel(2,self.__tr("Path"))
        QToolTip.add(self.fileListView,self.__tr("List of files to print"))
        self.addFileButton.setText(QString.null)
        self.addFileButton.setTextLabel(self.__tr("Add file to list"))
        self.delFileButton.setText(QString.null)
        self.delFileButton.setTextLabel(self.__tr("Remove file from list"))
        self.tabWidget4.changeTab(self.tab,self.__tr("Files"))
        self.groupBox5.setTitle(self.__tr("Number of Copies"))
        self.textLabel3.setText(self.__tr("Copies:"))
        QToolTip.add(self.copiesSpinBox,self.__tr("Number of copies"))
        self.pagesButtonGroup.setTitle(self.__tr("Pages"))
        self.radioButton3.setText(self.__tr("All pages"))
        self.radioButton4.setText(self.__tr("Page range:"))
        QToolTip.add(self.pageRangeEdit,self.__tr("Enter pages or ranges of pages separated by commas (e.g., 1-2,4,6-7)"))
        self.groupBox7_2.setTitle(self.__tr("Page Set"))
        self.textLabel11.setText(self.__tr("Page set:"))
        self.pageSetComboBox.clear()
        self.pageSetComboBox.insertItem(self.__tr("All pages"))
        self.pageSetComboBox.insertItem(self.__tr("Even pages"))
        self.pageSetComboBox.insertItem(self.__tr("Odd pages"))
        self.tabWidget4.changeTab(self.tab_2,self.__tr("Options"))
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
        self.tabWidget4.changeTab(self.TabPage,self.__tr("Printer"))


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

    def checkBoxPrettyPrinting_toggled(self,a0):
        print "PrinterForm_base.checkBoxPrettyPrinting_toggled(bool): Not implemented yet"

    def pageRangeEdit_lostFocus(self):
        print "PrinterForm_base.pageRangeEdit_lostFocus(): Not implemented yet"

    def pageRangeEdit_textChanged(self,a0):
        print "PrinterForm_base.pageRangeEdit_textChanged(const QString&): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("PrinterForm_base",s,c)
