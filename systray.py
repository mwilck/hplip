#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) Copyright 2003-2007 Hewlett-Packard Development Company, L.P.
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

__version__ = '2.0'
__mod__ = 'hp-systray'
__title__ = 'System Tray Status Service'
__doc__ = ""

# StdLib
import sys
import os
import getopt
import signal

# Local
from base.g import *
from base import utils, module
from prnt import cups


if __name__ == '__main__':
    mod = module.Module(__mod__, __title__, __version__, __doc__, None,
                       (GUI_MODE,), (UI_TOOLKIT_QT4, UI_TOOLKIT_QT3))

    mod.setUsage(module.USAGE_FLAG_NONE,
        extra_options=[("Startup even if no hplip CUPS queues are present:", "-x or --force-startup", "option", False)])

    opts, device_uri, printer_name, mode, ui_toolkit, lang = \
        mod.parseStdOpts('x', ['force-startup'], False)

    force_startup = False
    for o, a in opts:
        if o in ('-x', '--force-startup'):
            force_startup = True

    if os.getuid() == 0:
        log.error("hp-systray cannot be run as root. Exiting.")
        sys.exit(1)

    if ui_toolkit == 'qt3':
        if not utils.canEnterGUIMode():
            log.error("%s requires Qt3 GUI and DBus support. Exiting." % __mod__)
            sys.exit(1)
    
    else:
        if not utils.canEnterGUIMode4():
            log.error("%s requires Qt4 GUI and DBus support. Exiting." % __mod__)
            sys.exit(1)

    if not force_startup:
        # Check for any hp: or hpfax: queues. If none, exit
        if not utils.any([p.device_uri for p in cups.getPrinters()], lambda x : x.startswith('hp')):
            log.warn("No hp: or hpfax: devices found in any installed CUPS queue. Exiting.")
            sys.exit(1)

    mod.lockInstance()

    r, w = os.pipe()
    parent_pid = os.getpid()
    log.debug("Parent PID=%d" % parent_pid)
    child_pid = os.fork()

    if child_pid:
        # parent (UI)
        os.close(w)

        if ui_toolkit == 'qt3':
            import ui.systemtray as systray
        
        else: # qt4
            import ui4.systemtray as systray

        try:
            systray.run(r, child_pid)
        finally:
            log.debug("Killing child hpssd process (pid=%d)..." % child_pid)
            try:
                os.kill(child_pid, signal.SIGKILL)

            except OSError, e:
                log.debug("Failed: %s" % e)

            mod.unlockInstance()

    else:
        # child (dbus)
        os.close(r)

        try:
            import hpssd
            hpssd.run(w, parent_pid)
        finally:
            if parent_pid:
                log.debug("Killing parent systray process (pid=%d)..." % parent_pid)
                try:
                    os.kill(parent_pid, signal.SIGKILL)

                except OSError, e:
                    log.debug("Failed: %s" % e)

                mod.unlockInstance()
