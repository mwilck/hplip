#!/usr/bin/env python
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
# Authors: Don Welch, Pete Parks
#
# Thanks to Henrique M. Holschuh <hmh@debian.org> for various security patches
#
# ======================================================================
# Async code is Copyright 1996 by Sam Rushing
#
#                         All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of Sam
# Rushing not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission.
#
# SAM RUSHING DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
# NO EVENT SHALL SAM RUSHING BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# ======================================================================
#


__version__ = '7.5'
__title__ = "Services and Status Daemon"
__doc__ = "Provides various services to HPLIP client applications. Maintains persistant device status."


# Std Lib
import sys, socket, os, os.path, signal, getopt, glob, time, select
import popen2, threading, gettext, re, xml.parsers.expat, fcntl
import cStringIO, pwd

from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, \
     ENOTCONN, ESHUTDOWN, EINTR, EISCONN

# Local
from base.g import *
from base.codes import *
from base.msg import *
from base import utils, slp, device
from base.strings import string_table

# CUPS support
from prnt import cups

# Per user alert settings
alerts = {}

# Fax temp files
fax_file = {}


class ServerDevice(object):
    def __init__(self, model=''):
        self.history = utils.RingBuffer(prop.history_size)
        self.model = device.normalizeModelName(model)
        self.cache = {}
       

# Active devices - to hold event history
devices = {} # { 'device_uri' : ServerDevice, ... }

# Cache for model query data
model_cache = {} # { 'model_name'(lower) : {mq}, ...}

inter_pat = re.compile(r"""%(.*)%""", re.IGNORECASE)
direct_pat = re.compile(r'direct (.*?) "(.*?)" "(.*?)" "(.*?)"', re.IGNORECASE)

def QueryString(id, typ=0):
    id = str(id)
    try:
        s = string_table[id][typ]
    except KeyError:
        log.debug("String %s not found" % id)
        raise Error(ERROR_STRING_QUERY_FAILED)

    if type(s) == type(''):
        return s

    try:
        return s()
    except:
        raise Error(ERROR_STRING_QUERY_FAILED)



def initStrings():
    cycles = 0

    while True:

        found = False

        for s in string_table:
            short_string, long_string = string_table[s]
            short_replace, long_replace = short_string, long_string

            try:
                short_match = inter_pat.match(short_string).group(1)
            except (AttributeError, TypeError):
                short_match = None

            if short_match is not None:
                found = True

                try:
                    short_replace, dummy = string_table[short_match]
                except KeyError:
                    log.error("String interpolation error: %s" % short_match)

            try:
                long_match = inter_pat.match(long_string).group(1)
            except (AttributeError, TypeError):
                long_match = None

            if long_match is not None:
                found = True

                try:
                    dummy, long_replace = string_table[long_match]
                except KeyError:
                    log.error("String interpolation error: %s" % long_match)

            if found:
                string_table[s] = (short_replace, long_replace)

        if not found:
            break
        else:
            cycles +=1
            if cycles > 1000:
                break
                

class ModelParser:
    def __init__(self):
        self.model = {}
        self.cur_model = None
        self.stack = []
        self.model_found = False

    def startElement(self, name, attrs):
        global models

        if name in ('id', 'models'):
            return

        elif name == 'model':
            #self.model = {}
            self.cur_model = str(attrs['name']).lower()
            if self.cur_model == self.model_name:
                #log.debug( "Model found." )
                self.model_found = True
                self.stack = []
            else:
                self.cur_model = None

        elif self.cur_model is not None:
            self.stack.append(str(name).lower())

            if len(attrs):
                for a in attrs:
                    self.stack.append(str(a).lower())

                    try:
                        i = int(attrs[a])
                    except ValueError:
                        i = str(attrs[a])

                    self.model[str('-'.join(self.stack))] = i
                    self.stack.pop()

    def endElement(self, name):
        global models
        if name == 'model':
            pass
        elif name in ('id', 'models'):
            return
        else:
            if self.cur_model is not None:
                self.stack.pop()


    def charData(self, data):
        data = str(data).strip()

        if data and self.model is not None and \
            self.cur_model is not None and \
            self.stack:

            try:
                i = int(data)
            except ValueError:
                i = str(data)

            self.model[str('-'.join(self.stack))] = i

    def parseModels(self, model_name):
        self.model_name = model_name

        for g in [prop.xml_dir, os.path.join(prop.xml_dir, 'unreleased')]:

            if os.path.exists(g):
                log.debug("Searching directory: %s" % g)

                for f in glob.glob(g + "/*.xml"):
                    log.debug("Searching file: %s" % f)
                    parser = xml.parsers.expat.ParserCreate()
                    parser.StartElementHandler = self.startElement
                    parser.EndElementHandler = self.endElement
                    parser.CharacterDataHandler = self.charData
                    parser.Parse(open(f).read(), True)

                    if self.model_found:
                        log.debug("Found")
                        return self.model

        log.error("Not found")
        raise Error(ERROR_UNSUPPORTED_MODEL)



