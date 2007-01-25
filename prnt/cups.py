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

                if source not in ('application/octet-stream', 'application/vnd.cups-postscript'):
                    allowable_mime_types.append(source)

    # Add some well-known MIME types that may not appear in the .convs files
    allowable_mime_types.append("image/x-bmp")
    allowable_mime_types.append("text/cpp")

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


def levenshtein_distance(a,b):
    """
    Calculates the Levenshtein distance between a and b.
    Written by Magnus Lie Hetland.
    """
    n, m = len(a), len(b)
    if n > m:
        a,b = b,a
        n,m = m,n

    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*m
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]

number_pat = re.compile(r""".*?(\d+)""", re.IGNORECASE)

def getPPDFile(stripped_model, ppds):
    log.debug("1st stage edit distance match")
    mins = []
    eds = {}
    min_edit_distance = sys.maxint

    for f in ppds:
        t = os.path.basename(f).lower().replace('hp-', '').replace('-hpijs', '').\
            replace('.gz', '').replace('.ppd', '').replace('hp_', '').replace('_series', '').lower()

        eds[f] = levenshtein_distance(stripped_model, t)
        #log.debug("dist('%s', '%s') = %d" % (stripped_model, t, eds[f]))
        min_edit_distance = min(min_edit_distance, eds[f])

    log.debug("Min. dist = %d" % min_edit_distance)

    for f in ppds:
        if eds[f] == min_edit_distance:
            for m in mins:
                if os.path.basename(m) == os.path.basename(f):
                    break # File already in list possibly with different path (Ubuntu, etc)
            else:
                mins.append(f)

    log.debug(mins)

    if len(mins) > 1: # try pattern matching the model number 
        log.debug("2nd stage matching with model number")
        log.debug(mins)
        try:
            model_number = number_pat.match(stripped_model).group(1)
            model_number = int(model_number)
        except AttributeError:
            pass
        except ValueError:
            pass
        else:
            log.debug("model_number=%d" % model_number)
            matches = []
            for x in range(3): # 1, 10, 100
                factor = 10**x
                log.debug("Factor = %d" % factor)
                adj_model_number = int(model_number/factor)*factor
                number_matching, match = 0, ''

                for m in mins:
                    try:
                        mins_model_number = number_pat.match(os.path.basename(m)).group(1)
                        mins_model_number = int(mins_model_number)
                        log.debug("mins_model_number= %d" % mins_model_number)
                    except AttributeError:
                        continue
                    except ValueError:
                        continue

                    mins_adj_model_number = int(mins_model_number/factor)*factor
                    log.debug("mins_adj_model_number=%d" % mins_adj_model_number)
                    log.debug("adj_model_number=%d" % adj_model_number)

                    if mins_adj_model_number == adj_model_number: 
                        log.debug("match")
                        number_matching += 1
                        matches.append(m)
                        log.debug(matches)

                    log.debug("***")

                if len(matches):
                    mins = matches[:]
                    break

    return mins

