# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/dwelch/linux-imaging-and-printing/src/ui/informationform_base.ui'
#
# Created: Tue Aug 30 13:48:23 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class InformationForm_base(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("InformationForm_base")


        InformationForm_baseLayout = QGridLayout(self,1,1,11,6,"InformationForm_baseLayout")

        self.listView1 = QListView(self,"listView1")
        self.listView1.addColumn(self.__tr("Key"))
        self.listView1.addColumn(self.__tr("Value"))

        InformationForm_baseLayout.addMultiCellWidget(self.listView1,0,0,0,1)

        self.pushButton3 = QPushButton(self,"pushButton3")

        InformationForm_baseLayout.addWidget(self.pushButton3,1,1)
        spacer20 = QSpacerItem(471,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        InformationForm_baseLayout.addItem(spacer20,1,0)

        self.languageChange()

        self.resize(QSize(600,480).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.pushButton3,SIGNAL("clicked()"),self.accept)


    def languageChange(self):
        self.setCaption(self.__tr("HP Device Manager - Device Information"))
        self.listView1.header().setLabel(0,self.__tr("Key"))
        self.listView1.header().setLabel(1,self.__tr("Value"))
        self.pushButton3.setText(self.__tr("Close"))


    def __tr(self,s,c = None):
        return qApp.translate("InformationForm_base",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = InformationForm_base()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
