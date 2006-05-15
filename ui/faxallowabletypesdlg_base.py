# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'faxallowabletypesdlg_base.ui'
#
# Created: Tue Apr 11 10:58:56 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class FaxAllowableTypesDlg_base(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("FaxAllowableTypesDlg_base")


        FaxAllowableTypesDlg_baseLayout = QGridLayout(self,1,1,11,6,"FaxAllowableTypesDlg_baseLayout")

        self.line1_2 = QFrame(self,"line1_2")
        self.line1_2.setFrameShape(QFrame.HLine)
        self.line1_2.setFrameShadow(QFrame.Sunken)
        self.line1_2.setFrameShape(QFrame.HLine)

        FaxAllowableTypesDlg_baseLayout.addMultiCellWidget(self.line1_2,1,1,0,1)

        self.textLabel3_2 = QLabel(self,"textLabel3_2")
        self.textLabel3_2.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.textLabel3_2.sizePolicy().hasHeightForWidth()))

        FaxAllowableTypesDlg_baseLayout.addMultiCellWidget(self.textLabel3_2,0,0,0,1)

        self.pushButton10 = QPushButton(self,"pushButton10")

        FaxAllowableTypesDlg_baseLayout.addWidget(self.pushButton10,4,1)
        spacer7 = QSpacerItem(301,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        FaxAllowableTypesDlg_baseLayout.addItem(spacer7,4,0)

        self.allowableTypesListView = QListView(self,"allowableTypesListView")
        self.allowableTypesListView.addColumn(self.__tr("MIME Type"))
        self.allowableTypesListView.addColumn(self.__tr("Description"))
        self.allowableTypesListView.addColumn(self.__tr("Usual File Extension(s)"))
        self.allowableTypesListView.setSelectionMode(QListView.NoSelection)
        self.allowableTypesListView.setAllColumnsShowFocus(1)

        FaxAllowableTypesDlg_baseLayout.addMultiCellWidget(self.allowableTypesListView,2,2,0,1)

        self.textLabel1 = QLabel(self,"textLabel1")

        FaxAllowableTypesDlg_baseLayout.addMultiCellWidget(self.textLabel1,3,3,0,1)

        self.languageChange()

        self.resize(QSize(451,442).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.pushButton10,SIGNAL("clicked()"),self.accept)


    def languageChange(self):
        self.setCaption(self.__tr("HP Device Manager - Direct Allowable Types"))
        self.textLabel3_2.setText(self.__tr("<b>File types that can be <i>directly</i> added to a fax job.</b>"))
        self.pushButton10.setText(self.__tr("OK"))
        self.allowableTypesListView.header().setLabel(0,self.__tr("MIME Type"))
        self.allowableTypesListView.header().setLabel(1,self.__tr("Description"))
        self.allowableTypesListView.header().setLabel(2,self.__tr("Usual File Extension(s)"))
        self.textLabel1.setText(self.__tr("<i>Note: To add files types that do not appear on this list, print the document from the application that created it through the appropriate CUPS printer.</i>"))


    def __tr(self,s,c = None):
        return qApp.translate("FaxAllowableTypesDlg_base",s,c)
