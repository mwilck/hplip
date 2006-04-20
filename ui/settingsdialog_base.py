# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settingsdialog_base.ui'
#
# Created: Fri Aug 19 15:40:05 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class SettingsDialog_base(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("SettingsDialog_base")


        SettingsDialog_baseLayout = QGridLayout(self,1,1,11,6,"SettingsDialog_baseLayout")

        self.pushButton30 = QPushButton(self,"pushButton30")

        SettingsDialog_baseLayout.addWidget(self.pushButton30,1,3)

        self.pushButton31 = QPushButton(self,"pushButton31")

        SettingsDialog_baseLayout.addWidget(self.pushButton31,1,2)

        self.TabWidget = QTabWidget(self,"TabWidget")

        self.CleaningLevels = QWidget(self.TabWidget,"CleaningLevels")
        CleaningLevelsLayout = QGridLayout(self.CleaningLevels,1,1,11,6,"CleaningLevelsLayout")

        self.textLabel3_2_2 = QLabel(self.CleaningLevels,"textLabel3_2_2")

        CleaningLevelsLayout.addWidget(self.textLabel3_2_2,0,0)

        self.line1_2_2 = QFrame(self.CleaningLevels,"line1_2_2")
        self.line1_2_2.setFrameShape(QFrame.HLine)
        self.line1_2_2.setFrameShadow(QFrame.Sunken)
        self.line1_2_2.setFrameShape(QFrame.HLine)

        CleaningLevelsLayout.addWidget(self.line1_2_2,1,0)
        spacer8 = QSpacerItem(20,200,QSizePolicy.Minimum,QSizePolicy.Expanding)
        CleaningLevelsLayout.addItem(spacer8,3,0)

        self.CleaningLevel = QButtonGroup(self.CleaningLevels,"CleaningLevel")
        self.CleaningLevel.setColumnLayout(0,Qt.Vertical)
        self.CleaningLevel.layout().setSpacing(6)
        self.CleaningLevel.layout().setMargin(11)
        CleaningLevelLayout = QGridLayout(self.CleaningLevel.layout())
        CleaningLevelLayout.setAlignment(Qt.AlignTop)
        spacer9_2 = QSpacerItem(181,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        CleaningLevelLayout.addItem(spacer9_2,0,1)

        layout7 = QHBoxLayout(None,0,6,"layout7")

        self.AutoRefreshRate = QSpinBox(self.CleaningLevel,"AutoRefreshRate")
        self.AutoRefreshRate.setWrapping(1)
        self.AutoRefreshRate.setButtonSymbols(QSpinBox.PlusMinus)
        self.AutoRefreshRate.setMaxValue(360)
        self.AutoRefreshRate.setMinValue(5)
        layout7.addWidget(self.AutoRefreshRate)

        self.textLabel1_3 = QLabel(self.CleaningLevel,"textLabel1_3")
        layout7.addWidget(self.textLabel1_3)

        CleaningLevelLayout.addLayout(layout7,0,0)

        CleaningLevelsLayout.addWidget(self.CleaningLevel,2,0)
        self.TabWidget.insertTab(self.CleaningLevels,QString.fromLatin1(""))

        self.EmailAlerts = QWidget(self.TabWidget,"EmailAlerts")
        EmailAlertsLayout = QGridLayout(self.EmailAlerts,1,1,11,6,"EmailAlertsLayout")

        self.textLabel3_2 = QLabel(self.EmailAlerts,"textLabel3_2")

        EmailAlertsLayout.addMultiCellWidget(self.textLabel3_2,0,0,0,2)

        self.textLabel21 = QLabel(self.EmailAlerts,"textLabel21")

        EmailAlertsLayout.addMultiCellWidget(self.textLabel21,4,4,0,1)

        self.textLabel20 = QLabel(self.EmailAlerts,"textLabel20")

        EmailAlertsLayout.addMultiCellWidget(self.textLabel20,3,3,0,1)

        self.EmailAddress = QLineEdit(self.EmailAlerts,"EmailAddress")
        self.EmailAddress.setEnabled(0)

        EmailAlertsLayout.addWidget(self.EmailAddress,3,2)

        self.SMTPServer = QLineEdit(self.EmailAlerts,"SMTPServer")
        self.SMTPServer.setEnabled(0)

        EmailAlertsLayout.addWidget(self.SMTPServer,4,2)

        self.line1_2_2_2 = QFrame(self.EmailAlerts,"line1_2_2_2")
        self.line1_2_2_2.setFrameShape(QFrame.HLine)
        self.line1_2_2_2.setFrameShadow(QFrame.Sunken)
        self.line1_2_2_2.setFrameShape(QFrame.HLine)

        EmailAlertsLayout.addMultiCellWidget(self.line1_2_2_2,1,1,0,2)

        layout1 = QGridLayout(None,1,1,0,6,"layout1")

        self.Username = QLineEdit(self.EmailAlerts,"Username")
        self.Username.setEnabled(0)

        layout1.addWidget(self.Username,0,1)

        self.textLabel1 = QLabel(self.EmailAlerts,"textLabel1")

        layout1.addWidget(self.textLabel1,0,0)

        self.textLabel2 = QLabel(self.EmailAlerts,"textLabel2")

        layout1.addWidget(self.textLabel2,1,0)

        self.Password = QLineEdit(self.EmailAlerts,"Password")
        self.Password.setEnabled(0)
        self.Password.setEchoMode(QLineEdit.Password)

        layout1.addWidget(self.Password,1,1)

        EmailAlertsLayout.addLayout(layout1,6,2)

        self.ServerRequiresPasswd = QCheckBox(self.EmailAlerts,"ServerRequiresPasswd")
        self.ServerRequiresPasswd.setEnabled(0)

        EmailAlertsLayout.addWidget(self.ServerRequiresPasswd,5,2)

        self.EmailCheckBox = QCheckBox(self.EmailAlerts,"EmailCheckBox")

        EmailAlertsLayout.addMultiCellWidget(self.EmailCheckBox,2,2,0,2)
        spacer11 = QSpacerItem(471,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        EmailAlertsLayout.addMultiCell(spacer11,7,7,1,2)
        spacer5 = QSpacerItem(20,71,QSizePolicy.Minimum,QSizePolicy.Expanding)
        EmailAlertsLayout.addItem(spacer5,8,2)

        self.EmailTestButton = QPushButton(self.EmailAlerts,"EmailTestButton")

        EmailAlertsLayout.addWidget(self.EmailTestButton,7,0)
        spacer12 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        EmailAlertsLayout.addItem(spacer12,8,0)
        self.TabWidget.insertTab(self.EmailAlerts,QString.fromLatin1(""))

        self.FunctionCommands = QWidget(self.TabWidget,"FunctionCommands")
        FunctionCommandsLayout = QGridLayout(self.FunctionCommands,1,1,11,6,"FunctionCommandsLayout")

        self.line1_2_2_3 = QFrame(self.FunctionCommands,"line1_2_2_3")
        self.line1_2_2_3.setFrameShape(QFrame.HLine)
        self.line1_2_2_3.setFrameShadow(QFrame.Sunken)
        self.line1_2_2_3.setFrameShape(QFrame.HLine)

        FunctionCommandsLayout.addMultiCellWidget(self.line1_2_2_3,1,1,0,1)

        self.textLabel3_2_2_2 = QLabel(self.FunctionCommands,"textLabel3_2_2_2")

        FunctionCommandsLayout.addMultiCellWidget(self.textLabel3_2_2_2,0,0,0,1)

        self.textLabel1_2 = QLabel(self.FunctionCommands,"textLabel1_2")

        FunctionCommandsLayout.addMultiCellWidget(self.textLabel1_2,2,2,0,1)

        layout8 = QHBoxLayout(None,0,6,"layout8")

        self.PrintCommand = QLineEdit(self.FunctionCommands,"PrintCommand")
        layout8.addWidget(self.PrintCommand)

        FunctionCommandsLayout.addMultiCellLayout(layout8,3,3,0,1)

        self.textLabel1_2_2 = QLabel(self.FunctionCommands,"textLabel1_2_2")

        FunctionCommandsLayout.addMultiCellWidget(self.textLabel1_2_2,4,4,0,1)

        layout9 = QHBoxLayout(None,0,6,"layout9")

        self.ScanCommand = QLineEdit(self.FunctionCommands,"ScanCommand")
        layout9.addWidget(self.ScanCommand)

        FunctionCommandsLayout.addMultiCellLayout(layout9,5,5,0,1)

        self.textLabel1_2_3_3 = QLabel(self.FunctionCommands,"textLabel1_2_3_3")

        FunctionCommandsLayout.addMultiCellWidget(self.textLabel1_2_3_3,6,6,0,1)

        layout10 = QHBoxLayout(None,0,6,"layout10")

        self.AccessPCardCommand = QLineEdit(self.FunctionCommands,"AccessPCardCommand")
        layout10.addWidget(self.AccessPCardCommand)

        FunctionCommandsLayout.addMultiCellLayout(layout10,7,7,0,1)

        self.textLabel1_2_3 = QLabel(self.FunctionCommands,"textLabel1_2_3")
        self.textLabel1_2_3.setEnabled(1)

        FunctionCommandsLayout.addMultiCellWidget(self.textLabel1_2_3,8,8,0,1)

        layout11 = QHBoxLayout(None,0,6,"layout11")

        self.SendFaxCommand = QLineEdit(self.FunctionCommands,"SendFaxCommand")
        self.SendFaxCommand.setEnabled(1)
        layout11.addWidget(self.SendFaxCommand)

        FunctionCommandsLayout.addMultiCellLayout(layout11,9,9,0,1)

        self.textLabel1_2_3_2 = QLabel(self.FunctionCommands,"textLabel1_2_3_2")
        self.textLabel1_2_3_2.setEnabled(0)

        FunctionCommandsLayout.addMultiCellWidget(self.textLabel1_2_3_2,10,10,0,1)

        layout12 = QHBoxLayout(None,0,6,"layout12")

        self.MakeCopiesCommand = QLineEdit(self.FunctionCommands,"MakeCopiesCommand")
        self.MakeCopiesCommand.setEnabled(0)
        layout12.addWidget(self.MakeCopiesCommand)

        FunctionCommandsLayout.addMultiCellLayout(layout12,11,11,0,1)

        self.DefaultsButton = QPushButton(self.FunctionCommands,"DefaultsButton")
        self.DefaultsButton.setEnabled(1)

        FunctionCommandsLayout.addWidget(self.DefaultsButton,13,0)
        spacer8_2 = QSpacerItem(471,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        FunctionCommandsLayout.addItem(spacer8_2,13,1)
        spacer9 = QSpacerItem(20,81,QSizePolicy.Minimum,QSizePolicy.Expanding)
        FunctionCommandsLayout.addItem(spacer9,12,0)
        self.TabWidget.insertTab(self.FunctionCommands,QString.fromLatin1(""))

        SettingsDialog_baseLayout.addMultiCellWidget(self.TabWidget,0,0,0,3)
        spacer40 = QSpacerItem(430,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        SettingsDialog_baseLayout.addItem(spacer40,1,1)

        self.languageChange()

        self.resize(QSize(627,481).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.pushButton31,SIGNAL("clicked()"),self.reject)
        self.connect(self.pushButton30,SIGNAL("clicked()"),self.accept)
        self.connect(self.EmailCheckBox,SIGNAL("toggled(bool)"),self.EmailAddress.setEnabled)
        self.connect(self.EmailCheckBox,SIGNAL("toggled(bool)"),self.SMTPServer.setEnabled)
        self.connect(self.ServerRequiresPasswd,SIGNAL("toggled(bool)"),self.Username.setEnabled)
        self.connect(self.ServerRequiresPasswd,SIGNAL("toggled(bool)"),self.Password.setEnabled)
        self.connect(self.CleaningLevel,SIGNAL("clicked(int)"),self.CleaningLevel_clicked)
        self.connect(self.DefaultsButton,SIGNAL("clicked()"),self.DefaultsButton_clicked)
        self.connect(self.TabWidget,SIGNAL("currentChanged(QWidget*)"),self.TabWidget_currentChanged)
        self.connect(self.EmailTestButton,SIGNAL("clicked()"),self.EmailTestButton_clicked)

        self.setTabOrder(self.TabWidget,self.pushButton30)
        self.setTabOrder(self.pushButton30,self.pushButton31)
        self.setTabOrder(self.pushButton31,self.EmailAddress)
        self.setTabOrder(self.EmailAddress,self.SMTPServer)
        self.setTabOrder(self.SMTPServer,self.Username)
        self.setTabOrder(self.Username,self.Password)
        self.setTabOrder(self.Password,self.ServerRequiresPasswd)
        self.setTabOrder(self.ServerRequiresPasswd,self.EmailCheckBox)
        self.setTabOrder(self.EmailCheckBox,self.EmailTestButton)
        self.setTabOrder(self.EmailTestButton,self.PrintCommand)
        self.setTabOrder(self.PrintCommand,self.ScanCommand)
        self.setTabOrder(self.ScanCommand,self.AccessPCardCommand)
        self.setTabOrder(self.AccessPCardCommand,self.SendFaxCommand)
        self.setTabOrder(self.SendFaxCommand,self.MakeCopiesCommand)
        self.setTabOrder(self.MakeCopiesCommand,self.DefaultsButton)


    def languageChange(self):
        self.setCaption(self.__tr("HP Device Manager - Settings"))
        self.pushButton30.setText(self.__tr("OK"))
        self.pushButton31.setText(self.__tr("Cancel"))
        self.textLabel3_2_2.setText(self.__tr("<b>Configure the rate at which devices are automaically refreshed</b>"))
        self.CleaningLevel.setTitle(self.__tr("Auto refresh rate"))
        self.textLabel1_3.setText(self.__tr("seconds"))
        self.TabWidget.changeTab(self.CleaningLevels,self.__tr("Auto Refresh"))
        self.textLabel3_2.setText(self.__tr("<b>Configure if the HP Device Manager will send email on alerts</b>"))
        self.textLabel21.setText(self.__tr("SMTP server name:"))
        self.textLabel20.setText(self.__tr("Email address(es):"))
        self.textLabel1.setText(self.__tr("Username:"))
        self.textLabel2.setText(self.__tr("Password:"))
        self.ServerRequiresPasswd.setText(self.__tr("Server requires username and password:"))
        self.EmailCheckBox.setText(self.__tr("Send email when status alerts occur:"))
        self.EmailTestButton.setText(self.__tr("Test"))
        self.TabWidget.changeTab(self.EmailAlerts,self.__tr("Email Alerts"))
        self.textLabel3_2_2_2.setText(self.__tr("<b>Configure what commands to run for device functions</b>"))
        self.textLabel1_2.setText(self.__tr("Print Command"))
        self.textLabel1_2_2.setText(self.__tr("Scan Command"))
        self.textLabel1_2_3_3.setText(self.__tr("Access Photo Cards Command"))
        self.textLabel1_2_3.setText(self.__tr("Send Fax Command"))
        self.textLabel1_2_3_2.setText(self.__tr("Make Copies Command"))
        self.DefaultsButton.setText(self.__tr("Set Defaults"))
        self.TabWidget.changeTab(self.FunctionCommands,self.__tr("Function Commands"))


    def PrintCmdChangeButton_clicked(self):
        print "SettingsDialog_base.PrintCmdChangeButton_clicked(): Not implemented yet"

    def ScanCmdChangeButton_clicked(self):
        print "SettingsDialog_base.ScanCmdChangeButton_clicked(): Not implemented yet"

    def AccessPCardCmdChangeButton_clicked(self):
        print "SettingsDialog_base.AccessPCardCmdChangeButton_clicked(): Not implemented yet"

    def SendFaxCmdChangeButton_clicked(self):
        print "SettingsDialog_base.SendFaxCmdChangeButton_clicked(): Not implemented yet"

    def MakeCopiesCmdChangeButton_clicked(self):
        print "SettingsDialog_base.MakeCopiesCmdChangeButton_clicked(): Not implemented yet"

    def CleaningLevel_clicked(self,a0):
        print "SettingsDialog_base.CleaningLevel_clicked(int): Not implemented yet"

    def pushButton5_clicked(self):
        print "SettingsDialog_base.pushButton5_clicked(): Not implemented yet"

    def DefaultsButton_clicked(self):
        print "SettingsDialog_base.DefaultsButton_clicked(): Not implemented yet"

    def TabWidget_currentChanged(self,a0):
        print "SettingsDialog_base.TabWidget_currentChanged(QWidget*): Not implemented yet"

    def pushButton6_clicked(self):
        print "SettingsDialog_base.pushButton6_clicked(): Not implemented yet"

    def EmailTestButton_clicked(self):
        print "SettingsDialog_base.EmailTestButton_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("SettingsDialog_base",s,c)
