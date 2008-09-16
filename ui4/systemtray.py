#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) Copyright 2003-2008 Hewlett-Packard Development Company, L.P.
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

# Std Lib
import sys
import struct
import select
import os
import signal
import os.path

# Local
from base.g import *
from base import device, utils
from base.codes import *
from ui_utils import *

# PyQt
try:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
except ImportError:
    log.error("Python bindings for Qt4 not found. Try using --qt3. Exiting!")
    sys.exit(1)

from systrayframe import SystrayFrame
#from settingsdialog import SettingsDialog

# dbus
try:
    import dbus
    #import dbus.service
    from dbus import SessionBus, lowlevel #SystemBus,  lowlevel
    #from dbus.mainloop.qt import DBusQtMainLoop
except ImportError:
    log.error("Python bindings for dbus not found. Exiting!")
    sys.exit(1)

TRAY_MESSAGE_DELAY = 10000
HIDE_INACTIVE_DELAY = 5000


ERROR_STATE_TO_ICON = {
    ERROR_STATE_CLEAR: QSystemTrayIcon.Information, 
    ERROR_STATE_OK: QSystemTrayIcon.Information,
    ERROR_STATE_WARNING: QSystemTrayIcon.Warning,
    ERROR_STATE_ERROR: QSystemTrayIcon.Critical,
    ERROR_STATE_LOW_SUPPLIES: QSystemTrayIcon.Warning,
    ERROR_STATE_BUSY: QSystemTrayIcon.Warning,
    ERROR_STATE_LOW_PAPER: QSystemTrayIcon.Warning,
    ERROR_STATE_PRINTING: QSystemTrayIcon.Information,
    ERROR_STATE_SCANNING: QSystemTrayIcon.Information,
    ERROR_STATE_PHOTOCARD: QSystemTrayIcon.Information,
    ERROR_STATE_FAXING: QSystemTrayIcon.Information,
    ERROR_STATE_COPYING: QSystemTrayIcon.Information,
}



class SystraySettingsDialog(QDialog):
    def __init__(self, parent, systray_visible):
        QDialog.__init__(self, parent)
        self.systray_visible = systray_visible
        self.initUi()
        self.SystemTraySettings.updateUi()
    
    
    def initUi(self):
        self.setObjectName("SystraySettingsDialog")
        self.resize(QSize(QRect(0,0,488,565).size()).expandedTo(self.minimumSizeHint()))

        self.gridlayout = QGridLayout(self)
        self.gridlayout.setObjectName("gridlayout")

        self.SystemTraySettings = SystrayFrame(self)
        self.SystemTraySettings.systray_visible = self.systray_visible
        
        sizePolicy = QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SystemTraySettings.sizePolicy().hasHeightForWidth())
        self.SystemTraySettings.setSizePolicy(sizePolicy)
        self.SystemTraySettings.setFrameShadow(QFrame.Raised)
        self.SystemTraySettings.setObjectName("SystemTraySettings")
        self.gridlayout.addWidget(self.SystemTraySettings,0,0,1,2)

        spacerItem = QSpacerItem(301,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem,1,0,1,1)

        self.StdButtons = QDialogButtonBox(self)
        self.StdButtons.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.NoButton|QDialogButtonBox.Ok)
        self.StdButtons.setCenterButtons(False)
        self.StdButtons.setObjectName("StdButtons")
        self.gridlayout.addWidget(self.StdButtons,1,1,1,1)

        QObject.connect(self.StdButtons, SIGNAL("accepted()"), self.acceptClicked)
        QObject.connect(self.StdButtons, SIGNAL("rejected()"), self.reject)
        #QMetaObject.connectSlotsByName(self)

        self.setWindowTitle(self.__tr("HP Device Manager - System Tray Settings"))
    
    
    def acceptClicked(self):
        self.systray_visible = self.SystemTraySettings.systray_visible
        self.accept()
    

    def __tr(self, s, c=None):
        return QApplication.translate("SystraySettingsDialog", s, c, QApplication.UnicodeUTF8)