def QueryModel(model_name):
    model_name = device.normalizeModelName(model_name).lower()
    log.debug("Query model: %s" % model_name)

    if model_name in model_cache and \
        model_cache[model_name]:
            log.debug("Found")
            return model_cache[model_name]

    mq = ModelParser().parseModels(model_name)
    
    if mq:
        model_cache[model_name] = mq
    
    return mq or {}
    

socket_map = {}
loopback_trigger = None

def loop( timeout=1.0, sleep_time=0.1 ):
    while socket_map:
        r = []; w = []; e = []
        for fd, obj in socket_map.items():
            if obj.readable():
                r.append( fd )
            if obj.writable():
                w.append( fd )
        if [] == r == w == e:
            time.sleep( timeout )
        else:
            try:
                r,w,e = select.select( r, w, e, timeout )
            except select.error, err:
                if err[0] != EINTR:
                    raise Error( ERROR_INTERNAL )
                r = []; w = []; e = []

        for fd in r:
            try:
                obj = socket_map[ fd ]
            except KeyError:
                continue

            try:
                obj.handle_read_event()
            except Error, e:
                obj.handle_error( e )

        for fd in w:
            try:
                obj = socket_map[ fd ]
            except KeyError:
                continue

            try:
                obj.handle_write_event()
            except Error, e:
                obj.handle_error( e )

            time.sleep( sleep_time )


class dispatcher:
    connected = False
    accepting = False
    closing = False
    addr = None

    def __init__ (self, sock=None ):
        self.typ = ''
        self.send_events = False
        self.username = ''
        
        if sock:
            self.set_socket( sock ) 
            self.socket.setblocking( 0 )
            self.connected = True
            try:
                self.addr = sock.getpeername()
            except socket.error:
                # The addr isn't crucial
                pass
        else:
            self.socket = None

    def add_channel ( self ): 
        global socket_map
        socket_map[ self._fileno ] = self

    def del_channel( self ): 
        global socket_map
        fd = self._fileno
        if socket_map.has_key( fd ):
            del socket_map[ fd ]

    def create_socket( self, family, type ):
        self.family_and_type = family, type
        self.socket = socket.socket (family, type)
        self.socket.setblocking( 0 )
        self._fileno = self.socket.fileno()
        self.add_channel()

    def set_socket( self, sock ): 
        self.socket = sock
        self._fileno = sock.fileno()
        self.add_channel()

    def set_reuse_addr( self ):
        try:
            self.socket.setsockopt (
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt (socket.SOL_SOCKET,
                                        socket.SO_REUSEADDR) | 1
                )
        except socket.error:
            pass

    def readable (self):
        return True

    def writable (self):
        return True

    def listen (self, num):
        self.accepting = True
        return self.socket.listen( num )

    def bind( self, addr ):
        self.addr = addr
        return self.socket.bind( addr )

    def connect( self, address ):
        self.connected = False
        err = self.socket.connect_ex( address )
        if err in ( EINPROGRESS, EALREADY, EWOULDBLOCK ):
            return
        if err in (0, EISCONN):
            self.addr = address
            self.connected = True
            self.handle_connect()
        else:
            raise socket.error, err

    def accept (self):
        try:
            conn, addr = self.socket.accept()
            return conn, addr
        except socket.error, why:
            if why[0] == EWOULDBLOCK:
                pass
            else:
                raise socket.error, why

    def send (self, data):
        try:
            result = self.socket.send( data )
            return result
        except socket.error, why:
            if why[0] == EWOULDBLOCK:
                return 0
            else:
                raise socket.error, why
            return 0

    def recv( self, buffer_size ):
        try:
            data = self.socket.recv (buffer_size)
            if not data:
                self.handle_close()
                return ''
            else:
                return data
        except socket.error, why:
            if why[0] in [ECONNRESET, ENOTCONN, ESHUTDOWN]:
                self.handle_close()
                return ''
            else:
                raise socket.error, why

    def close (self):
        self.del_channel()
        self.socket.close()

    # cheap inheritance, used to pass all other attribute
    # references to the underlying socket object.
    #def __getattr__ (self, attr):
    #    return getattr (self.socket, attr)

    def handle_read_event( self ):
        if self.accepting:
            if not self.connected:
                self.connected = True
            self.handle_accept()
        elif not self.connected:
            self.handle_connect()
            self.connected = True
            self.handle_read()
        else:
            self.handle_read()

    def handle_write_event( self ):
        if not self.connected:
            self.handle_connect()
            self.connected = True
        self.handle_write()

    def handle_expt_event( self ):
        self.handle_expt()

    def handle_error( self, e ):
        log.error( "Error processing request." )
        raise Error(ERROR_INTERNAL)

    def handle_expt( self ):
        raise Error

    def handle_read( self ):
        raise Error

    def handle_write( self ):
        raise Error

    def handle_connect( self ):
        raise Error

    def handle_accept( self ):
        raise Error

    def handle_close( self ):
        self.close()


