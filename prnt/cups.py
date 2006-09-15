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

# Std Lib
import os, os.path, gzip, re, time, urllib, tempfile, glob

# Local
from base.g import *

# Handle case where cups.py (via device.py) is loaded 
# and cupsext doesn't exist yet. This happens in the 
# installer...
try:
    import cupsext
except ImportError:
    pass

# PPD parsing patterns
mfg_pat = re.compile(r'\*\s*Manufacturer:\s*\".*?(.*?)\"', re.IGNORECASE)
model_pat = re.compile(r'\*\s*Product:\s*\"\(.*?(.*?)\)\"', re.IGNORECASE)

IPP_PRINTER_STATE_IDLE = 3
IPP_PRINTER_STATE_PROCESSING = 4
IPP_PRINTER_STATE_STOPPED = 5

def restartCUPS(): # must be root. How do you check for this?
    os.system('killall -HUP cupsd')

def getPPDPath(addtional_paths=[]):
    search_paths = [prop.ppd_search_path.split(';')] + addtional_paths
    for path in search_paths:
        ppd_path = os.path.join(path, 'cups/model')
        if os.path.exists(ppd_path):
            return ppd_path


def collectPPDs(ppd_path):
    from base import utils
    ppds = {} # { <model> : <PPD file> , ... }

    for f in utils.walkFiles(ppd_path, recurse=True, abs_paths=True,
                              return_folders=False , pattern=prop.ppd_search_pattern):

        if f.endswith('.gz'):
            g = gzip.open(f, 'r')
        else:
            g = open(f, 'r')

        try:
            d = g.read(4096)
        except IOError:
            g.close()
            continue
        try:
            mfg = mfg_pat.search(d).group(1).lower()
        except ValueError:
            g.close()
            continue

        if mfg != 'hp':
            continue

        try:
            model = model_pat.search(d).group(1).replace(' ', '_')
        except ValueError:
            g.close()
            continue

        ppds[model] = f

        g.close()

    return ppds


def downloadPPD(lporg_model_name, driver='hpijs', url=prop.ppd_download_url):
    # model name must match model name on lp.org
    u = urllib.urlopen(url, urllib.urlencode({'driver' : driver,
                                              'printer' : urllib.quote(lporg_model_name),
                                              'show' : '0'}))

    ppd_file = os.path.join(tempfile.gettempdir(), lporg_model_name + prop.ppd_file_suffix)
    f = file(ppd_file, 'w')
    f.write(u.read())
    f.close()

    return ppd_file


def getAllowableMIMETypes():    
    # Scan all /etc/cups/*.convs files for allowable file formats
    files = glob.glob("/etc/cups/*.convs")
    
    allowable_mime_types = []
    
    for f in files:
        #log.debug( "Capturing allowable MIME types from: %s" % f )
        conv_file = file(f, 'r')
    
        for line in conv_file:
            if not line.startswith("#") and len(line) > 1:
                try:
                    source, dest, cost, prog =  line.split()
                except ValueError:
                    continue
    
                allowable_mime_types.append(source)
            
    return allowable_mime_types


# cupsext wrapper

def getDefault():
    return cupsext.getDefault()

def openPPD(printer):
    return cupsext.openPPD(printer)

def closePPD():
    return cupsext.closePPD()
    
def getPPD(printer):
    return cupsext.getPPD(printer)

def getPPDOption(option):
    return cupsext.getPPDOption(option)

def getPPDPageSize():
    return cupsext.getPPDPageSize()

def getPrinters():
    return cupsext.getPrinters()

def getJobs(my_job=0, completed=0):
    return cupsext.getJobs(my_job, completed)

def getAllJobs(my_job=0):
    return cupsext.getJobs(my_job, 0) + cupsext.getJobs(my_job, 1)

def getVersion():
    return cupsext.getVersion()
    
def getVersionTuple():
    return cupsext.getVersionTuple()

def getServer():
    return cupsext.getServer()

def cancelJob(jobid, dest=None):
    if dest is not None:
        return cupsext.cancelJob(dest, jobid)
    else:
        jobs = cupsext.getJobs(0, 0)
        for j in jobs:
            if j.id == jobid:
                return cupsext.cancelJob(j.dest, jobid)

    return False
    
def resetOptions():
    return cupsext.resetOptions()
    
def addOption(option):
    return cupsext.addOption(option)
    
def printFile(printer, filename, title):
    if os.path.exists(filename):
        return cupsext.printFileWithOptions(printer, filename, title)
    else:
        return -1
        
def addPrinter(printer_name, device_uri, location, ppd_file, info):
    return cupsext.addPrinter(printer_name, device_uri, location, ppd_file, info)
    
def delPrinter(printer_name):
    return cupsext.delPrinter(printer_name)
        
