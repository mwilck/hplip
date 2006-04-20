# -*- coding: utf-8 -*-

import sys
from qt import *
from waitform_base import WaitForm_base

class WaitForm(WaitForm_base):
    def __init__(self, seconds, message=None, cancel_func=None, parent=None, name=None, modal=0, fl=0):
        WaitForm_base.__init__(self,parent,name,modal,fl)

        self.wait_timer = QTimer(self, "WaitTimer")
        self.connect(self.wait_timer, SIGNAL('timeout()'), self.wait_timer_timeout)
        self.seconds = seconds
        self.progress = 0
        self.ProgressBar.setTotalSteps(seconds)

        if seconds == 0:
            self.wait_timer.start(10)
        else:
            self.wait_timer.start(1000)

        if message is not None:
            self.setMessage(message)
            
        self.cancelPushButton.setEnabled(cancel_func is not None)
        self.cancel_func = cancel_func
        self.canceled = False

    def wait_timer_timeout(self):
        self.progress += 1
        self.ProgressBar.setProgress(self.progress)

        if self.progress == self.seconds:
            self.wait_timer.stop()
            self.close()

            
    def setMessage(self, message):
        self.textLabel3.setText(message)

        
    def cancelPushButton_clicked(self):
        self.canceled = True
        if self.cancel_func is not None:
            self.cancel_func()
        self.cancelPushButton.setEnabled(False)
        