class SystemTrayApp(QApplication):
    def __init__(self, args, read_pipe, child_pid):
        QApplication.__init__(self, args)

        self.child_pid = child_pid
        self.read_pipe = read_pipe
        self.fmt = "64s64sI32sI64sf"
        self.fmt_size = struct.calcsize(self.fmt)

        self.user_settings = UserSettings()
        self.user_settings.load()
        
        self.tray_icon = QSystemTrayIcon()
        icon = QIcon(load_pixmap("prog", "48x48", (22, 22)))
        self.tray_icon.setIcon(icon)

        self.menu = QMenu()

        title = QWidgetAction(self.menu)
        title.setDisabled(True)

        hbox = QFrame(self.menu)
        layout = QHBoxLayout(hbox)
        layout.setMargin(3)
        layout.setSpacing(5)
        pix_label = QLabel(hbox)

        layout.insertWidget(-1, pix_label, 0)

        icon_size = self.menu.style().pixelMetric(QStyle.PM_SmallIconSize)
        pix_label.setPixmap(icon.pixmap(icon_size))

        label = QLabel(hbox)
        layout.insertWidget(-1, label, 20)
        title.setDefaultWidget(hbox)

        label.setText(self.tr("HPLIP Status Service"))

        f = label.font()
        f.setBold(True)
        label.setFont(f)
        self.menu.insertAction(None, title)

        self.menu.addSeparator()
        self.menu.addAction(self.tr("HP Device Manager..."), self.toolboxTriggered)

        self.menu.addSeparator()
        
        icon1 = QIcon(os.path.join(prop.image_dir, '16x16', 'settings.png'))
        self.settings_action = self.menu.addAction(icon1, self.tr("Settings..."),  self.settingsTriggered)

        icon3 = QIcon(os.path.join(prop.image_dir, '16x16', 'quit.png'))

        self.menu.addSeparator()
        self.menu.addAction(icon3, "Quit", self.quitTriggered)
        self.tray_icon.setContextMenu(self.menu)
        
        self.tray_icon.setToolTip("HPLIP Status Service")

        QObject.connect(self.tray_icon, SIGNAL("messageClicked()"), self.messageClicked)

        
        notifier = QSocketNotifier(self.read_pipe, QSocketNotifier.Read)
        QObject.connect(notifier, SIGNAL("activated(int)"), self.notifierActivated)

        QObject.connect(self.tray_icon, SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.trayActivated)

        self.tray_icon.show()

        if self.user_settings.systray_visible == SYSTRAY_VISIBLE_SHOW_ALWAYS:
            self.tray_icon.setVisible(True)
        else: 
            QTimer.singleShot(HIDE_INACTIVE_DELAY, self.timeoutHideWhenInactive) # show icon for awhile @ startup

        
    
    def settingsTriggered(self):
        dlg = SystraySettingsDialog(self.menu, self.user_settings.systray_visible)
        
        if dlg.exec_() == QDialog.Accepted:
            self.user_settings.systray_visible = dlg.systray_visible
            self.user_settings.save()
            
            if self.user_settings.systray_visible == SYSTRAY_VISIBLE_SHOW_ALWAYS:
                log.debug("Showing...")
                self.tray_icon.setVisible(True)
                
            else:
                log.debug("Waiting to hide...")
                QTimer.singleShot(HIDE_INACTIVE_DELAY, self.timeoutHideWhenInactive)
            
            
    def timeoutHideWhenInactive(self):
        log.debug("Hiding...")
        if self.user_settings.systray_visible in (SYSTRAY_VISIBLE_HIDE_WHEN_INACTIVE, SYSTRAY_VISIBLE_HIDE_ALWAYS): 
            self.tray_icon.setVisible(False)
            log.debug("Hidden")
            

    def trayActivated(self, reason):
        if reason == QSystemTrayIcon.Context:
            #print "context menu"
            pass

        elif reason == QSystemTrayIcon.DoubleClick:
            #print "double click"
            self.toolboxTriggered()
            pass

        elif reason == QSystemTrayIcon.Trigger:
            #print "single click"
            pass

        elif reason == QSystemTrayIcon.MiddleClick:
            #print "middle click"
            pass


    def messageClicked(self):
        #print "\nPARENT: message clicked"
        pass


    def quitTriggered(self):
        print "quit"
        self.quit()


    def toolboxTriggered(self):
        try:
            os.waitpid(-1, os.WNOHANG)
        except OSError:
            pass

        # See if it is already running...
        ok, lock_file = utils.lock_app('hp-toolbox', True)

        if ok: # able to lock, not running...
            utils.unlock(lock_file)

            path = utils.which('hp-toolbox')
            if path:
                path = os.path.join(path, 'hp-toolbox')
            else:
                self.tray_icon.showMessage(self.__tr("HPLIP Status Service"), 
                                self.__tr("Unable to locate hp-toolbox on system PATH."),
                                QSystemTrayIcon.Critical, TRAY_MESSAGE_DELAY)

                log.error("Unable to find hp-toolbox on PATH.")
                return

            #log.debug(path)
            log.debug("Running hp-toolbox: hp-toolbox --qt4")
            os.spawnlp(os.P_NOWAIT, path, 'hp-toolbox',  '--qt4')

        else: # ...already running, raise it
            args = ['', '', EVENT_RAISE_DEVICE_MANAGER, prop.username, 0, '', '']
            msg = lowlevel.SignalMessage('/', 'com.hplip.Toolbox', 'Event')
            msg.append(signature='ssisiss', *args)

            SessionBus().send_message(msg)


    def preferencesTriggered(self):
        #print "\nPARENT: prefs!"
        pass


    def notifierActivated(self, s):
        m = ''
        while True:
            ready = select.select([self.read_pipe], [], [], 1.0)

            if ready[0]:
                m = ''.join([m, os.read(self.read_pipe, self.fmt_size)])
                if len(m) == self.fmt_size:
                    event = device.Event(*struct.unpack(self.fmt, m))

                    if event.event_code == EVENT_USER_CONFIGURATION_CHANGED:
                        self.user_settings.load()

                    if self.user_settings.systray_visible in \
                        (SYSTRAY_VISIBLE_SHOW_ALWAYS, SYSTRAY_VISIBLE_HIDE_WHEN_INACTIVE):
                        
                        log.debug("Showing...")
                        self.tray_icon.setVisible(True)

                    if self.user_settings.systray_visible == SYSTRAY_VISIBLE_HIDE_WHEN_INACTIVE:
                        log.debug("Waiting to hide...")
                        QTimer.singleShot(HIDE_INACTIVE_DELAY, self.timeoutHideWhenInactive)
                    
                    if event.event_code <= EVENT_MAX_USER_EVENT and self.tray_icon.supportsMessages():
                        log.debug("Tray icon message:")
                        event.debug()
                        
                        error_state = STATUS_TO_ERROR_STATE_MAP.get(event.event_code, ERROR_STATE_CLEAR)
                        icon = ERROR_STATE_TO_ICON.get(error_state, QSystemTrayIcon.Information)
                        desc = device.queryString(event.event_code)

                        if event.job_id and event.title:
                            self.tray_icon.showMessage(self.__tr("HPLIP Device Status"), 
                                QString("%1\n%2\n%3\n(%4/%5/%6)").\
                                arg(event.device_uri).arg(event.event_code).\
                                arg(desc).arg(event.username).arg(event.job_id).arg(event.title),
                                icon, TRAY_MESSAGE_DELAY)
                        else:
                            self.tray_icon.showMessage(self.__tr("HPLIP Device Status"), 
                                QString("%1\n%2\n%3").arg(event.device_uri).\
                                arg(event.event_code).arg(desc),
                                icon, TRAY_MESSAGE_DELAY)

            else:
                break


    def __tr(self, s, c=None):
        return QApplication.translate("SystemTray", s, c, QApplication.UnicodeUTF8)

    

def run(read_pipe, child_pid):
    log.set_module("hp-systray(qt4)")
    log.debug("Child PID=%d" % child_pid)

    app = SystemTrayApp(sys.argv, read_pipe, child_pid)
    app.setQuitOnLastWindowClosed(False) # If not set, settings dlg closes app
    
    if not QSystemTrayIcon.isSystemTrayAvailable():
        FailureUI(None, 
            QApplication.translate("SystemTray", 
            "<b>No system tray detected on this system.</b><p>Unable to start, exiting.</p>", 
            None, QApplication.UnicodeUTF8),
            QApplication.translate("SystemTray", "HPLIP Status Service", 
            None, QApplication.UnicodeUTF8))
    else:
        notifier = QSocketNotifier(read_pipe, QSocketNotifier.Read)
        QObject.connect(notifier, SIGNAL("activated(int)"), app.notifierActivated)

        app.exec_()


