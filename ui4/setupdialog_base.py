# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui4/setupdialog_base.ui'
#
# Created: Thu Sep  4 15:43:41 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,600,500).size()).expandedTo(Dialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(Dialog)
        self.gridlayout.setObjectName("gridlayout")

        self.StackedWidget = QtGui.QStackedWidget(Dialog)
        self.StackedWidget.setObjectName("StackedWidget")

        self.page = QtGui.QWidget()
        self.page.setObjectName("page")

        self.gridlayout1 = QtGui.QGridLayout(self.page)
        self.gridlayout1.setObjectName("gridlayout1")

        self.label = QtGui.QLabel(self.page)

        font = QtGui.QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridlayout1.addWidget(self.label,0,0,1,4)

        self.line = QtGui.QFrame(self.page)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridlayout1.addWidget(self.line,1,0,1,4)

        self.groupBox = QtGui.QGroupBox(self.page)
        self.groupBox.setObjectName("groupBox")

        self.gridlayout2 = QtGui.QGridLayout(self.groupBox)
        self.gridlayout2.setObjectName("gridlayout2")

        self.radioButton = QtGui.QRadioButton(self.groupBox)
        self.radioButton.setObjectName("radioButton")
        self.gridlayout2.addWidget(self.radioButton,0,0,1,1)

        self.radioButton_2 = QtGui.QRadioButton(self.groupBox)
        self.radioButton_2.setObjectName("radioButton_2")
        self.gridlayout2.addWidget(self.radioButton_2,1,0,1,1)

        self.radioButton_3 = QtGui.QRadioButton(self.groupBox)
        self.radioButton_3.setEnabled(False)
        self.radioButton_3.setObjectName("radioButton_3")
        self.gridlayout2.addWidget(self.radioButton_3,2,0,1,1)
        self.gridlayout1.addWidget(self.groupBox,2,0,1,4)

        self.AdvancedPushButton = QtGui.QPushButton(self.page)
        self.AdvancedPushButton.setObjectName("AdvancedPushButton")
        self.gridlayout1.addWidget(self.AdvancedPushButton,3,0,1,1)

        spacerItem = QtGui.QSpacerItem(391,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout1.addItem(spacerItem,3,1,1,1)

        spacerItem1 = QtGui.QSpacerItem(20,21,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem1,3,2,1,1)

        self.AdvancedStackedWidget = QtGui.QStackedWidget(self.page)
        self.AdvancedStackedWidget.setFrameShape(QtGui.QFrame.Box)
        self.AdvancedStackedWidget.setObjectName("AdvancedStackedWidget")

        self.page_4 = QtGui.QWidget()
        self.page_4.setObjectName("page_4")

        self.gridlayout3 = QtGui.QGridLayout(self.page_4)
        self.gridlayout3.setObjectName("gridlayout3")

        self.groupBox_2 = QtGui.QGroupBox(self.page_4)
        self.groupBox_2.setObjectName("groupBox_2")

        self.gridlayout4 = QtGui.QGridLayout(self.groupBox_2)
        self.gridlayout4.setObjectName("gridlayout4")

        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.gridlayout4.addWidget(self.label_2,0,0,1,1)

        self.lineEdit = QtGui.QLineEdit(self.groupBox_2)
        self.lineEdit.setObjectName("lineEdit")
        self.gridlayout4.addWidget(self.lineEdit,0,1,1,3)

        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.gridlayout4.addWidget(self.label_3,1,0,1,1)

        self.comboBox = QtGui.QComboBox(self.groupBox_2)
        self.comboBox.setObjectName("comboBox")
        self.gridlayout4.addWidget(self.comboBox,1,1,1,3)

        self.label_15 = QtGui.QLabel(self.groupBox_2)
        self.label_15.setObjectName("label_15")
        self.gridlayout4.addWidget(self.label_15,2,0,1,2)

        self.comboBox_2 = QtGui.QComboBox(self.groupBox_2)
        self.comboBox_2.setObjectName("comboBox_2")
        self.gridlayout4.addWidget(self.comboBox_2,2,2,1,1)

        spacerItem2 = QtGui.QSpacerItem(271,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout4.addItem(spacerItem2,2,3,1,1)
        self.gridlayout3.addWidget(self.groupBox_2,0,0,1,1)

        self.groupBox_5 = QtGui.QGroupBox(self.page_4)
        self.groupBox_5.setObjectName("groupBox_5")

        self.gridlayout5 = QtGui.QGridLayout(self.groupBox_5)
        self.gridlayout5.setObjectName("gridlayout5")

        self.label_14 = QtGui.QLabel(self.groupBox_5)
        self.label_14.setObjectName("label_14")
        self.gridlayout5.addWidget(self.label_14,0,0,1,1)

        self.lineEdit_10 = QtGui.QLineEdit(self.groupBox_5)
        self.lineEdit_10.setObjectName("lineEdit_10")
        self.gridlayout5.addWidget(self.lineEdit_10,0,1,1,1)
        self.gridlayout3.addWidget(self.groupBox_5,1,0,1,1)
        self.AdvancedStackedWidget.addWidget(self.page_4)

        self.page_5 = QtGui.QWidget()
        self.page_5.setObjectName("page_5")
        self.AdvancedStackedWidget.addWidget(self.page_5)
        self.gridlayout1.addWidget(self.AdvancedStackedWidget,4,0,1,4)
        self.StackedWidget.addWidget(self.page)

        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName("page_2")

        self.gridlayout6 = QtGui.QGridLayout(self.page_2)
        self.gridlayout6.setObjectName("gridlayout6")

        self.label_4 = QtGui.QLabel(self.page_2)

        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridlayout6.addWidget(self.label_4,0,0,1,2)

        self.line_2 = QtGui.QFrame(self.page_2)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridlayout6.addWidget(self.line_2,1,0,1,3)

        self.tableWidget = QtGui.QTableWidget(self.page_2)
        self.tableWidget.setObjectName("tableWidget")
        self.gridlayout6.addWidget(self.tableWidget,2,0,1,3)

        self.pushButton_4 = QtGui.QPushButton(self.page_2)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridlayout6.addWidget(self.pushButton_4,3,0,1,1)

        spacerItem3 = QtGui.QSpacerItem(241,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout6.addItem(spacerItem3,3,1,1,1)

        self.pushButton_5 = QtGui.QPushButton(self.page_2)
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridlayout6.addWidget(self.pushButton_5,3,2,1,1)
        self.StackedWidget.addWidget(self.page_2)

        self.page_3 = QtGui.QWidget()
        self.page_3.setObjectName("page_3")

        self.gridlayout7 = QtGui.QGridLayout(self.page_3)
        self.gridlayout7.setObjectName("gridlayout7")

        self.label_5 = QtGui.QLabel(self.page_3)

        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridlayout7.addWidget(self.label_5,0,0,1,1)

        self.line_3 = QtGui.QFrame(self.page_3)
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridlayout7.addWidget(self.line_3,1,0,1,1)

        self.groupBox_3 = QtGui.QGroupBox(self.page_3)
        self.groupBox_3.setObjectName("groupBox_3")

        self.gridlayout8 = QtGui.QGridLayout(self.groupBox_3)
        self.gridlayout8.setObjectName("gridlayout8")

        self.label_6 = QtGui.QLabel(self.groupBox_3)
        self.label_6.setObjectName("label_6")
        self.gridlayout8.addWidget(self.label_6,0,0,1,1)

        self.lineEdit_2 = QtGui.QLineEdit(self.groupBox_3)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridlayout8.addWidget(self.lineEdit_2,0,1,1,1)

        self.label_7 = QtGui.QLabel(self.groupBox_3)
        self.label_7.setObjectName("label_7")
        self.gridlayout8.addWidget(self.label_7,1,0,1,1)

        self.lineEdit_3 = QtGui.QLineEdit(self.groupBox_3)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridlayout8.addWidget(self.lineEdit_3,1,1,1,1)

        self.label_8 = QtGui.QLabel(self.groupBox_3)
        self.label_8.setObjectName("label_8")
        self.gridlayout8.addWidget(self.label_8,2,0,1,1)

        self.lineEdit_4 = QtGui.QLineEdit(self.groupBox_3)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridlayout8.addWidget(self.lineEdit_4,2,1,1,1)
        self.gridlayout7.addWidget(self.groupBox_3,2,0,1,1)

        self.groupBox_4 = QtGui.QGroupBox(self.page_3)
        self.groupBox_4.setCheckable(True)
        self.groupBox_4.setObjectName("groupBox_4")

        self.gridlayout9 = QtGui.QGridLayout(self.groupBox_4)
        self.gridlayout9.setObjectName("gridlayout9")

        self.label_9 = QtGui.QLabel(self.groupBox_4)
        self.label_9.setObjectName("label_9")
        self.gridlayout9.addWidget(self.label_9,0,0,1,1)

        self.lineEdit_5 = QtGui.QLineEdit(self.groupBox_4)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.gridlayout9.addWidget(self.lineEdit_5,0,1,1,3)

        self.label_10 = QtGui.QLabel(self.groupBox_4)
        self.label_10.setObjectName("label_10")
        self.gridlayout9.addWidget(self.label_10,1,0,1,1)

        self.lineEdit_6 = QtGui.QLineEdit(self.groupBox_4)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.gridlayout9.addWidget(self.lineEdit_6,1,1,1,1)

        self.label_11 = QtGui.QLabel(self.groupBox_4)
        self.label_11.setObjectName("label_11")
        self.gridlayout9.addWidget(self.label_11,1,2,1,1)

        self.lineEdit_7 = QtGui.QLineEdit(self.groupBox_4)
        self.lineEdit_7.setObjectName("lineEdit_7")
        self.gridlayout9.addWidget(self.lineEdit_7,1,3,1,1)

        self.label_12 = QtGui.QLabel(self.groupBox_4)
        self.label_12.setObjectName("label_12")
        self.gridlayout9.addWidget(self.label_12,2,0,1,1)

        self.lineEdit_8 = QtGui.QLineEdit(self.groupBox_4)
        self.lineEdit_8.setObjectName("lineEdit_8")
        self.gridlayout9.addWidget(self.lineEdit_8,2,1,1,3)

        self.label_13 = QtGui.QLabel(self.groupBox_4)
        self.label_13.setObjectName("label_13")
        self.gridlayout9.addWidget(self.label_13,3,0,1,1)

        self.lineEdit_9 = QtGui.QLineEdit(self.groupBox_4)
        self.lineEdit_9.setObjectName("lineEdit_9")
        self.gridlayout9.addWidget(self.lineEdit_9,3,1,1,3)
        self.gridlayout7.addWidget(self.groupBox_4,3,0,1,1)

        spacerItem4 = QtGui.QSpacerItem(20,31,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout7.addItem(spacerItem4,4,0,1,1)

        self.checkBox = QtGui.QCheckBox(self.page_3)
        self.checkBox.setObjectName("checkBox")
        self.gridlayout7.addWidget(self.checkBox,5,0,1,1)
        self.StackedWidget.addWidget(self.page_3)
        self.gridlayout.addWidget(self.StackedWidget,0,0,1,5)

        self.StepText = QtGui.QLabel(Dialog)
        self.StepText.setObjectName("StepText")
        self.gridlayout.addWidget(self.StepText,1,0,1,1)

        spacerItem5 = QtGui.QSpacerItem(181,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem5,1,1,1,1)

        self.pushButton_3 = QtGui.QPushButton(Dialog)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridlayout.addWidget(self.pushButton_3,1,2,1,1)

        self.pushButton_2 = QtGui.QPushButton(Dialog)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridlayout.addWidget(self.pushButton_2,1,3,1,1)

        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.gridlayout.addWidget(self.pushButton,1,4,1,1)

        self.retranslateUi(Dialog)
        self.StackedWidget.setCurrentIndex(0)
        self.AdvancedStackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "HP Device Manager - Setup", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Device Discovery", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Connection (I/O) Type", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton.setText(QtGui.QApplication.translate("Dialog", "Universal Serial Bus (USB)", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_2.setText(QtGui.QApplication.translate("Dialog", "Network/Ethernet/Wireless network (direct connection or JetDirect)", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_3.setText(QtGui.QApplication.translate("Dialog", "Parallel Port (LPT)", None, QtGui.QApplication.UnicodeUTF8))
        self.AdvancedPushButton.setText(QtGui.QApplication.translate("Dialog", "Show Advanced >>", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "Discovery Options", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Search term:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Device type:", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.addItem(QtGui.QApplication.translate("Dialog", "All devices", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.addItem(QtGui.QApplication.translate("Dialog", "Single function printers", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.addItem(QtGui.QApplication.translate("Dialog", "All-in-one/MFP devices", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setText(QtGui.QApplication.translate("Dialog", "Network discovery method:", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_2.addItem(QtGui.QApplication.translate("Dialog", "SLP", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_2.addItem(QtGui.QApplication.translate("Dialog", "mDNS", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_5.setTitle(QtGui.QApplication.translate("Dialog", "Manual Discovery", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setText(QtGui.QApplication.translate("Dialog", "Parameter:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "Select From Discovered Devices", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.pushButton_4.setText(QtGui.QApplication.translate("Dialog", "Manual Discovery...", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_5.setText(QtGui.QApplication.translate("Dialog", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Dialog", "Setup Device", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Dialog", "Printer Setup", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Dialog", "Printer name:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Dialog", "Description:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Dialog", "Location:", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setTitle(QtGui.QApplication.translate("Dialog", "Fax Setup", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Dialog", "Fax name:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("Dialog", "Fax number:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("Dialog", "Name/company:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("Dialog", "Description:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_13.setText(QtGui.QApplication.translate("Dialog", "Location:", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("Dialog", "Send test page to printer", None, QtGui.QApplication.UnicodeUTF8))
        self.StepText.setText(QtGui.QApplication.translate("Dialog", "Step %1 of %2", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("Dialog", "< Back", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("Dialog", "Next >", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Dialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

