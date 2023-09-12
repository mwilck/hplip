# -*- coding: utf-8 -*-
#
# (c) Copyright 2003-2006 Hewlett-Packard Development Company, L.P.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# Author: Don Welch
#

from qt import *
from base.g import *
from fax import coverpages
from coverpageform_base import CoverpageForm_base

class CoverpageForm(CoverpageForm_base):
    def __init__(self, cover_page_name='', parent=None,name=None,modal=0,fl=0):
        CoverpageForm_base.__init__(self,parent,name,modal,fl)
        pix = QPixmap(os.path.join(prop.image_dir, 'prev.png'))
        self.prevCoverpageButton.setPixmap(pix)
        pix = QPixmap(os.path.join(prop.image_dir, 'next.png'))
        self.nextCoverpageButton.setPixmap(pix)
        self.coverpage_list = coverpages.COVERPAGES.keys()
        
        if cover_page_name:
            self.coverpage_index = self.coverpage_list.index(cover_page_name)
        else:    
            self.coverpage_index = 0
            
        self.setCoverpage()
        
    def setCoverpage(self, inc=0):
        self.coverpage_index += inc
        
        if self.coverpage_index > len(self.coverpage_list) - 1:
            self.coverpage_index = 0
            
        elif self.coverpage_index < 0:
            self.coverpage_index = len(self.coverpage_list) - 1
            
        self.coverpage_name = self.coverpage_list[self.coverpage_index]
        self.data = coverpages.COVERPAGES[self.coverpage_name]
        pix = QPixmap(os.path.join(prop.image_dir, self.data[1]))
        self.coverpagePixmap.setPixmap(pix)

    def prevCoverpageButton_clicked(self):
        self.setCoverpage(-1)

    def nextCoverpageButton_clicked(self):
        self.setCoverpage(1)

    def __tr(self,s,c = None):
        return qApp.translate("CoverpageForm_base",s,c)