class file_wrapper:
    def __init__(self, fd):
        self.fd = fd

    def recv(self, *args):
        return os.read(self.fd, *args)

    def send(self, *args):
        return os.write(self.fd, *args)

    read = recv
    write = send

    def close(self):
        os.close(self.fd)

    def fileno(self):
        return self.fd


class file_dispatcher(dispatcher):

    def __init__(self, fd):
        dispatcher.__init__(self, None)
        self.connected = True
        self.set_file(fd)
        flags = fcntl.fcntl(fd, fcntl.F_GETFL, 0)
        flags = flags | os.O_NONBLOCK
        fcntl.fcntl(fd, fcntl.F_SETFL, flags)

    def set_file(self, fd):
        self._fileno = fd
        self.socket = file_wrapper(fd)
        self.add_channel()    


class trigger(file_dispatcher):
        def __init__(self):
            r, w = os.pipe()
            self.trigger = w
            file_dispatcher.__init__(self, r)
            self.send_events = False
            self.typ = 'trigger'

        def readable(self):
            return True

        def writable(self):
            return False

        def handle_connect(self):
            pass

        def pull_trigger(self):
            os.write(self.trigger, '.')

        def handle_read (self):
            self.recv(8192)


class hpssd_server(dispatcher):
    def __init__(self, ip, port):
        self.ip = ip
        self.send_events = False
        

        if port != 0:
            self.port = port
        else:
            self.port = socket.htons(0)

        dispatcher.__init__(self)
        self.typ = 'server'
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()

        try:
            self.bind((ip, port))
        except socket.error:
            raise Error(ERROR_UNABLE_TO_BIND_SOCKET)

        prop.hpssd_port = self.port = self.socket.getsockname()[1]
        self.listen(5)


    def writable(self):
        return False

    def readable(self):
        return self.accepting

    def handle_accept(self):
        try:
            conn, addr = self.accept()
            log.debug("Connected to client: %s:%d (%d)" % (addr[0], addr[1], self._fileno))
        except socket.error:
            log.error("Socket error on accept()")
            return
        except TypeError:
            log.error("EWOULDBLOCK exception on accept()")
            return
        handler = hpssd_handler(conn, addr, self)

    def handle_close(self):
        dispatcher.handle_close(self)


