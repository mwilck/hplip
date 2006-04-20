# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'faxsendjobform_base.ui'
#
# Created: Mon Feb 27 16:38:21 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class FaxSendJobForm_base(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("FaxSendJobForm_base")


        FaxSendJobForm_baseLayout = QGridLayout(self,1,1,11,6,"FaxSendJobForm_baseLayout")

        self.addressBookButton = QPushButton(self,"addressBookButton")

        FaxSendJobForm_baseLayout.addWidget(self.addressBookButton,1,0)

        self.pushButton29 = QPushButton(self,"pushButton29")

        FaxSendJobForm_baseLayout.addWidget(self.pushButton29,1,3)

        self.sendNowButton = QPushButton(self,"sendNowButton")
        self.sendNowButton.setEnabled(0)

        FaxSendJobForm_baseLayout.addWidget(self.sendNowButton,1,4)

        self.tabWidget2 = QTabWidget(self,"tabWidget2")

        self.tab = QWidget(self.tabWidget2,"tab")
        tabLayout = QGridLayout(self.tab,1,1,11,6,"tabLayout")

        self.textLabel3_2 = QLabel(self.tab,"textLabel3_2")
        self.textLabel3_2.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.textLabel3_2.sizePolicy().hasHeightForWidth()))

        tabLayout.addMultiCellWidget(self.textLabel3_2,0,0,0,1)

        self.fileListView = QListView(self.tab,"fileListView")
        self.fileListView.addColumn(self.__tr("Name/Title"))
        self.fileListView.header().setClickEnabled(0,self.fileListView.header().count() - 1)
        self.fileListView.addColumn(self.__tr("File Type"))
        self.fileListView.header().setClickEnabled(0,self.fileListView.header().count() - 1)
        self.fileListView.addColumn(self.__tr("Pages (Total=0)"))
        self.fileListView.header().setClickEnabled(0,self.fileListView.header().count() - 1)

        tabLayout.addMultiCellWidget(self.fileListView,3,6,0,0)

        self.buttonGroup3 = QButtonGroup(self.tab,"buttonGroup3")
        self.buttonGroup3.setColumnLayout(0,Qt.Vertical)
        self.buttonGroup3.layout().setSpacing(6)
        self.buttonGroup3.layout().setMargin(11)
        buttonGroup3Layout = QGridLayout(self.buttonGroup3.layout())
        buttonGroup3Layout.setAlignment(Qt.AlignTop)

        layout9 = QHBoxLayout(None,0,6,"layout9")

        self.textLabel1_2 = QLabel(self.buttonGroup3,"textLabel1_2")
        layout9.addWidget(self.textLabel1_2)

        self.fileEdit = QLineEdit(self.buttonGroup3,"fileEdit")
        layout9.addWidget(self.fileEdit)

        self.browsePushButton = QPushButton(self.buttonGroup3,"browsePushButton")
        layout9.addWidget(self.browsePushButton)

        buttonGroup3Layout.addMultiCellLayout(layout9,0,0,0,1)

        self.addFilePushButton = QPushButton(self.buttonGroup3,"addFilePushButton")
        self.addFilePushButton.setEnabled(0)

        buttonGroup3Layout.addWidget(self.addFilePushButton,2,1)
        spacer8 = QSpacerItem(361,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        buttonGroup3Layout.addItem(spacer8,2,0)

        tabLayout.addWidget(self.buttonGroup3,7,0)

        self.groupBox1 = QGroupBox(self.tab,"groupBox1")
        self.groupBox1.setColumnLayout(0,Qt.Vertical)
        self.groupBox1.layout().setSpacing(6)
        self.groupBox1.layout().setMargin(11)
        groupBox1Layout = QGridLayout(self.groupBox1.layout())
        groupBox1Layout.setAlignment(Qt.AlignTop)

        self.addCoverpagePushButton = QPushButton(self.groupBox1,"addCoverpagePushButton")

        groupBox1Layout.addWidget(self.addCoverpagePushButton,0,2)

        self.editCoverpagePushButton = QPushButton(self.groupBox1,"editCoverpagePushButton")
        self.editCoverpagePushButton.setEnabled(0)

        groupBox1Layout.addWidget(self.editCoverpagePushButton,0,1)
        spacer6 = QSpacerItem(190,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox1Layout.addItem(spacer6,0,0)

        tabLayout.addWidget(self.groupBox1,8,0)

        self.line1_2 = QFrame(self.tab,"line1_2")
        self.line1_2.setFrameShape(QFrame.HLine)
        self.line1_2.setFrameShadow(QFrame.Sunken)
        self.line1_2.setFrameShape(QFrame.HLine)

        tabLayout.addMultiCellWidget(self.line1_2,1,2,0,1)

        self.delFileButton = QToolButton(self.tab,"delFileButton")
        self.delFileButton.setEnabled(0)
        self.delFileButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.delFileButton.sizePolicy().hasHeightForWidth()))
        self.delFileButton.setMinimumSize(QSize(32,32))
        self.delFileButton.setMaximumSize(QSize(32,32))

        tabLayout.addMultiCellWidget(self.delFileButton,2,3,1,1)

        self.upFileButton = QToolButton(self.tab,"upFileButton")
        self.upFileButton.setEnabled(0)
        self.upFileButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.upFileButton.sizePolicy().hasHeightForWidth()))
        self.upFileButton.setMinimumSize(QSize(32,32))
        self.upFileButton.setMaximumSize(QSize(32,32))

        tabLayout.addWidget(self.upFileButton,4,1)

        self.downFileButton = QToolButton(self.tab,"downFileButton")
        self.downFileButton.setEnabled(0)
        self.downFileButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.downFileButton.sizePolicy().hasHeightForWidth()))
        self.downFileButton.setMinimumSize(QSize(32,32))
        self.downFileButton.setMaximumSize(QSize(32,32))

        tabLayout.addWidget(self.downFileButton,5,1)
        spacer7 = QSpacerItem(20,300,QSizePolicy.Minimum,QSizePolicy.Expanding)
        tabLayout.addMultiCell(spacer7,6,9,1,1)

        self.groupBox5 = QGroupBox(self.tab,"groupBox5")
        self.groupBox5.setColumnLayout(0,Qt.Vertical)
        self.groupBox5.layout().setSpacing(6)
        self.groupBox5.layout().setMargin(11)
        groupBox5Layout = QGridLayout(self.groupBox5.layout())
        groupBox5Layout.setAlignment(Qt.AlignTop)

        self.appPrintNoteLabel = QLabel(self.groupBox5,"appPrintNoteLabel")

        groupBox5Layout.addWidget(self.appPrintNoteLabel,0,0)

        tabLayout.addWidget(self.groupBox5,9,0)
        spacer7_2 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        tabLayout.addItem(spacer7_2,10,0)
        self.tabWidget2.insertTab(self.tab,QString.fromLatin1(""))

        self.tab_2 = QWidget(self.tabWidget2,"tab_2")
        tabLayout_2 = QGridLayout(self.tab_2,1,1,11,6,"tabLayout_2")

        self.textLabel3 = QLabel(self.tab_2,"textLabel3")

        tabLayout_2.addMultiCellWidget(self.textLabel3,0,0,0,1)

        self.line1 = QFrame(self.tab_2,"line1")
        self.line1.setFrameShape(QFrame.HLine)
        self.line1.setFrameShadow(QFrame.Sunken)
        self.line1.setFrameShape(QFrame.HLine)

        tabLayout_2.addMultiCellWidget(self.line1,1,1,0,1)

        self.textLabel1 = QLabel(self.tab_2,"textLabel1")

        tabLayout_2.addMultiCellWidget(self.textLabel1,2,2,0,1)

        self.individualSendListView = QListView(self.tab_2,"individualSendListView")
        self.individualSendListView.addColumn(self.__tr("Select"))
        self.individualSendListView.addColumn(self.__tr("Name"))
        self.individualSendListView.addColumn(self.__tr("Fax Number"))
        self.individualSendListView.addColumn(self.__tr("Notes/Other Information"))
        self.individualSendListView.setSelectionMode(QListView.NoSelection)

        tabLayout_2.addMultiCellWidget(self.individualSendListView,3,3,0,1)

        self.textLabel2 = QLabel(self.tab_2,"textLabel2")

        tabLayout_2.addMultiCellWidget(self.textLabel2,4,4,0,1)

        self.groupSendListView = QListView(self.tab_2,"groupSendListView")
        self.groupSendListView.addColumn(self.__tr("Select"))
        self.groupSendListView.addColumn(self.__tr("Group"))
        self.groupSendListView.addColumn(self.__tr("Group Members"))
        self.groupSendListView.setEnabled(1)
        self.groupSendListView.setSelectionMode(QListView.NoSelection)

        tabLayout_2.addMultiCellWidget(self.groupSendListView,5,5,0,1)

        self.textLabel5 = QLabel(self.tab_2,"textLabel5")

        tabLayout_2.addWidget(self.textLabel5,6,0)

        self.selectionEdit = QLineEdit(self.tab_2,"selectionEdit")
        self.selectionEdit.setReadOnly(1)

        tabLayout_2.addWidget(self.selectionEdit,6,1)
        self.tabWidget2.insertTab(self.tab_2,QString.fromLatin1(""))

        self.TabPage = QWidget(self.tabWidget2,"TabPage")
        TabPageLayout = QGridLayout(self.TabPage,1,1,11,6,"TabPageLayout")
        spacer11 = QSpacerItem(20,200,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout.addItem(spacer11,9,0)

        layout7 = QHBoxLayout(None,0,6,"layout7")

        self.textLabel7_2 = QLabel(self.TabPage,"textLabel7_2")
        layout7.addWidget(self.textLabel7_2)

        layout6 = QHBoxLayout(None,0,6,"layout6")

        self.StateText = QLabel(self.TabPage,"StateText")
        self.StateText.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred,0,0,self.StateText.sizePolicy().hasHeightForWidth()))
        layout6.addWidget(self.StateText)

        self.refreshToolButton = QToolButton(self.TabPage,"refreshToolButton")
        self.refreshToolButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.refreshToolButton.sizePolicy().hasHeightForWidth()))
        self.refreshToolButton.setMinimumSize(QSize(32,32))
        self.refreshToolButton.setMaximumSize(QSize(32,32))
        layout6.addWidget(self.refreshToolButton)
        layout7.addLayout(layout6)

        TabPageLayout.addLayout(layout7,8,0)

        layout9_2 = QHBoxLayout(None,0,6,"layout9_2")

        self.textLabel9 = QLabel(self.TabPage,"textLabel9")
        layout9_2.addWidget(self.textLabel9)

        self.LocationText = QLabel(self.TabPage,"LocationText")
        self.LocationText.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred,0,0,self.LocationText.sizePolicy().hasHeightForWidth()))
        layout9_2.addWidget(self.LocationText)

        TabPageLayout.addLayout(layout9_2,5,0)

        self.line12 = QFrame(self.TabPage,"line12")
        self.line12.setFrameShape(QFrame.HLine)
        self.line12.setFrameShadow(QFrame.Sunken)
        self.line12.setFrameShape(QFrame.HLine)

        TabPageLayout.addWidget(self.line12,7,0)

        layout5 = QHBoxLayout(None,0,6,"layout5")

        self.textLabel6 = QLabel(self.TabPage,"textLabel6")
        layout5.addWidget(self.textLabel6)

        self.printerNameComboBox = QComboBox(0,self.TabPage,"printerNameComboBox")
        self.printerNameComboBox.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,QSizePolicy.Fixed,0,0,self.printerNameComboBox.sizePolicy().hasHeightForWidth()))
        layout5.addWidget(self.printerNameComboBox)

        TabPageLayout.addLayout(layout5,2,0)

        self.line11 = QFrame(self.TabPage,"line11")
        self.line11.setFrameShape(QFrame.HLine)
        self.line11.setFrameShadow(QFrame.Sunken)
        self.line11.setFrameShape(QFrame.HLine)

        TabPageLayout.addWidget(self.line11,3,0)

        layout10 = QHBoxLayout(None,0,6,"layout10")

        self.textLabel7 = QLabel(self.TabPage,"textLabel7")
        layout10.addWidget(self.textLabel7)

        self.DeviceURIText = QLabel(self.TabPage,"DeviceURIText")
        self.DeviceURIText.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred,0,0,self.DeviceURIText.sizePolicy().hasHeightForWidth()))
        layout10.addWidget(self.DeviceURIText)

        TabPageLayout.addLayout(layout10,4,0)

        layout8 = QHBoxLayout(None,0,6,"layout8")

        self.textLabel10 = QLabel(self.TabPage,"textLabel10")
        layout8.addWidget(self.textLabel10)

        self.CommentText = QLabel(self.TabPage,"CommentText")
        self.CommentText.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred,0,0,self.CommentText.sizePolicy().hasHeightForWidth()))
        layout8.addWidget(self.CommentText)

        TabPageLayout.addLayout(layout8,6,0)

        self.line1_2_2_2 = QFrame(self.TabPage,"line1_2_2_2")
        self.line1_2_2_2.setFrameShape(QFrame.HLine)
        self.line1_2_2_2.setFrameShadow(QFrame.Sunken)
        self.line1_2_2_2.setFrameShape(QFrame.HLine)

        TabPageLayout.addWidget(self.line1_2_2_2,1,0)

        self.textLabel3_2_2_2 = QLabel(self.TabPage,"textLabel3_2_2_2")

        TabPageLayout.addWidget(self.textLabel3_2_2_2,0,0)
        self.tabWidget2.insertTab(self.TabPage,QString.fromLatin1(""))

        FaxSendJobForm_baseLayout.addMultiCellWidget(self.tabWidget2,0,0,0,4)
        spacer30 = QSpacerItem(70,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        FaxSendJobForm_baseLayout.addItem(spacer30,1,2)

        self.settingsPushButton = QPushButton(self,"settingsPushButton")

        FaxSendJobForm_baseLayout.addWidget(self.settingsPushButton,1,1)

        self.languageChange()

        self.resize(QSize(546,541).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.pushButton29,SIGNAL("clicked()"),self.reject)
        self.connect(self.individualSendListView,SIGNAL("clicked(QListViewItem*)"),self.individualSendListView_clicked)
        self.connect(self.groupSendListView,SIGNAL("clicked(QListViewItem*)"),self.groupSendListView_clicked)
        self.connect(self.addressBookButton,SIGNAL("clicked()"),self.addressBookButton_clicked)
        self.connect(self.sendNowButton,SIGNAL("clicked()"),self.sendNowButton_clicked)
        self.connect(self.delFileButton,SIGNAL("clicked()"),self.delFileButton_clicked)
        self.connect(self.addFilePushButton,SIGNAL("clicked()"),self.addFilePushButton_clicked)
        self.connect(self.browsePushButton,SIGNAL("clicked()"),self.browsePushButton_clicked)
        self.connect(self.upFileButton,SIGNAL("clicked()"),self.upFileButton_clicked)
        self.connect(self.downFileButton,SIGNAL("clicked()"),self.downFileButton_clicked)
        self.connect(self.fileEdit,SIGNAL("textChanged(const QString&)"),self.fileEdit_textChanged)
        self.connect(self.addCoverpagePushButton,SIGNAL("clicked()"),self.addCoverpagePushButton_clicked)
        self.connect(self.refreshToolButton,SIGNAL("clicked()"),self.refreshToolButton_clicked)
        self.connect(self.printerNameComboBox,SIGNAL("highlighted(const QString&)"),self.printerNameComboBox_highlighted)
        self.connect(self.editCoverpagePushButton,SIGNAL("clicked()"),self.editCoverpagePushButton_clicked)
        self.connect(self.settingsPushButton,SIGNAL("clicked()"),self.settingsPushButton_clicked)

        self.setTabOrder(self.fileListView,self.fileEdit)
        self.setTabOrder(self.fileEdit,self.browsePushButton)
        self.setTabOrder(self.browsePushButton,self.addFilePushButton)
        self.setTabOrder(self.addFilePushButton,self.editCoverpagePushButton)
        self.setTabOrder(self.editCoverpagePushButton,self.addCoverpagePushButton)
        self.setTabOrder(self.addCoverpagePushButton,self.addressBookButton)
        self.setTabOrder(self.addressBookButton,self.settingsPushButton)
        self.setTabOrder(self.settingsPushButton,self.pushButton29)
        self.setTabOrder(self.pushButton29,self.sendNowButton)
        self.setTabOrder(self.sendNowButton,self.tabWidget2)
        self.setTabOrder(self.tabWidget2,self.individualSendListView)
        self.setTabOrder(self.individualSendListView,self.groupSendListView)
        self.setTabOrder(self.groupSendListView,self.selectionEdit)
        self.setTabOrder(self.selectionEdit,self.printerNameComboBox)


    def languageChange(self):
        self.setCaption(self.__tr("HP Device Manager - Send Fax"))
        self.addressBookButton.setText(self.__tr("Address Book..."))
        self.pushButton29.setText(self.__tr("Close"))
        self.sendNowButton.setText(self.__tr("Send Fax"))
        self.textLabel3_2.setText(self.__tr("<b>Add items to the list to send as a fax.</b>"))
        self.fileListView.header().setLabel(0,self.__tr("Name/Title"))
        self.fileListView.header().setLabel(1,self.__tr("File Type"))
        self.fileListView.header().setLabel(2,self.__tr("Pages (Total=0)"))
        self.buttonGroup3.setTitle(self.__tr("File"))
        self.textLabel1_2.setText(self.__tr("File:"))
        self.browsePushButton.setText(self.__tr("Browse..."))
        self.addFilePushButton.setText(self.__tr("Add to List"))
        self.groupBox1.setTitle(self.__tr("Coverpage"))
        self.addCoverpagePushButton.setText(self.__tr("Add to List..."))
        self.editCoverpagePushButton.setText(self.__tr("Edit..."))
        self.delFileButton.setText(QString.null)
        self.delFileButton.setTextLabel(self.__tr("Remove file from list"))
        self.upFileButton.setText(QString.null)
        self.upFileButton.setTextLabel(self.__tr("Move file up in list"))
        self.downFileButton.setText(QString.null)
        self.downFileButton.setTextLabel(self.__tr("Move file down in list"))
        self.groupBox5.setTitle(self.__tr("Application Document"))
        self.appPrintNoteLabel.setText(self.__tr("<i>You can also add items by printing documents from an application using the CUPS printer '%1'.</i>"))
        self.tabWidget2.changeTab(self.tab,self.__tr("Items"))
        self.textLabel3.setText(self.__tr("<b>Select the individuals and/or groups as fax recipients.</b>"))
        self.textLabel1.setText(self.__tr("Individual(s):"))
        self.individualSendListView.header().setLabel(0,self.__tr("Select"))
        self.individualSendListView.header().setLabel(1,self.__tr("Name"))
        self.individualSendListView.header().setLabel(2,self.__tr("Fax Number"))
        self.individualSendListView.header().setLabel(3,self.__tr("Notes/Other Information"))
        self.textLabel2.setText(self.__tr("Group(s):"))
        self.groupSendListView.header().setLabel(0,self.__tr("Select"))
        self.groupSendListView.header().setLabel(1,self.__tr("Group"))
        self.groupSendListView.header().setLabel(2,self.__tr("Group Members"))
        self.textLabel5.setText(self.__tr("Selection:"))
        self.tabWidget2.changeTab(self.tab_2,self.__tr("Recipients"))
        self.textLabel7_2.setText(self.__tr("Status:"))
        self.StateText.setText(QString.null)
        self.refreshToolButton.setText(QString.null)
        QToolTip.add(self.refreshToolButton,self.__tr("Refresh status"))
        self.textLabel9.setText(self.__tr("Location:"))
        self.LocationText.setText(QString.null)
        self.textLabel6.setText(self.__tr("Name:"))
        self.textLabel7.setText(self.__tr("Device URI:"))
        self.DeviceURIText.setText(QString.null)
        self.textLabel10.setText(self.__tr("Comment:"))
        self.CommentText.setText(QString.null)
        self.textLabel3_2_2_2.setText(self.__tr("<b>Device information and status.</b>"))
        self.tabWidget2.changeTab(self.TabPage,self.__tr("Device"))
        self.settingsPushButton.setText(self.__tr("Settings..."))


    def individualSendListView_clicked(self,a0):
        print "FaxSendJobForm_base.individualSendListView_clicked(QListViewItem*): Not implemented yet"

    def groupSendListView_clicked(self,a0):
        print "FaxSendJobForm_base.groupSendListView_clicked(QListViewItem*): Not implemented yet"

    def addressBookButton_clicked(self):
        print "FaxSendJobForm_base.addressBookButton_clicked(): Not implemented yet"

    def sendLaterButton_clicked(self):
        print "FaxSendJobForm_base.sendLaterButton_clicked(): Not implemented yet"

    def sendNowButton_clicked(self):
        print "FaxSendJobForm_base.sendNowButton_clicked(): Not implemented yet"

    def addFileButton_clicked(self):
        print "FaxSendJobForm_base.addFileButton_clicked(): Not implemented yet"

    def delFileButton_clicked(self):
        print "FaxSendJobForm_base.delFileButton_clicked(): Not implemented yet"

    def addFilePushButton_clicked(self):
        print "FaxSendJobForm_base.addFilePushButton_clicked(): Not implemented yet"

    def browsePushButton_clicked(self):
        print "FaxSendJobForm_base.browsePushButton_clicked(): Not implemented yet"

    def upFileButton_clicked(self):
        print "FaxSendJobForm_base.upFileButton_clicked(): Not implemented yet"

    def downFileButton_clicked(self):
        print "FaxSendJobForm_base.downFileButton_clicked(): Not implemented yet"

    def fileEdit_textChanged(self,a0):
        print "FaxSendJobForm_base.fileEdit_textChanged(const QString&): Not implemented yet"

    def titleEdit_textChanged(self,a0):
        print "FaxSendJobForm_base.titleEdit_textChanged(const QString&): Not implemented yet"

    def addCoverpagePushButton_clicked(self):
        print "FaxSendJobForm_base.addCoverpagePushButton_clicked(): Not implemented yet"

    def refreshToolButton_clicked(self):
        print "FaxSendJobForm_base.refreshToolButton_clicked(): Not implemented yet"

    def printerNameComboBox_highlighted(self,a0):
        print "FaxSendJobForm_base.printerNameComboBox_highlighted(const QString&): Not implemented yet"

    def editCoverpagePushButton_clicked(self):
        print "FaxSendJobForm_base.editCoverpagePushButton_clicked(): Not implemented yet"

    def settingsPushButton_clicked(self):
        print "FaxSendJobForm_base.settingsPushButton_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("FaxSendJobForm_base",s,c)
