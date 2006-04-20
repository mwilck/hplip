# -*- coding: utf-8 -*-

from base.g import *
from qt import *
from supportform_base import SupportForm_base
from base import utils
import os.path

class SupportForm(SupportForm_base):

    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        SupportForm_base.__init__(self,parent,name,modal,fl)

    def hpinktjetButton_clicked(self):
        utils.openURL("http://hpinkjet.sourceforge.net")

    def linuxprintingButton_clicked(self):
        utils.openURL("http://linuxprinting.org")

    def linuxprintingButton_2_clicked(self):
        utils.openURL("http://cups.org")
        
    def hpinktjetButton_2_clicked(self):
        utils.openURL("file://" + os.path.join(prop.home_dir ,"hplip_readme.html"))
    