class hpssd_handler(dispatcher):
    def __init__(self, conn, addr, server):
        dispatcher.__init__(self, sock=conn)
        self.addr = addr
        self.in_buffer = ''
        self.out_buffer = ''
        self.server = server
        self.fields = {}
        self.payload = ''
        self.signal_exit = False
        self.typ = ''
        self.send_events = False 
        self.username = ''
        
        # handlers for all the messages we expect to receive
        self.handlers = {
            # Request/Reply Messages
            'probedevicesfiltered' : self.handle_probedevicesfiltered,
            'setalerts'            : self.handle_setalerts,
            'testemail'            : self.handle_test_email,
            'querymodel'           : self.handle_querymodel, # By device URI
            'modelquery'           : self.handle_modelquery, # By model (backwards compatibility)
            'queryhistory'         : self.handle_queryhistory,
            'querystring'          : self.handle_querystring,
            'setvalue'             : self.handle_setvalue, # device cache
            'getvalue'             : self.handle_getvalue, # device cache
            'injectvalue'          : self.handle_injectvalue, # model query data (debugging use)

            # Event Messages (no reply message)
            'event'                : self.handle_event,
            'registerguievent'     : self.handle_registerguievent, # register for events
            'unregisterguievent'   : self.handle_unregisterguievent,
            'exitevent'            : self.handle_exit,

            # Fax
            'hpfaxbegin'           : self.handle_hpfaxbegin,
            'hpfaxdata'            : self.handle_hpfaxdata,
            'hpfaxend'             : self.handle_hpfaxend,
            'faxgetdata'           : self.handle_faxgetdata,
            
            # Misc
            'unknown'              : self.handle_unknown,
        }


    def handle_read(self):
        log.debug("Reading data on channel (%d)" % self._fileno)
        self.in_buffer = self.recv(prop.max_message_read)

        log.debug(repr(self.in_buffer))

        if not self.in_buffer:
            return False

        remaining_msg = self.in_buffer

        while True:
            try:
                self.fields, self.payload, remaining_msg = parseMessage(remaining_msg)
            except Error, e:
                err = e.opt
                log.warn("Message parsing error: %s (%d)" % (e.msg, err))
                self.out_buffer = self.handle_unknown(err)
                log.debug(self.out_buffer)
                return True

            msg_type = self.fields.get('msg', 'unknown').lower()
            log.debug("Handling: %s %s %s" % ("*"*20, msg_type, "*"*20))
            log.debug(repr(self.in_buffer))

            try:
                self.handlers.get(msg_type, self.handle_unknown)()
            except Error:
                log.error("Unhandled exception during processing:")
                log.exception()

            try:
                self.handle_write()
            except socket.error, why:
                log.error("Socket error: %s" % why)
            
            if not remaining_msg:
                break

        return True

    def handle_unknown(self, err=ERROR_INVALID_MSG_TYPE):
        pass


    def handle_write(self):
        if not self.out_buffer:
            return

        log.debug("Sending data on channel (%d)" % self._fileno)
        log.debug(repr(self.out_buffer))
        
        while self.out_buffer:
            sent = self.send(self.out_buffer)
            self.out_buffer = self.out_buffer[sent:]

        if self.signal_exit:
            self.handle_close()


    def __checkdevice(self, device_uri):
        try:
            devices[device_uri]
        except KeyError:
            log.debug("New device: %s" % device_uri)
            try:
                back_end, is_hp, bus, model, serial, dev_file, host, port = \
                    device.parseDeviceURI(device_uri)
            except Error:
                log.error("Invalid device URI")
                return ERROR_INVALID_DEVICE_URI

            devices[device_uri] = ServerDevice(model)
        
        return ERROR_SUCCESS
            

    def handle_getvalue(self):
        device_uri = self.fields.get('device-uri', '').replace('hpfax:', 'hp:')
        value = ''
        key = self.fields.get('key', '')
        result_code = self.__checkdevice(device_uri)
        
        if result_code == ERROR_SUCCESS:
            try:
                value = devices[device_uri].cache[key]
            except KeyError:
                value, result_code = '', ERROR_INTERNAL
            
        self.out_buffer = buildResultMessage('GetValueResult', value, result_code)
        
    def handle_setvalue(self):
        device_uri = self.fields.get('device-uri', '').replace('hpfax:', 'hp:')
        key = self.fields.get('key', '')
        value = self.fields.get('value', '')
        result_code = self.__checkdevice(device_uri)
        
        if result_code == ERROR_SUCCESS:    
            devices[device_uri].cache[key] = value
        
        self.out_buffer = buildResultMessage('SetValueResult', None, ERROR_SUCCESS)
        
    def handle_queryhistory(self):
        device_uri = self.fields.get('device-uri', '').replace('hpfax:', 'hp:')
        payload = ''
        result_code = self.__checkdevice(device_uri)

        if result_code == ERROR_SUCCESS:    
            for h in devices[device_uri].history.get():
                payload = '\n'.join([payload, ','.join([str(x) for x in h])])

        self.out_buffer = buildResultMessage('QueryHistoryResult', payload, result_code)

    def handle_querymodel(self): # By device URI (used by toolbox, info, etc)
        device_uri = self.fields.get('device-uri', '').replace('hpfax:', 'hp:')
        result_code = self.__checkdevice(device_uri)
        mq = {}
        
        if result_code == ERROR_SUCCESS:    
            try:
                back_end, is_hp, bus, model, \
                    serial, dev_file, host, port = \
                    device.parseDeviceURI(device_uri)
            except Error:
                result_code = e.opt
            else:
                try:
                    mq = QueryModel(model)
                except Error, e:
                    mq = {}
                    result_code = e.opt
    
        self.out_buffer = buildResultMessage('QueryModelResult', None, result_code, mq)


    def handle_modelquery(self): # By model (used by hp: backend)
        model = self.fields.get('model', '')
        result_code = ERROR_SUCCESS

        try:
            mq = QueryModel(model)
        except Error, e:
            mq = {}
            result_code = e.opt

        self.out_buffer = buildResultMessage('ModelQueryResult', None, result_code, mq)

    def handle_injectvalue(self): # Tweak MQ values at runtime
        device_uri = self.fields.get('device-uri', '').replace('hpfax:', 'hp:')
        model = self.fields.get('model', '')
        result_code = ERROR_INTERNAL
        
        if not model and device_uri:
            try:
                back_end, is_hp, bus, model, \
                    serial, dev_file, host, port = \
                    device.parseDeviceURI(device_uri)
            except Error:
                result_code = e.opt
        
        log.debug(model)
        
        if model:
            key = self.fields.get('key', '')
            value = self.fields.get('value', '')
            
            if key and value: 
                if QueryModel(model):
                    if model.lower() in model_cache:
                        model_cache[model.lower()][key] = value
                        result_code = ERROR_SUCCESS
                
        self.out_buffer = buildResultMessage('InjectValueResult', None, result_code)
        

    # TODO: Need to load alerts at start-up
    def handle_setalerts(self):
        result_code = ERROR_SUCCESS
        username = self.fields.get('username', '')

        alerts[username] = {'email-alerts'       : utils.to_bool(self.fields.get('email-alerts', '0')),
                            'email-from-address' : self.fields.get('email-from-address', ''),
                            'email-to-addresses' : self.fields.get('email-to-addresses', ''),
                           }

        self.out_buffer = buildResultMessage('SetAlertsResult', None, result_code)


    # EVENT
    def handle_registerguievent(self):
        username = self.fields.get('username', '')
        typ = self.fields.get('type', 'unknown')
        self.typ = typ
        self.username = username
        self.send_events = True
        log.debug("Registering GUI for events: (%s, %s, %d)" % (username, typ, self._fileno))

    # EVENT
    def handle_unregisterguievent(self):
        username = self.fields.get('username', '')
        self.send_events = False


    def handle_test_email(self):
        result_code = ERROR_SUCCESS
        username = self.fields.get('username', prop.username)

        try:
            message = QueryString('email_test_message')
        except Error:
            message = ''
            
        try:
            subject = QueryString('email_test_subject')
        except Error:
            subject = ''

        result_code = self.sendEmail(username, subject, message, True)
        self.out_buffer = buildResultMessage('TestEmailResult', None, result_code)


    def handle_querystring(self):
        payload, result_code = '', ERROR_SUCCESS
        string_id = self.fields['string-id']
        try:
            payload = QueryString(string_id)
        except Error:
            log.error("String query failed for id %s" % string_id)
            payload = None
            result_code = ERROR_STRING_QUERY_FAILED

        self.out_buffer = buildResultMessage('QueryStringResult', payload, result_code)

        
    def createHistory(self, device_uri, code, jobid=0, username=prop.username):
        result_code = self.__checkdevice(device_uri)
        
        if result_code == ERROR_SUCCESS:    
            try:
                short_string = QueryString(code, 0)
            except Error:
                short_string, long_string = '', ''
            else:
                try:
                    long_string = QueryString(code, 1)
                except Error:
                    pass

            devices[device_uri].history.append(tuple(time.localtime()) +
                                                (jobid, username, code,
                                                 short_string, long_string))
                                                 
            # return True if added code is the same 
            # as the previous code (dup_event)
            try:
                prev_code = devices[device_uri].history.get()[-2][11]
            except IndexError:
                return False
            else:
                return code == prev_code
                
        
    # sent by hpfax: to indicate the start of a complete fax rendering job
    def handle_hpfaxbegin(self):      
        global fax_file
        username = self.fields.get('username', prop.username)
        job_id = self.fields.get('job-id', 0)
        printer_name = self.fields.get('printer', '')
        device_uri = self.fields.get('device-uri', '').replace('hp:', 'hpfax:')
        title = self.fields.get('title', '')
        
        # Send an early warning to the hp-sendfax UI so that
        # the response time to something happening is as short as possible
        result_code = ERROR_GUI_NOT_AVAILABLE
        
        for handler in socket_map:
            handler_obj = socket_map[handler]        
            
            log.debug("sendevents=%s, type=%s, username=%s" % (handler_obj.send_events, handler_obj.typ, handler_obj.username))
            
            if handler_obj.send_events and \
                handler_obj.typ == 'fax' and \
                handler_obj.username == username:
                
                # send event to already running hp-sendfax
                handler_obj.out_buffer = \
                    buildMessage('EventGUI', 
                                '\n\n',
                                {'job-id' : job_id,
                                 'event-code' : EVENT_FAX_RENDER_DISTANT_EARLY_WARNING,
                                 'event-type' : 'event',
                                 'retry-timeout' : 0,
                                 'device-uri' : device_uri,
                                 'printer' : printer_name,
                                 'title' : title,
                                })
                
                loopback_trigger.pull_trigger()        
                result_code = ERROR_SUCCESS

                # Only create a data store if a UI was found
                log.debug("Creating data store for %s:%d" % (username, job_id))
                fax_file[(username, job_id)] = cStringIO.StringIO()
                
                break
        
        # hpfax: will repeatedly send HPFaxBegin messages until it gets a 
        # ERROR_SUCCESS result code. (every 30sec)
        self.out_buffer = buildResultMessage('HPFaxBeginResult', None, result_code)
        
        
    # sent by hpfax: to transfer completed fax rendering data
    def handle_hpfaxdata(self):
        global fax_file
        username = self.fields.get('username', prop.username)
        job_id = self.fields.get('job-id', 0)
        
        if self.payload and (username, job_id) in fax_file:
            fax_file[(username, job_id)].write(self.payload)
            
        self.out_buffer = buildResultMessage('HPFaxDataResult', None, ERROR_SUCCESS)
        
            
    # sent by hpfax: to indicate the end of a complete fax rendering job
    def handle_hpfaxend(self):
        global fax_file
        
        username = self.fields.get('username', '')
        job_id = self.fields.get('job-id', 0)
        printer_name = self.fields.get('printer', '')
        device_uri = self.fields.get('device-uri', '').replace('hp:', 'hpfax:')
        title = self.fields.get('title', '')
        job_size = self.fields.get('job-size', 0)
        
        fax_file[(username, job_id)].seek(0)
        
        #print username, job_id, printer_name, device_uri, title, job_size
        
        for handler in socket_map:
            handler_obj = socket_map[handler]        
            
            #print handler_obj.send_events, handler_obj.typ, handler_obj.username
            
            if handler_obj.send_events and \
                handler_obj.typ == 'fax' and \
                handler_obj.username == username:
                
                # send event to already running hp-sendfax
                handler_obj.out_buffer = \
                    buildMessage('EventGUI', 
                                '\n\n',
                                {'job-id' : job_id,
                                 'event-code' : EVENT_FAX_RENDER_COMPLETE,
                                 'event-type' : 'event',
                                 'retry-timeout' : 0,
                                 'device-uri' : device_uri,
                                 'printer' : printer_name,
                                 'title' : title,
                                 'job-size': job_size,
                                })        
                
                loopback_trigger.pull_trigger()
                break

        self.out_buffer = buildResultMessage('HPFaxEndResult', None, ERROR_SUCCESS)

        
    # sent by hp-sendfax to retrieve a complete fax rendering job
    # sent in response to the EVENT_FAX_RENDER_COMPLETE event or
    # after being run with --job param, both after a hpfaxend message
    def handle_faxgetdata(self):
        global fax_file
        result_code = ERROR_SUCCESS
        username = self.fields.get('username', '')
        job_id = self.fields.get('job-id', 0)
        
        try:
            fax_file[(username, job_id)]
        except KeyError:
            result_code, data = ERROR_NO_DATA_AVAILABLE, ''
        else:
            data = fax_file[(username, job_id)].read(prop.max_message_len)
        
        if not data:
            result_code = ERROR_NO_DATA_AVAILABLE
            log.debug("Deleting data store for %s:%d" % (username, job_id))
            del fax_file[(username, job_id)]
        
        self.out_buffer = buildResultMessage('FaxGetDataResult', data, result_code)
        
    
    # EVENT
    def handle_event(self):
        gui_port, gui_host = None, None
        event_type = self.fields.get('event-type', 'event')
        event_code = self.fields.get('event-code', 0)
        device_uri = self.fields.get('device-uri', '').replace('hpfax:', 'hp:')
        log.debug("Device URI: %s" % device_uri)

        try:
            error_string_short = QueryString(str(event_code), 0)
        except Error:
            error_string_short, error_string_long = '', ''
        else:
            try:
                error_string_long = QueryString(str(event_code), 1)
            except Error:
                pass

        log.debug("Short/Long: %s/%s" % (error_string_short, error_string_long))

        job_id = self.fields.get('job-id', 0)

        try:
            username = self.fields['username']
        except KeyError:
            if job_id == 0:
                username = prop.username
            else:
                jobs = cups.getAllJobs()
                for j in jobs:
                    if j.id == job_id:
                        username = j.user
                        break
                else:
                    username = prop.username


        no_fwd = self.fields.get('no-fwd', False)
        log.debug("Username (jobid): %s (%d)" % (username, job_id))
        retry_timeout = self.fields.get('retry-timeout', 0)
        user_alerts = alerts.get(username, {})        

        dup_event = False
        if event_code <= EVENT_MAX_USER_EVENT:
            dup_event = self.createHistory(device_uri, event_code, job_id, username)

        pull = False
        if not no_fwd:
            for handler in socket_map:
                handler_obj = socket_map[handler]
                
                if handler_obj.send_events:
                    log.debug("Sending event to client: (%s, %s, %d)" % (handler_obj.username, handler_obj.typ, handler_obj._fileno))
                    pull = True

                    if handler_obj.typ == 'fax':
                        t = device_uri.replace('hp:', 'hpfax:')
                    else:
                        t = device_uri.replace('hpfax:', 'hp:')
                    
                    handler_obj.out_buffer = \
                        buildMessage('EventGUI', 
                            '%s\n%s\n' % (error_string_short, error_string_long),
                            {'job-id' : job_id,
                             'event-code' : event_code,
                             'event-type' : event_type,
                             'retry-timeout' : retry_timeout,
                             'device-uri' : t,
                            })

            if pull:
                loopback_trigger.pull_trigger()

            if event_code <= EVENT_MAX_USER_EVENT and \
                user_alerts.get('email-alerts', False) and \
                event_type == 'error' and \
                not dup_event:

                try:
                    subject = QueryString('email_alert_subject') + device_uri
                except Error:
                    subject = device_uri
                
                message = '\n'.join([device_uri, 
                                     time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()),
                                     error_string_short, 
                                     error_string_long,
                                     str(event_code)])
                                     
                self.sendEmail(username, subject, message, False)
                
                
    def sendEmail(self, username, subject, message, wait):
        msg = cStringIO.StringIO()
        result_code = ERROR_SUCCESS
        
        user_alerts = alerts.get(username, {}) 
        from_address = user_alerts.get('email-from-address', '')
        to_addresses = user_alerts.get('email-to-addresses', from_address)
        
        t = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        UUID = file("/proc/sys/kernel/random/uuid").readline().rstrip("\n")
        
        msg.write("Date: %s\n" % t)
        msg.write("From: <%s>\n" % from_address)
        msg.write("To: %s\n" % to_addresses)
        msg.write("Message-Id: <%s %s>\n" % (UUID, t))
        msg.write('Content-Type: text/plain\n')
        msg.write("Content-Transfer-Encoding: 7bit\n")
        msg.write('Mime-Version: 1.0\n')
        msg.write("Subject: %s\n" % subject)
        msg.write('\n')
        msg.write(message)
        #msg.write('\n')
        email_message = msg.getvalue()
        log.debug(repr(email_message))

        mt = MailThread(email_message, from_address)
        mt.start()
        
        if wait:
            mt.join() # wait for thread to finish
            result_code = mt.result
            
        return result_code


    def handle_probedevicesfiltered(self):
        payload, result_code = '', ERROR_SUCCESS
        num_devices, ret_devices = 0, {}

        buses = self.fields.get('bus', 'cups,usb,par').split(',')
        format = self.fields.get('format', 'default')

        for b in buses:
            bus = b.lower().strip()
            
            if bus == 'net':
                ttl = int(self.fields.get('ttl', 4))
                timeout = int(self.fields.get('timeout', 5))

                try:
                    detected_devices = slp.detectNetworkDevices(ttl, timeout)
                except Error:
                    log.error("An error occured during network probe.")
                else:
                    for ip in detected_devices:
                        hn = detected_devices[ip].get('hn', '?UNKNOWN?')
                        num_devices_on_jd = detected_devices[ip].get('num_devices', 0)
                        num_ports_on_jd = detected_devices[ip].get('num_ports', 1)

                        if num_devices_on_jd > 0:
                            for port in range(num_ports_on_jd):
                                dev = detected_devices[ip].get('device%d' % (port+1), '0')

                                if dev is not None and dev != '0':
                                    device_id = device.parseDeviceID(dev)
                                    model = device.normalizeModelName(device_id.get('MDL', '?UNKNOWN?'))

                                    if num_ports_on_jd == 1:
                                        device_uri = 'hp:/net/%s?ip=%s' % (model, ip)
                                    else:
                                        device_uri = 'hp:/net/%s?ip=%s&port=%d' % (model, ip, (port+1))

                                    device_filter = self.fields.get('filter', 'none')

                                    if device_filter in ('none', 'print'):
                                        include = True
                                    else:
                                        include = True

                                        try:

                                            fields = QueryModel(model)
                                        except Error:
                                            continue

                                        for f in device_filter.split(','):
                                            filter_type = int(fields.get('%s-type' % f.lower().strip(), 0))
                                            if filter_type == 0:
                                                include = False
                                                break

                                    if include:
                                        ret_devices[device_uri] = (model, model, hn)

            elif bus in ('usb', 'par'):
                log.debug(bus)
                try:
                    prop.hpiod_port = int(file(os.path.join(prop.run_dir, 'hpiod.port'), 'r').read())
                except:
                    prop.hpiod_port = 0
                
                log.debug("Connecting to hpiod (%s:%d)..." % (prop.hpiod_host, prop.hpiod_port))
                hpiod_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                hpiod_sock.connect((prop.hpiod_host, prop.hpiod_port))
            
                fields, data, result_code = \
                    xmitMessage(hpiod_sock, "ProbeDevices", None, {'bus' : bus,})
                
                hpiod_sock.close()

                if result_code == ERROR_SUCCESS:
                    for x in data.splitlines():
                        m = direct_pat.match(x)
                        
                        uri = m.group(1) or ''
                        mdl = m.group(2) or ''
                        desc = m.group(3) or ''
                        devid = m.group(4) or ''
                        
                        try:
                            back_end, is_hp, bus, model, serial, dev_file, host, port = \
                                device.parseDeviceURI(uri)
                        except Error:
                            continue
                        
                        if mdl and uri and is_hp:
                            device_filter = self.fields.get('filter', 'none')
                            include = True
                            
                            if device_filter not in ('none', 'print'):
                                try:
                                    fields = QueryModel(model)
                                except Error:
                                    continue
    
                                for f in device_filter.split(','):
                                    filter_type = int(fields.get('%s-type' % f.lower().strip(), 0))
                                    if filter_type == 0:
                                        include = False
                                        break
    
                            if include:
                                ret_devices[uri] = (mdl, desc, devid) # model w/ _'s, mdl w/o

            elif bus == 'cups':
                cups_printers = cups.getPrinters()
                x = len(cups_printers)

                for p in cups_printers:
                    device_uri = p.device_uri

                    if p.device_uri != '':
                        device_filter = self.fields.get('filter', 'none')

                        try:
                            back_end, is_hp, bs, model, serial, dev_file, host, port = \
                                device.parseDeviceURI(device_uri)
                        except Error:
                            log.warning("Inrecognized URI: %s" % device_uri)
                            continue

                        if not is_hp:
                            continue
                            
                        include = True
                        if device_filter not in ('none', 'print'):
                            try:
                                fields = QueryModel(model)
                            except Error:
                                continue

                            for f in device_filter.split(','):
                                filter_type = int(fields.get('%s-type' % f.lower().strip(), 0))
                                if filter_type == 0:
                                    include = False
                                    break

                        if include:
                            ret_devices[device_uri] = (model, model, '')


        for uri in ret_devices:
            num_devices += 1
            mdl, model, devid_or_hn = ret_devices[uri]
            
            if format == 'cups':
                payload = ''.join([payload, uri, ' ', utils.dquote(mdl), ' ', utils.dquote(model), ' ',utils.dquote(devid_or_hn), '\n'])
            else: # default
                payload = ''.join([payload, uri, ',', mdl, '\n'])
            

        self.out_buffer = buildResultMessage('ProbeDevicesFilteredResult', payload,
                                             result_code, {'num-devices' : num_devices})

    # EVENT
    def handle_exit(self):
        self.signal_exit = True

    def handle_messageerror(self):
        pass

    def writable(self):
        return not (not self.out_buffer and self.connected)


    def handle_close(self):
        log.debug("Closing channel (%d)" % self._fileno)
        self.connected = False
        self.close()


