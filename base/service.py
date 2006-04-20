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


#Std Lib
import socket

# Local
from g import *
from codes import *
import msg


def registerGUI(sock, username, host, port, pid, typ):
    msg.sendEvent(sock,
                  "RegisterGUIEvent",
                  None,
                  { 'username' : username,
                    'hostname' : host,
                    'port' : port,
                    'pid' : pid,
                    'type' : typ }
                  )


def unregisterGUI(sock, username, pid, typ):
    msg.sendEvent(sock,
                   "UnRegisterGUIEvent",
                   None,
                   {
                       'username' : username,
                       'pid' : pid,
                       'type' : typ,
                   }
                  )



def testEmail(sock, email_address, smtp_server, username, password):
    fields = {}
    result_code = ERROR_SUCCESS
    try:
        fields, data, result_code = \
            msg.xmitMessage(sock,
                            "TestEmail",
                            None,
                            {
                                'email-address' : email_address,
                                'smtp-server' : smtp_server,
                                'username'      : username,
                                'server-pass'   : password,
                            }
                            )
    except Error, e:
        result_code = e.opt
        utils.log_exception()

    return result_code


def sendEvent(sock, event, typ='event', jobid=0, 
              username=prop.username, device_uri='', 
              other_fields={}, data=None):
    
    fields = {'job-id'        : jobid,
              'event-type'    : typ,
              'event-code'    : event,
              'username'      : username,
              'device-uri'    : device_uri,
              'retry-timeout' : 0,}

    if other_fields:
        fields.update(other_fields)

    msg.sendEvent(sock, 'Event', data, fields)



def setAlerts(sock, email_alerts, email_address, smtp_server):
    fields, data, result_code = \
        msg.xmitMessage(sock,
                        "SetAlerts",
                        None,
                        {
                            'username'      : prop.username,
                            'email-alerts'  : email_alerts,
                            'email-address' : email_address,
                            'smtp-server'   : smtp_server,
                        }
                        )
