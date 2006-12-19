# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unloadform_base.ui'
#
# Created: Tue Oct 24 15:31:40 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class UnloadForm_base(QMainWindow):
    def __init__(self,parent = None,name = None,fl = 0):
        QMainWindow.__init__(self,parent,name,fl)
        self.statusBar()

        if not name:
            self.setName("UnloadForm_base")


        self.setCentralWidget(QWidget(self,"qt_central_widget"))
        UnloadForm_baseLayout = QGridLayout(self.centralWidget(),1,1,11,6,"UnloadForm_baseLayout")

        self.groupBox2 = QGroupBox(self.centralWidget(),"groupBox2")
        self.groupBox2.setColumnLayout(0,Qt.Vertical)
        self.groupBox2.layout().setSpacing(6)
        self.groupBox2.layout().setMargin(11)
        groupBox2Layout = QGridLayout(self.groupBox2.layout())
        groupBox2Layout.setAlignment(Qt.AlignTop)

        self.DeviceText = QLabel(self.groupBox2,"DeviceText")

        groupBox2Layout.addWidget(self.DeviceText,0,0)

        UnloadForm_baseLayout.addMultiCellWidget(self.groupBox2,0,0,0,2)

        self.UnloadButton = QPushButton(self.centralWidget(),"UnloadButton")

        UnloadForm_baseLayout.addWidget(self.UnloadButton,4,2)
        spacer1 = QSpacerItem(211,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        UnloadForm_baseLayout.addItem(spacer1,4,0)

        self.CancelButton = QPushButton(self.centralWidget(),"CancelButton")

        UnloadForm_baseLayout.addWidget(self.CancelButton,4,1)

        self.groupBox3 = QGroupBox(self.centralWidget(),"groupBox3")
        self.groupBox3.setColumnLayout(0,Qt.Vertical)
        self.groupBox3.layout().setSpacing(6)
        self.groupBox3.layout().setMargin(11)
        groupBox3Layout = QGridLayout(self.groupBox3.layout())
        groupBox3Layout.setAlignment(Qt.AlignTop)

        self.UnloadDirectoryEdit = QLineEdit(self.groupBox3,"UnloadDirectoryEdit")

        groupBox3Layout.addWidget(self.UnloadDirectoryEdit,0,0)

        self.UnloadDirectoryBrowseButton = QPushButton(self.groupBox3,"UnloadDirectoryBrowseButton")

        groupBox3Layout.addWidget(self.UnloadDirectoryBrowseButton,0,1)

        UnloadForm_baseLayout.addMultiCellWidget(self.groupBox3,2,2,0,2)

        self.FileRemovalGroup = QButtonGroup(self.centralWidget(),"FileRemovalGroup")
        self.FileRemovalGroup.setColumnLayout(0,Qt.Vertical)
        self.FileRemovalGroup.layout().setSpacing(6)
        self.FileRemovalGroup.layout().setMargin(11)
        FileRemovalGroupLayout = QGridLayout(self.FileRemovalGroup.layout())
        FileRemovalGroupLayout.setAlignment(Qt.AlignTop)

        self.LeaveAllRadio = QRadioButton(self.FileRemovalGroup,"LeaveAllRadio")
        self.LeaveAllRadio.setChecked(1)

        FileRemovalGroupLayout.addWidget(self.LeaveAllRadio,0,0)

        self.RemoveSelectedRadio = QRadioButton(self.FileRemovalGroup,"RemoveSelectedRadio")

        FileRemovalGroupLayout.addWidget(self.RemoveSelectedRadio,1,0)

        UnloadForm_baseLayout.addMultiCellWidget(self.FileRemovalGroup,3,3,0,2)

        self.groupBox1 = QGroupBox(self.centralWidget(),"groupBox1")
        self.groupBox1.setColumnLayout(0,Qt.Vertical)
        self.groupBox1.layout().setSpacing(6)
        self.groupBox1.layout().setMargin(11)
        groupBox1Layout = QGridLayout(self.groupBox1.layout())
        groupBox1Layout.setAlignment(Qt.AlignTop)

        self.IconView = QIconView(self.groupBox1,"IconView")
        self.IconView.setResizePolicy(QIconView.AutoOneFit)
        self.IconView.setSelectionMode(QIconView.Multi)
        self.IconView.setResizeMode(QIconView.Adjust)
        self.IconView.setMaxItemWidth(200)
        self.IconView.setAutoArrange(0)
        self.IconView.setItemsMovable(1)

        groupBox1Layout.addMultiCellWidget(self.IconView,0,0,0,3)

        self.SelectAllButton = QPushButton(self.groupBox1,"SelectAllButton")

        groupBox1Layout.addWidget(self.SelectAllButton,1,0)

        self.SelectNoneButton = QPushButton(self.groupBox1,"SelectNoneButton")

        groupBox1Layout.addWidget(self.SelectNoneButton,1,1)

        self.ShowThumbnailsButton = QPushButton(self.groupBox1,"ShowThumbnailsButton")

        groupBox1Layout.addWidget(self.ShowThumbnailsButton,1,3)
        spacer2 = QSpacerItem(360,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox1Layout.addItem(spacer2,1,2)

        UnloadForm_baseLayout.addMultiCellWidget(self.groupBox1,1,1,0,2)



        self.MenuBar = QMenuBar(self,"MenuBar")



        self.languageChange()

        self.resize(QSize(550,538).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.SelectAllButton,SIGNAL("clicked()"),self.SelectAllButton_clicked)
        self.connect(self.SelectNoneButton,SIGNAL("clicked()"),self.SelectNoneButton_clicked)
        self.connect(self.IconView,SIGNAL("doubleClicked(QIconViewItem*)"),self.IconView_doubleClicked)
        self.connect(self.UnloadDirectoryBrowseButton,SIGNAL("clicked()"),self.UnloadDirectoryBrowseButton_clicked)
        self.connect(self.UnloadButton,SIGNAL("clicked()"),self.UnloadButton_clicked)
        self.connect(self.IconView,SIGNAL("rightButtonClicked(QIconViewItem*,const QPoint&)"),self.IconView_rightButtonClicked)
        self.connect(self.FileRemovalGroup,SIGNAL("clicked(int)"),self.FileRemovalGroup_clicked)
        self.connect(self.IconView,SIGNAL("clicked(QIconViewItem*)"),self.IconView_clicked)
        self.connect(self.IconView,SIGNAL("selectionChanged()"),self.IconView_selectionChanged)
        self.connect(self.ShowThumbnailsButton,SIGNAL("clicked()"),self.ShowThumbnailsButton_clicked)
        self.connect(self.CancelButton,SIGNAL("clicked()"),self.CancelButton_clicked)


    def languageChange(self):
        self.setCaption(self.__tr("HP Device Manager - Unload Files from Photo Card"))
        self.groupBox2.setTitle(self.__tr("Device:"))
        self.DeviceText.setText(QString.null)
        self.UnloadButton.setText(self.__tr("Unload Selected Files"))
        self.CancelButton.setText(self.__tr("Close"))
        self.groupBox3.setTitle(self.__tr("Unload Directory:"))
        self.UnloadDirectoryBrowseButton.setText(self.__tr("Browse..."))
        self.FileRemovalGroup.setTitle(self.__tr("File Removal:"))
        self.LeaveAllRadio.setText(self.__tr("Leave all files on photo card"))
        self.RemoveSelectedRadio.setText(self.__tr("Remove selected files"))
        self.groupBox1.setTitle(self.__tr("Select Files to Unload from Photo Card:"))
        self.SelectAllButton.setText(self.__tr("Select All"))
        self.SelectNoneButton.setText(self.__tr("Select None"))
        self.ShowThumbnailsButton.setText(self.__tr("Show Thumbnails"))


    def fileNew(self):
        print "UnloadForm_base.fileNew(): Not implemented yet"

    def fileOpen(self):
        print "UnloadForm_base.fileOpen(): Not implemented yet"

    def fileSave(self):
        print "UnloadForm_base.fileSave(): Not implemented yet"

    def fileSaveAs(self):
        print "UnloadForm_base.fileSaveAs(): Not implemented yet"

    def filePrint(self):
        print "UnloadForm_base.filePrint(): Not implemented yet"

    def fileExit(self):
        print "UnloadForm_base.fileExit(): Not implemented yet"

    def editUndo(self):
        print "UnloadForm_base.editUndo(): Not implemented yet"

    def editRedo(self):
        print "UnloadForm_base.editRedo(): Not implemented yet"

    def editCut(self):
        print "UnloadForm_base.editCut(): Not implemented yet"

    def editCopy(self):
        print "UnloadForm_base.editCopy(): Not implemented yet"

    def editPaste(self):
        print "UnloadForm_base.editPaste(): Not implemented yet"

    def editFind(self):
        print "UnloadForm_base.editFind(): Not implemented yet"

    def helpIndex(self):
        print "UnloadForm_base.helpIndex(): Not implemented yet"

    def helpContents(self):
        print "UnloadForm_base.helpContents(): Not implemented yet"

    def helpAbout(self):
        print "UnloadForm_base.helpAbout(): Not implemented yet"

    def SelectAllButton_clicked(self):
        print "UnloadForm_base.SelectAllButton_clicked(): Not implemented yet"

    def SelectNoneButton_clicked(self):
        print "UnloadForm_base.SelectNoneButton_clicked(): Not implemented yet"

    def IconView_doubleClicked(self,a0):
        print "UnloadForm_base.IconView_doubleClicked(QIconViewItem*): Not implemented yet"

    def UnloadDirectoryBrowseButton_clicked(self):
        print "UnloadForm_base.UnloadDirectoryBrowseButton_clicked(): Not implemented yet"

    def UnloadButton_clicked(self):
        print "UnloadForm_base.UnloadButton_clicked(): Not implemented yet"

    def IconView_rightButtonClicked(self,a0,a1):
        print "UnloadForm_base.IconView_rightButtonClicked(QIconViewItem*,const QPoint&): Not implemented yet"

    def FileRemovalGroup_clicked(self,a0):
        print "UnloadForm_base.FileRemovalGroup_clicked(int): Not implemented yet"

    def IconView_selectionChanged(self,a0):
        print "UnloadForm_base.IconView_selectionChanged(QIconViewItem*): Not implemented yet"

    def IconView_clicked(self,a0,a1):
        print "UnloadForm_base.IconView_clicked(QIconViewItem*,const QPoint&): Not implemented yet"

    def IconView_clicked(self,a0):
        print "UnloadForm_base.IconView_clicked(QIconViewItem*): Not implemented yet"

    def IconView_currentChanged(self,a0):
        print "UnloadForm_base.IconView_currentChanged(QIconViewItem*): Not implemented yet"

    def IconView_selectionChanged(self):
        print "UnloadForm_base.IconView_selectionChanged(): Not implemented yet"

    def ShowThumbnailsButton_clicked(self):
        print "UnloadForm_base.ShowThumbnailsButton_clicked(): Not implemented yet"

    def CancelButton_clicked(self):
        print "UnloadForm_base.CancelButton_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("UnloadForm_base",s,c)