class MailThread(threading.Thread):
    def __init__(self, message, from_address):
        threading.Thread.__init__(self)
        self.message = message
        self.from_address = from_address
        self.result = ERROR_SUCCESS

    def run(self):
        log.debug("Starting Mail Thread...")
        sendmail = utils.which('sendmail')
        
        if sendmail:
            sendmail = os.path.join(sendmail, 'sendmail')
            sendmail += ' -t -r %s' % self.from_address
            
            log.debug(sendmail)
            std_out, std_in, std_err = popen2.popen3(sendmail) 
            log.debug(repr(self.message))
            std_in.write(self.message)
            std_in.close()
            
            r, w, e = select.select([std_err], [], [], 2.0)
            
            if r:
                err = std_err.read()
                if err:
                    log.error(repr(err))
                    self.result = ERROR_TEST_EMAIL_FAILED
            
        else:
            log.error("Mail send failed. sendmail not found.")
            self.result = ERROR_TEST_EMAIL_FAILED
            
        log.debug("Exiting mail thread")


def reInit():
    initStrings()


def handleSIGHUP(signo, frame):
    log.info("SIGHUP")
    reInit()


def exitAllGUIs():
    pass

    
USAGE = [(__doc__, "", "name", True),
         ("Usage: hpssd.py [OPTIONS]", "", "summary", True),
         utils.USAGE_OPTIONS,
         ("Do not daemonize:", "-x", "option", False),
         ("Port to listen on:", "-p<port> or --port=<port> (overrides value in /etc/hp/hplip.conf)", "option", False),
         utils.USAGE_LOGGING1, utils.USAGE_LOGGING2,
         ("Run in debug mode:", "-g (same as options: -ldebug -x)", "option", False),
         utils.USAGE_HELP,
        ]
        

