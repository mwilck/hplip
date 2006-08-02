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

from __future__ import generators

# Std Lib
import sys, os, os.path, mmap, struct, time, threading, Queue, socket
from cStringIO import StringIO

# Local
from base.g import *
from base.codes import *
from base import device, utils, status, pml, msg

# Event queue values (UI ==> Copy thread)
COPY_CANCELED = 1

# Update queue values (Copy thread ==> UI)
STATUS_IDLE = 0
STATUS_SETTING_UP = 1
STATUS_WARMING_UP = 2
STATUS_ACTIVE = 3
STATUS_DONE = 4
STATUS_ERROR = 5


# PML Copier Only
class PMLCopyDevice(device.Device):
    def __init__(self, device_uri=None, printer_name=None,
                 hpssd_sock=None, hpiod_sock=None, callback=None):

        device.Device.__init__(self, device_uri, printer_name,
                               hpssd_sock, hpiod_sock, callback)

        self.copy_thread = None
        
    def copy(self, num_copies=1, contrast=0, reduction=100,
             quality=pml.COPIER_QUALITY_NORMAL, 
             fit_to_page=pml.COPIER_FIT_TO_PAGE_ENABLED,
             update_queue=None, event_queue=None): 
        
        if not self.isCopyActive():
            self.copy_thread = PMLCopyThread(self, num_copies, contrast, reduction, quality, 
                                             fit_to_page, update_queue, event_queue)
            self.copy_thread.start()
            return True
        else:
            return False

    def isCopyActive(self):
        if self.copy_thread is not None:
            return self.copy_thread.isAlive()
        else:
            return False

    def waitForCopyThread(self):
        if self.copy_thread is not None and \
            self.copy_thread.isAlive():

            self.copy_thread.join()
        

        
