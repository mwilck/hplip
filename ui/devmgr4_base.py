# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'devmgr4_base.ui'
#
# Created: Fri May 5 14:41:40 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class DevMgr4_base(QMainWindow):
    def __init__(self,parent = None,name = None,fl = 0):
        QMainWindow.__init__(self,parent,name,fl)
        self.statusBar()

        if not name:
            self.setName("DevMgr4_base")


        self.setCentralWidget(QWidget(self,"qt_central_widget"))
        DevMgr4_baseLayout = QGridLayout(self.centralWidget(),1,1,11,6,"DevMgr4_baseLayout")

        self.splitter2 = QSplitter(self.centralWidget(),"splitter2")
        self.splitter2.setOrientation(QSplitter.Horizontal)

        self.DeviceList = QIconView(self.splitter2,"DeviceList")
        self.DeviceList.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.DeviceList.sizePolicy().hasHeightForWidth()))
        self.DeviceList.setMaximumSize(QSize(32767,32767))
        self.DeviceList.setResizePolicy(QIconView.Manual)
        self.DeviceList.setArrangement(QIconView.TopToBottom)
        self.DeviceList.setResizeMode(QIconView.Adjust)

        self.Tabs = QTabWidget(self.splitter2,"Tabs")

        self.TabPage = QWidget(self.Tabs,"TabPage")
        TabPageLayout = QGridLayout(self.TabPage,1,1,11,6,"TabPageLayout")

        self.ConfigureFeaturesButton = QPushButton(self.TabPage,"ConfigureFeaturesButton")

        TabPageLayout.addWidget(self.ConfigureFeaturesButton,7,1)
        spacer11_2 = QSpacerItem(321,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TabPageLayout.addItem(spacer11_2,7,0)
        spacer10 = QSpacerItem(20,80,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout.addItem(spacer10,6,1)

        self.ScanButton = QPushButton(self.TabPage,"ScanButton")
        self.ScanButton.setEnabled(0)

        TabPageLayout.addMultiCellWidget(self.ScanButton,2,2,0,1)

        self.PCardButton = QPushButton(self.TabPage,"PCardButton")
        self.PCardButton.setEnabled(0)

        TabPageLayout.addMultiCellWidget(self.PCardButton,3,3,0,1)

        self.SendFaxButton = QPushButton(self.TabPage,"SendFaxButton")
        self.SendFaxButton.setEnabled(0)

        TabPageLayout.addMultiCellWidget(self.SendFaxButton,4,4,0,1)

        self.MakeCopiesButton = QPushButton(self.TabPage,"MakeCopiesButton")
        self.MakeCopiesButton.setEnabled(0)

        TabPageLayout.addMultiCellWidget(self.MakeCopiesButton,5,5,0,1)
        spacer12_2 = QSpacerItem(20,90,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout.addItem(spacer12_2,0,0)

        self.PrintButton = QPushButton(self.TabPage,"PrintButton")
        self.PrintButton.setEnabled(0)

        TabPageLayout.addMultiCellWidget(self.PrintButton,1,1,0,1)
        self.Tabs.insertTab(self.TabPage,QString.fromLatin1(""))

        self.StatusTab = QWidget(self.Tabs,"StatusTab")
        StatusTabLayout = QGridLayout(self.StatusTab,1,1,11,6,"StatusTabLayout")

        self.StatusGroupBox = QGroupBox(self.StatusTab,"StatusGroupBox")
        self.StatusGroupBox.setColumnLayout(0,Qt.Vertical)
        self.StatusGroupBox.layout().setSpacing(6)
        self.StatusGroupBox.layout().setMargin(11)
        StatusGroupBoxLayout = QGridLayout(self.StatusGroupBox.layout())
        StatusGroupBoxLayout.setAlignment(Qt.AlignTop)

        self.StatusText = QLabel(self.StatusGroupBox,"StatusText")
        StatusText_font = QFont(self.StatusText.font())
        StatusText_font.setBold(1)
        self.StatusText.setFont(StatusText_font)
        self.StatusText.setFrameShape(QLabel.NoFrame)

        StatusGroupBoxLayout.addWidget(self.StatusText,0,0)

        self.StatusIcon = QLabel(self.StatusGroupBox,"StatusIcon")
        self.StatusIcon.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.StatusIcon.sizePolicy().hasHeightForWidth()))
        self.StatusIcon.setMinimumSize(QSize(32,32))
        self.StatusIcon.setMaximumSize(QSize(32,32))
        self.StatusIcon.setScaledContents(1)

        StatusGroupBoxLayout.addWidget(self.StatusIcon,0,1)

        self.StatusText2 = QLabel(self.StatusGroupBox,"StatusText2")
        StatusText2_font = QFont(self.StatusText2.font())
        StatusText2_font.setItalic(1)
        self.StatusText2.setFont(StatusText2_font)
        self.StatusText2.setFrameShape(QLabel.NoFrame)

        StatusGroupBoxLayout.addMultiCellWidget(self.StatusText2,1,1,0,1)

        StatusTabLayout.addWidget(self.StatusGroupBox,0,0)

        self.groupBox3 = QGroupBox(self.StatusTab,"groupBox3")
        self.groupBox3.setColumnLayout(0,Qt.Vertical)
        self.groupBox3.layout().setSpacing(6)
        self.groupBox3.layout().setMargin(11)
        groupBox3Layout = QGridLayout(self.groupBox3.layout())
        groupBox3Layout.setAlignment(Qt.AlignTop)

        self.StatusHistoryList = QListView(self.groupBox3,"StatusHistoryList")
        self.StatusHistoryList.addColumn(QString.null)
        self.StatusHistoryList.header().setResizeEnabled(0,self.StatusHistoryList.header().count() - 1)
        self.StatusHistoryList.addColumn(self.__tr("Date"))
        self.StatusHistoryList.addColumn(self.__tr("Time"))
        self.StatusHistoryList.addColumn(self.__tr("User"))
        self.StatusHistoryList.addColumn(self.__tr("Job ID"))
        self.StatusHistoryList.addColumn(self.__tr("Code"))
        self.StatusHistoryList.addColumn(self.__tr("Description"))
        self.StatusHistoryList.setEnabled(1)
        self.StatusHistoryList.setSelectionMode(QListView.Single)
        self.StatusHistoryList.setAllColumnsShowFocus(1)

        groupBox3Layout.addWidget(self.StatusHistoryList,0,0)

        StatusTabLayout.addWidget(self.groupBox3,1,0)
        self.Tabs.insertTab(self.StatusTab,QString.fromLatin1(""))

        self.MaintTab = QWidget(self.Tabs,"MaintTab")
        self.Tabs.insertTab(self.MaintTab,QString.fromLatin1(""))

        self.SuppliesTab = QWidget(self.Tabs,"SuppliesTab")
        self.Tabs.insertTab(self.SuppliesTab,QString.fromLatin1(""))

        self.TabPage_2 = QWidget(self.Tabs,"TabPage_2")
        TabPageLayout_2 = QGridLayout(self.TabPage_2,1,1,11,6,"TabPageLayout_2")

        self.PrintJobList = QListView(self.TabPage_2,"PrintJobList")
        self.PrintJobList.addColumn(self.__tr("Queue"))
        self.PrintJobList.addColumn(self.__tr("Job ID"))
        self.PrintJobList.addColumn(self.__tr("Status"))
        self.PrintJobList.addColumn(self.__tr("User"))
        self.PrintJobList.addColumn(self.__tr("Title"))
        self.PrintJobList.setAllColumnsShowFocus(1)

        TabPageLayout_2.addMultiCellWidget(self.PrintJobList,0,0,0,1)

        self.CancelPrintJobButton = QPushButton(self.TabPage_2,"CancelPrintJobButton")
        self.CancelPrintJobButton.setEnabled(0)

        TabPageLayout_2.addWidget(self.CancelPrintJobButton,1,1)
        spacer12_3 = QSpacerItem(471,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TabPageLayout_2.addItem(spacer12_3,1,0)
        self.Tabs.insertTab(self.TabPage_2,QString.fromLatin1(""))

        self.TabPage_3 = QWidget(self.Tabs,"TabPage_3")
        TabPageLayout_3 = QGridLayout(self.TabPage_3,1,1,11,6,"TabPageLayout_3")

        self.groupBox9_2 = QGroupBox(self.TabPage_3,"groupBox9_2")
        self.groupBox9_2.setColumnLayout(0,Qt.Vertical)
        self.groupBox9_2.layout().setSpacing(6)
        self.groupBox9_2.layout().setMargin(11)
        groupBox9_2Layout = QGridLayout(self.groupBox9_2.layout())
        groupBox9_2Layout.setAlignment(Qt.AlignTop)

        self.Panel = QLabel(self.groupBox9_2,"Panel")
        self.Panel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.Panel.sizePolicy().hasHeightForWidth()))
        self.Panel.setMinimumSize(QSize(254,40))
        self.Panel.setMaximumSize(QSize(254,40))
        self.Panel.setFrameShape(QLabel.NoFrame)
        self.Panel.setScaledContents(1)

        groupBox9_2Layout.addWidget(self.Panel,1,1)
        spacer11_3 = QSpacerItem(20,101,QSizePolicy.Minimum,QSizePolicy.Expanding)
        groupBox9_2Layout.addItem(spacer11_3,0,1)
        spacer12_4 = QSpacerItem(20,181,QSizePolicy.Minimum,QSizePolicy.Expanding)
        groupBox9_2Layout.addItem(spacer12_4,2,1)
        spacer13_3 = QSpacerItem(121,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox9_2Layout.addItem(spacer13_3,1,2)
        spacer14_2 = QSpacerItem(151,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox9_2Layout.addItem(spacer14_2,1,0)

        TabPageLayout_3.addWidget(self.groupBox9_2,0,0)
        self.Tabs.insertTab(self.TabPage_3,QString.fromLatin1(""))

        DevMgr4_baseLayout.addWidget(self.splitter2,0,0)

        self.helpContentsAction = QAction(self,"helpContentsAction")
        self.helpIndexAction = QAction(self,"helpIndexAction")
        self.helpIndexAction.setEnabled(0)
        self.helpAboutAction = QAction(self,"helpAboutAction")
        self.deviceRescanAction = QAction(self,"deviceRescanAction")
        self.deviceExitAction = QAction(self,"deviceExitAction")
        self.settingsPopupAlertsAction = QAction(self,"settingsPopupAlertsAction")
        self.settingsEmailAlertsAction = QAction(self,"settingsEmailAlertsAction")
        self.settingsConfigure = QAction(self,"settingsConfigure")
        self.deviceRefreshAll = QAction(self,"deviceRefreshAll")
        self.autoRefresh = QAction(self,"autoRefresh")
        self.autoRefresh.setToggleAction(1)
        self.autoRefresh.setOn(1)
        self.setupDevice = QAction(self,"setupDevice")
        self.setupDevice.setEnabled(0)
        self.viewSupportAction = QAction(self,"viewSupportAction")




        self.MenuBar = QMenuBar(self,"MenuBar")

        self.MenuBar.setAcceptDrops(0)

        self.Device = QPopupMenu(self)
        self.setupDevice.addTo(self.Device)
        self.Device.insertSeparator()
        self.deviceRescanAction.addTo(self.Device)
        self.deviceRefreshAll.addTo(self.Device)
        self.Device.insertSeparator()
        self.deviceExitAction.addTo(self.Device)
        self.MenuBar.insertItem(QString(""),self.Device,2)

        self.Configure = QPopupMenu(self)
        self.settingsConfigure.addTo(self.Configure)
        self.MenuBar.insertItem(QString(""),self.Configure,3)

        self.helpMenu = QPopupMenu(self)
        self.helpContentsAction.addTo(self.helpMenu)
        self.helpMenu.insertSeparator()
        self.helpAboutAction.addTo(self.helpMenu)
        self.MenuBar.insertItem(QString(""),self.helpMenu,4)

        self.MenuBar.insertSeparator(5)


        self.languageChange()

        self.resize(QSize(838,493).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.helpIndexAction,SIGNAL("activated()"),self.helpIndex)
        self.connect(self.helpContentsAction,SIGNAL("activated()"),self.helpContents)
        self.connect(self.helpAboutAction,SIGNAL("activated()"),self.helpAbout)
        self.connect(self.deviceExitAction,SIGNAL("activated()"),self.close)
        self.connect(self.deviceRescanAction,SIGNAL("activated()"),self.deviceRescanAction_activated)
        self.connect(self.settingsEmailAlertsAction,SIGNAL("activated()"),self.settingsEmailAlertsAction_activated)
        self.connect(self.settingsConfigure,SIGNAL("activated()"),self.settingsConfigure_activated)
        self.connect(self.DeviceList,SIGNAL("currentChanged(QIconViewItem*)"),self.DeviceList_currentChanged)
        self.connect(self.PrintButton,SIGNAL("clicked()"),self.PrintButton_clicked)
        self.connect(self.ScanButton,SIGNAL("clicked()"),self.ScanButton_clicked)
        self.connect(self.PCardButton,SIGNAL("clicked()"),self.PCardButton_clicked)
        self.connect(self.SendFaxButton,SIGNAL("clicked()"),self.SendFaxButton_clicked)
        self.connect(self.MakeCopiesButton,SIGNAL("clicked()"),self.MakeCopiesButton_clicked)
        self.connect(self.ConfigureFeaturesButton,SIGNAL("clicked()"),self.ConfigureFeaturesButton_clicked)
        self.connect(self.deviceRefreshAll,SIGNAL("activated()"),self.deviceRefreshAll_activated)
        self.connect(self.DeviceList,SIGNAL("clicked(QIconViewItem*)"),self.DeviceList_clicked)
        self.connect(self.autoRefresh,SIGNAL("toggled(bool)"),self.autoRefresh_toggled)
        self.connect(self.PrintJobList,SIGNAL("currentChanged(QListViewItem*)"),self.PrintJobList_currentChanged)
        self.connect(self.CancelPrintJobButton,SIGNAL("clicked()"),self.CancelPrintJobButton_clicked)
        self.connect(self.PrintJobList,SIGNAL("selectionChanged(QListViewItem*)"),self.PrintJobList_selectionChanged)
        self.connect(self.DeviceList,SIGNAL("rightButtonClicked(QIconViewItem*,const QPoint&)"),self.DeviceList_rightButtonClicked)
        self.connect(self.setupDevice,SIGNAL("activated()"),self.setupDevice_activated)
        self.connect(self.viewSupportAction,SIGNAL("activated()"),self.viewSupportAction_activated)


    def languageChange(self):
        self.setCaption(self.__tr("HP Device Manager"))
        self.ConfigureFeaturesButton.setText(self.__tr("Configure..."))
        self.ScanButton.setText(self.__tr("Scan..."))
        self.PCardButton.setText(self.__tr("Access Photo Cards..."))
        self.SendFaxButton.setText(self.__tr("Send Fax..."))
        self.MakeCopiesButton.setText(self.__tr("Make Copies..."))
        self.PrintButton.setText(self.__tr("Print..."))
        self.Tabs.changeTab(self.TabPage,self.__tr("Functions"))
        self.StatusGroupBox.setTitle(self.__tr("Last"))
        self.StatusText.setText(QString.null)
        self.StatusText2.setText(QString.null)
        self.groupBox3.setTitle(self.__tr("History"))
        self.StatusHistoryList.header().setLabel(0,QString.null)
        self.StatusHistoryList.header().setLabel(1,self.__tr("Date"))
        self.StatusHistoryList.header().setLabel(2,self.__tr("Time"))
        self.StatusHistoryList.header().setLabel(3,self.__tr("User"))
        self.StatusHistoryList.header().setLabel(4,self.__tr("Job ID"))
        self.StatusHistoryList.header().setLabel(5,self.__tr("Code"))
        self.StatusHistoryList.header().setLabel(6,self.__tr("Description"))
        self.Tabs.changeTab(self.StatusTab,self.__tr("Status"))
        self.Tabs.changeTab(self.MaintTab,self.__tr("Tools && Settings"))
        self.Tabs.changeTab(self.SuppliesTab,self.__tr("Supplies"))
        self.PrintJobList.header().setLabel(0,self.__tr("Queue"))
        self.PrintJobList.header().setLabel(1,self.__tr("Job ID"))
        self.PrintJobList.header().setLabel(2,self.__tr("Status"))
        self.PrintJobList.header().setLabel(3,self.__tr("User"))
        self.PrintJobList.header().setLabel(4,self.__tr("Title"))
        self.CancelPrintJobButton.setText(self.__tr("Cancel Job"))
        self.Tabs.changeTab(self.TabPage_2,self.__tr("Print Jobs"))
        self.groupBox9_2.setTitle(self.__tr("Front Panel Display"))
        self.Tabs.changeTab(self.TabPage_3,self.__tr("Panel"))
        self.helpContentsAction.setText(self.__tr("Contents"))
        self.helpContentsAction.setMenuText(self.__tr("&Contents..."))
        self.helpContentsAction.setToolTip(self.__tr("Help Contents (F1)"))
        self.helpIndexAction.setText(self.__tr("Index"))
        self.helpIndexAction.setMenuText(self.__tr("&Index..."))
        self.helpIndexAction.setAccel(QString.null)
        self.helpAboutAction.setText(self.__tr("&About..."))
        self.helpAboutAction.setMenuText(self.__tr("&About..."))
        self.helpAboutAction.setToolTip(self.__tr("About HP Device Manager..."))
        self.deviceRescanAction.setText(self.__tr("Refresh Device"))
        self.deviceRescanAction.setMenuText(self.__tr("Refresh Device"))
        self.deviceRescanAction.setToolTip(self.__tr("Refresh Device (F5)"))
        self.deviceRescanAction.setAccel(self.__tr("F5"))
        self.deviceExitAction.setText(self.__tr("Exit"))
        self.deviceExitAction.setMenuText(self.__tr("Exit"))
        self.deviceExitAction.setToolTip(self.__tr("Exit HP Device Manager"))
        self.deviceExitAction.setAccel(self.__tr("Ctrl+Q"))
        self.settingsPopupAlertsAction.setText(self.__tr("Popup Alerts..."))
        self.settingsPopupAlertsAction.setMenuText(self.__tr("Popup alerts..."))
        self.settingsPopupAlertsAction.setToolTip(self.__tr("Configure popup alerts"))
        self.settingsEmailAlertsAction.setText(self.__tr("Email alerts..."))
        self.settingsEmailAlertsAction.setMenuText(self.__tr("Email alerts..."))
        self.settingsEmailAlertsAction.setToolTip(self.__tr("Configure email alerts"))
        self.settingsConfigure.setText(self.__tr("Settings..."))
        self.settingsConfigure.setAccel(self.__tr("F2"))
        self.deviceRefreshAll.setText(self.__tr("Refresh All"))
        self.deviceRefreshAll.setAccel(self.__tr("F6"))
        self.autoRefresh.setText(self.__tr("Auto Refresh"))
        self.autoRefresh.setToolTip(self.__tr("Turn on/off Auto Refresh (Ctrl+A)"))
        self.autoRefresh.setAccel(self.__tr("Ctrl+A"))
        self.setupDevice.setText(self.__tr("Action"))
        self.setupDevice.setMenuText(self.__tr("Settings..."))
        self.setupDevice.setToolTip(self.__tr("Device Settings (F3)"))
        self.setupDevice.setAccel(self.__tr("F3"))
        self.viewSupportAction.setText(self.__tr("Support..."))
        if self.MenuBar.findItem(2):
            self.MenuBar.findItem(2).setText(self.__tr("Device"))
        if self.MenuBar.findItem(3):
            self.MenuBar.findItem(3).setText(self.__tr("Configure"))
        if self.MenuBar.findItem(4):
            self.MenuBar.findItem(4).setText(self.__tr("&Help"))


    def fileNew(self):
        print "DevMgr4_base.fileNew(): Not implemented yet"

    def fileOpen(self):
        print "DevMgr4_base.fileOpen(): Not implemented yet"

    def fileSave(self):
        print "DevMgr4_base.fileSave(): Not implemented yet"

    def fileSaveAs(self):
        print "DevMgr4_base.fileSaveAs(): Not implemented yet"

    def filePrint(self):
        print "DevMgr4_base.filePrint(): Not implemented yet"

    def fileExit(self):
        print "DevMgr4_base.fileExit(): Not implemented yet"

    def editUndo(self):
        print "DevMgr4_base.editUndo(): Not implemented yet"

    def editRedo(self):
        print "DevMgr4_base.editRedo(): Not implemented yet"

    def editCut(self):
        print "DevMgr4_base.editCut(): Not implemented yet"

    def editCopy(self):
        print "DevMgr4_base.editCopy(): Not implemented yet"

    def editPaste(self):
        print "DevMgr4_base.editPaste(): Not implemented yet"

    def editFind(self):
        print "DevMgr4_base.editFind(): Not implemented yet"

    def helpIndex(self):
        print "DevMgr4_base.helpIndex(): Not implemented yet"

    def helpContents(self):
        print "DevMgr4_base.helpContents(): Not implemented yet"

    def helpAbout(self):
        print "DevMgr4_base.helpAbout(): Not implemented yet"

    def deviceRescanAction_activated(self):
        print "DevMgr4_base.deviceRescanAction_activated(): Not implemented yet"

    def settingsEmailAlertsAction_activated(self):
        print "DevMgr4_base.settingsEmailAlertsAction_activated(): Not implemented yet"

    def DeviceList_currentChanged(self,a0):
        print "DevMgr4_base.DeviceList_currentChanged(QIconViewItem*): Not implemented yet"

    def CleanPensButton_clicked(self):
        print "DevMgr4_base.CleanPensButton_clicked(): Not implemented yet"

    def AlignPensButton_clicked(self):
        print "DevMgr4_base.AlignPensButton_clicked(): Not implemented yet"

    def PrintTestPageButton_clicked(self):
        print "DevMgr4_base.PrintTestPageButton_clicked(): Not implemented yet"

    def AdvancedInfoButton_clicked(self):
        print "DevMgr4_base.AdvancedInfoButton_clicked(): Not implemented yet"

    def ColorCalibrationButton_clicked(self):
        print "DevMgr4_base.ColorCalibrationButton_clicked(): Not implemented yet"

    def settingsConfigure_activated(self):
        print "DevMgr4_base.settingsConfigure_activated(): Not implemented yet"

    def PrintButton_clicked(self):
        print "DevMgr4_base.PrintButton_clicked(): Not implemented yet"

    def ScanButton_clicked(self):
        print "DevMgr4_base.ScanButton_clicked(): Not implemented yet"

    def PCardButton_clicked(self):
        print "DevMgr4_base.PCardButton_clicked(): Not implemented yet"

    def SendFaxButton_clicked(self):
        print "DevMgr4_base.SendFaxButton_clicked(): Not implemented yet"

    def MakeCopiesButton_clicked(self):
        print "DevMgr4_base.MakeCopiesButton_clicked(): Not implemented yet"

    def ConfigureFeaturesButton_clicked(self):
        print "DevMgr4_base.ConfigureFeaturesButton_clicked(): Not implemented yet"

    def CancelJobButton_clicked(self):
        print "DevMgr4_base.CancelJobButton_clicked(): Not implemented yet"

    def deviceRefreshAll_activated(self):
        print "DevMgr4_base.deviceRefreshAll_activated(): Not implemented yet"

    def DeviceList_clicked(self,a0):
        print "DevMgr4_base.DeviceList_clicked(QIconViewItem*): Not implemented yet"

    def autoRefresh_toggled(self,a0):
        print "DevMgr4_base.autoRefresh_toggled(bool): Not implemented yet"

    def PrintJobList_currentChanged(self,a0):
        print "DevMgr4_base.PrintJobList_currentChanged(QListViewItem*): Not implemented yet"

    def CancelPrintJobButton_clicked(self):
        print "DevMgr4_base.CancelPrintJobButton_clicked(): Not implemented yet"

    def PrintJobList_selectionChanged(self,a0):
        print "DevMgr4_base.PrintJobList_selectionChanged(QListViewItem*): Not implemented yet"

    def DeviceList_rightButtonClicked(self,a0,a1):
        print "DevMgr4_base.DeviceList_rightButtonClicked(QIconViewItem*,const QPoint&): Not implemented yet"

    def OpenEmbeddedBrowserButton_clicked(self):
        print "DevMgr4_base.OpenEmbeddedBrowserButton_clicked(): Not implemented yet"

    def deviceSettingsButton_clicked(self):
        print "DevMgr4_base.deviceSettingsButton_clicked(): Not implemented yet"

    def faxSetupWizardButton_clicked(self):
        print "DevMgr4_base.faxSetupWizardButton_clicked(): Not implemented yet"

    def faxSettingsButton_clicked(self):
        print "DevMgr4_base.faxSettingsButton_clicked(): Not implemented yet"

    def setupDevice_activated(self):
        print "DevMgr4_base.setupDevice_activated(): Not implemented yet"

    def viewSupportAction_activated(self):
        print "DevMgr4_base.viewSupportAction_activated(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("DevMgr4_base",s,c)