def usage(typ='text'):
    if typ == 'text':
        utils.log_title(__title__, __version__)
        
    utils.format_text(USAGE, typ, __title__, 'hpssd.py', __version__)
    sys.exit(0)



def main(args):
    log.set_module('hpssd')

    prop.prog = sys.argv[0]
    prop.daemonize = True

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'l:xhp:g', 
            ['level=', 'help', 'help-man', 'help-rest', 'port='])

    except getopt.GetoptError:
        usage()

    if os.getenv("HPLIP_DEBUG"):
        log.set_level('debug')
    
    for o, a in opts:
        if o in ('-l', '--logging'):
            log_level = a.lower().strip()
            if not log.set_level(log_level):
                usage()
                
        elif o == '-g':
            log.set_level('debug')
            prop.daemonize = False

        elif o in ('-x',):
            prop.daemonize = False

        elif o in ('-h', '--help'):
            usage()
            
        elif o == '--help-rest':
            usage('rest')
            
        elif o == '--help-man':
            usage('man')
            
        elif o in ('-p', '--port'):
            try:
                prop.hpssd_cfg_port = int(a)
            except ValueError:
                log.error('Port must be a numeric value')
                usage()


    utils.log_title(__title__, __version__)

    prop.history_size = 32

    # Lock pidfile before we muck around with system state
    # Patch by Henrique M. Holschuh <hmh@debian.org>
    utils.get_pidfile_lock(os.path.join(prop.run_dir, 'hpssd.pid'))

    # Spawn child right away so that boot up sequence
    # is as fast as possible
    if prop.daemonize:
        utils.daemonize()


    # configure the various data stores
    gettext.install('hplip')
    reInit()

    # hpssd server dispatcher object
    try:
        server = hpssd_server(prop.hpssd_host, prop.hpssd_cfg_port)
    except Error, e:
        log.error("Server exited with error: %s" % e.msg)
        sys.exit(1)

    global loopback_trigger
    try:
        loopback_trigger = trigger()
    except Error, e:
        log.error("Server exited with error: %s" % e.msg)
        sys.exit(1)

    os.umask(0133)
    file(os.path.join(prop.run_dir, 'hpssd.port'), 'w').write('%d\n' % prop.hpssd_port)
    os.umask (0077)
    log.debug('port=%d' % prop.hpssd_port)
    log.info("Listening on %s:%d" % (prop.hpssd_host, prop.hpssd_port))

    signal.signal(signal.SIGHUP, handleSIGHUP)

    try:
        log.debug("Starting async loop...")
        try:
            loop(timeout=0.5)
        except KeyboardInterrupt:
            log.warn("Ctrl-C hit, exiting...")
        except Exception:
            log.exception()

        log.debug("Cleaning up...")
    finally:
        os.remove(os.path.join(prop.run_dir, 'hpssd.pid'))
        os.remove(os.path.join(prop.run_dir, 'hpssd.port'))
        server.close()
        return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


