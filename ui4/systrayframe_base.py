# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui4/systrayframe_base.ui'
#
# Created: Thu Sep 11 13:22:46 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,524,464).size()).expandedTo(Form.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(Form)
        self.gridlayout.setObjectName("gridlayout")

        self.groupBox_2 = QtGui.QGroupBox(Form)
        self.groupBox_2.setObjectName("groupBox_2")

        self.gridlayout1 = QtGui.QGridLayout(self.groupBox_2)
        self.gridlayout1.setObjectName("gridlayout1")

        self.ShowAlwaysRadioButton = QtGui.QRadioButton(self.groupBox_2)
        self.ShowAlwaysRadioButton.setObjectName("ShowAlwaysRadioButton")
        self.gridlayout1.addWidget(self.ShowAlwaysRadioButton,0,0,1,1)

        self.HideWhenInactiveRadioButton = QtGui.QRadioButton(self.groupBox_2)
        self.HideWhenInactiveRadioButton.setObjectName("HideWhenInactiveRadioButton")
        self.gridlayout1.addWidget(self.HideWhenInactiveRadioButton,1,0,1,1)

        self.HideAlwaysRadioButton = QtGui.QRadioButton(self.groupBox_2)
        self.HideAlwaysRadioButton.setObjectName("HideAlwaysRadioButton")
        self.gridlayout1.addWidget(self.HideAlwaysRadioButton,2,0,1,1)
        self.gridlayout.addWidget(self.groupBox_2,0,0,1,1)

        self.PollingGroupBox = QtGui.QGroupBox(Form)
        self.PollingGroupBox.setCheckable(True)
        self.PollingGroupBox.setObjectName("PollingGroupBox")

        self.gridlayout2 = QtGui.QGridLayout(self.PollingGroupBox)
        self.gridlayout2.setObjectName("gridlayout2")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.label_2 = QtGui.QLabel(self.PollingGroupBox)
        self.label_2.setObjectName("label_2")
        self.hboxlayout.addWidget(self.label_2)

        self.PollingInterval = QtGui.QSpinBox(self.PollingGroupBox)
        self.PollingInterval.setMinimum(3)
        self.PollingInterval.setMaximum(999)
        self.PollingInterval.setObjectName("PollingInterval")
        self.hboxlayout.addWidget(self.PollingInterval)

        self.label_3 = QtGui.QLabel(self.PollingGroupBox)
        self.label_3.setObjectName("label_3")
        self.hboxlayout.addWidget(self.label_3)
        self.gridlayout2.addLayout(self.hboxlayout,0,0,1,1)

        spacerItem = QtGui.QSpacerItem(201,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout2.addItem(spacerItem,0,1,1,1)

        self.label = QtGui.QLabel(self.PollingGroupBox)
        self.label.setObjectName("label")
        self.gridlayout2.addWidget(self.label,1,0,1,2)

        self.PollingListWidget = QtGui.QListWidget(self.PollingGroupBox)
        self.PollingListWidget.setObjectName("PollingListWidget")
        self.gridlayout2.addWidget(self.PollingListWidget,2,0,1,2)
        self.gridlayout.addWidget(self.PollingGroupBox,1,0,1,1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Form", "System Tray icon Visibility", None, QtGui.QApplication.UnicodeUTF8))
        self.ShowAlwaysRadioButton.setText(QtGui.QApplication.translate("Form", "Always show", None, QtGui.QApplication.UnicodeUTF8))
        self.HideWhenInactiveRadioButton.setText(QtGui.QApplication.translate("Form", "Hide when inactive", None, QtGui.QApplication.UnicodeUTF8))
        self.HideAlwaysRadioButton.setText(QtGui.QApplication.translate("Form", "Always hide", None, QtGui.QApplication.UnicodeUTF8))
        self.PollingGroupBox.setTitle(QtGui.QApplication.translate("Form", "Monitor button presses on devices", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Polling interval:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Devices to Monitor:", None, QtGui.QApplication.UnicodeUTF8))

