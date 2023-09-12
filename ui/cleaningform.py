# -*- coding: utf-8 -*-
#
# (c) Copyright 2001-2006 Hewlett-Packard Development Company, L.P.
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

#import sys
from qt import *
from cleaningform_base import CleaningForm_base
from base.g import *
import os.path

class CleaningForm(CleaningForm_base):
    def __init__(self, parent, cleaning_level, name = None, modal = 0, fl = 0):
        CleaningForm_base.__init__(self,parent,name,modal,fl)

        text = str(self.CleaningText.text())
        self.CleaningText.setText(text % str(cleaning_level + 1))
        
        text = str(self.Continue.text())
        self.Continue.setText(text % str(cleaning_level + 1))
        
        text = str(self.CleaningTitle.text())
        self.CleaningTitle.setText(text % str(cleaning_level))

        self.Icon.setPixmap(QPixmap(os.path.join(prop.image_dir, 'clean.png')))
    
