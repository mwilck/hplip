# -*- coding: utf-8 -*-

from qt import *
from informationform_base import InformationForm_base


class InformationForm(InformationForm_base):

    def __init__(self, dev, parent = None,name = None,modal = 0,fl = 0):
        InformationForm_base.__init__(self,parent,name,modal,fl)

        dq_keys = dev.dq.keys()
        dq_keys.sort()
        dq_keys.reverse()
        for key,i in zip(dq_keys, range(len(dq_keys))):
            QListViewItem(self.listView1, key, str(dev.dq[key]))

        mq_keys = dev.mq.keys()
        mq_keys.sort()
        mq_keys.reverse()
        for key,i in zip(mq_keys, range(len(mq_keys))):
            QListViewItem(self.listView1, key, str(dev.mq[key]))