class PMLCopyThread(threading.Thread):
    def __init__(self, dev, num_copies, contrast, reduction, quality, 
                 fit_to_page, update_queue=None, event_queue=None):

        threading.Thread.__init__(self)
        self.dev = dev
        self.num_copies = num_copies
        self.contrast = contrast
        self.reduction = reduction
        self.quality = quality
        self.fit_to_page = fit_to_page
        self.event_queue = event_queue
        self.update_queue = update_queue
        self.prev_update = ''
        
    def run(self):
        STATE_DONE = 0
        STATE_ERROR = 5
        STATE_ABORTED = 10
        STATE_SUCCESS = 20
        STATE_BUSY = 25
        STATE_SET_TOKEN = 30
        STATE_SETUP_STATE = 40
        STATE_SETUP_PARAMS = 50
        STATE_START = 60
        STATE_ACTIVE = 70
        STATE_RESET_TOKEN = 80
        
        state = STATE_SET_TOKEN
        
        while state != STATE_DONE: # ------------------------- Copier Thread
            if self.check_for_cancel():
                state = STATE_ABORTED
            
            if state == STATE_ABORTED:
                log.debug("%s State: Aborted" % ("*"*20))
                self.write_queue(STATUS_ERROR)
                state = STATE_RESET_TOKEN
                
            if state == STATE_ERROR:
                log.debug("%s State: Error" % ("*"*20))
                self.write_queue(STATUS_ERROR)
                state = STATE_RESET_TOKEN

            elif state == STATE_SUCCESS:
                log.debug("%s State: Success" % ("*"*20))
                self.write_queue(STATUS_DONE)
                state = STATE_RESET_TOKEN
                
            elif state == STATE_BUSY:
                log.debug("%s State: Busy" % ("*"*20))
                self.write_queue(STATUS_ERROR)
                state = STATE_RESET_TOKEN
                
            elif state == STATE_SET_TOKEN:
                log.debug("%s State: Acquire copy token" % ("*"*20))
                
                self.write_queue(STATUS_SETTING_UP)
                
                try:
                    result_code, token = self.dev.getPML(pml.OID_COPIER_TOKEN)
                except Error:
                    log.debug("Unable to acquire copy token (1).")
                    state = STATE_SETUP
                else:
                    if result_code > pml.ERROR_MAX_OK:
                        state = STATE_SETUP_STATE
                        log.debug("Skipping token acquisition.")
                    else:
                        token = time.strftime("%d%m%Y%H:%M:%S", time.gmtime())
                        log.debug("Setting token: %s" % token)
                        try:
                            self.dev.setPML(pml.OID_COPIER_TOKEN, token)
                        except Error:
                            log.error("Unable to acquire copy token (2).")
                            state = STATUS_ERROR
                        else:
                            result_code, check_token = self.dev.getPML(pml.OID_COPIER_TOKEN)

                            if check_token == token:
                                state = STATE_SETUP_STATE
                            else:
                                log.error("Unable to acquire copy token (3).")
                                state = STATE_ERROR
        
            elif state == STATE_SETUP_STATE:
                log.debug("%s State: Setup state" % ("*"*20))
                
                result_code, copy_state = self.dev.getPML(pml.OID_COPIER_JOB)
                
                if copy_state == pml.COPIER_JOB_IDLE:
                    self.dev.setPML(pml.OID_COPIER_JOB, pml.COPIER_JOB_SETUP)
                    state = STATE_SETUP_PARAMS
                    
                else:
                    state = STATE_BUSY
                    
                
            elif state == STATE_SETUP_PARAMS:
                log.debug("%s State: Setup Params" % ("*"*20))
                
                # num_copies
                if self.num_copies < 0: self.num_copies = 1
                if self.num_copies > 99: self.num_copies = 99
                
                self.dev.setPML(pml.OID_COPIER_JOB_NUM_COPIES, self.num_copies)
                
                # contrast
                self.dev.setPML(pml.OID_COPIER_JOB_CONTRAST, self.contrast)
                
                # reduction
                self.dev.setPML(pml.OID_COPIER_JOB_REDUCTION, self.reduction)
                
                # quality
                self.dev.setPML(pml.OID_COPIER_JOB_QUALITY, self.quality)
                
                # fit_to_page
                self.dev.setPML(pml.OID_COPIER_JOB_FIT_TO_PAGE, self.fit_to_page)
                
                log.debug("num_copies = %d" % self.num_copies)
                log.debug("contrast= %d" % self.contrast)
                log.debug("reduction = %d" % self.reduction)
                log.debug("quality = %d" % self.quality)
                log.debug("fit_to_page = %d" % self.fit_to_page)
                #log.debug("max_reduction = %d" % self.max_reduction)
                #log.debug("max_enlargement = %d" % self.max_enlargement)
                
                state = STATE_START
                
            elif state == STATE_START:
                log.debug("%s State: Start" % ("*"*20))
                
                self.dev.setPML(pml.OID_COPIER_JOB, pml.COPIER_JOB_START)
                state = STATE_ACTIVE
                
            elif state == STATE_ACTIVE:
                log.debug("%s State: Active" % ("*"*20))
                
                while True:
                    result_code, copy_state = self.dev.getPML(pml.OID_COPIER_JOB)
                    
                    if self.check_for_cancel():
                        self.dev.setPML(pml.OID_COPIER_JOB, pml.COPIER_JOB_IDLE) # cancel
                        state = STATE_ABORTED
                        break
                    
                    if copy_state == pml.COPIER_JOB_START:
                        log.debug("state = start")
                        time.sleep(1)
                        continue
                    
                    if copy_state == pml.COPIER_JOB_ACTIVE:
                        self.write_queue(STATUS_ACTIVE)
                        log.debug("state = active")
                        time.sleep(2)
                        continue
                        
                    elif copy_state == pml.COPIER_JOB_ABORTING:
                        log.debug("state = aborting")
                        state = STATE_ABORTED
                        break
                    
                    elif copy_state == pml.COPIER_JOB_IDLE:
                        log.debug("state = idle")
                        state = STATE_SUCCESS
                        break
                
            elif state == STATE_RESET_TOKEN:
                log.debug("%s State: Release copy token" % ("*"*20))
                
                try:
                    self.dev.setPML(pml.OID_COPIER_TOKEN, '\x00'*16)
                except Error:
                    log.error("Unable to release copier token.")
                    
                state = STATE_DONE
                
                
    def check_for_cancel(self):
        canceled = False
        while self.event_queue.qsize():
            try:
                event = self.event_queue.get(0)
                if event == COPY_CANCELED:
                    canceled = True
                    log.debug("Cancel pressed!")
            except Queue.Empty:
                break
    
        return canceled

    def write_queue(self, message):
        if self.update_queue is not None and message != self.prev_update:
            self.update_queue.put(message)
            time.sleep(0)
            self.prev_update = message
