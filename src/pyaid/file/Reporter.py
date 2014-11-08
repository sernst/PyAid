# Reporter.py
# (C)2012-2013
# Scott Ernst

from __future__ import print_function
from __future__ import absolute_import

import sys
import os
import datetime
import math
import random

from lockfile import FileLock
from pyaid.dict.DictUtils import DictUtils

from pyaid.json.JSON import JSON
from pyaid.radix.Base64 import Base64
from pyaid.string.StringUtils import StringUtils
from pyaid.time.TimeUtils import TimeUtils

#___________________________________________________________________________________________________ Reporter
class Reporter(object):
    """A class for reporting JSON-encoded string data to the operations/reports directory."""

#===================================================================================================
#                                                                                       C L A S S

    _REPORT_PATH       = None
    _ZERO_TIME         = 0
    _ROTATION_INTERVAL = 30

#___________________________________________________________________________________________________ __init__
    def __init__(self, name=None, **kwargs):
        """Initializes settings."""
        self._buffer     = []
        self._meta       = dict()
        self._fileCount  = kwargs.get('fileCount', 10)
        self._zeroTime   = kwargs.get('zeroTime', self._ZERO_TIME)
        self._reportPath = kwargs.get('path', self._REPORT_PATH)
        self._time       = datetime.datetime.utcnow()
        self._timeCode   = Reporter.getTimecodeFromDatetime(self._time, self._zeroTime)

        if StringUtils.isStringType(name) and len(name) > 0:
            self._name = name
        elif hasattr(name, '__class__'):
            try:
                self._name = name.__class__.__name__
            except Exception:
                self._name = 'UnknownObject'
        elif hasattr(name, '__name__'):
            try:
                self._name = name.__name__
            except Exception:
                self._name = 'UnknownClass'
        else:
            self._name = 'General'

        self._meta['_vw'] = self._name

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getReportFolder
    def getReportFolder(self):
        reports = self._reportPath
        if not os.path.exists(reports):
            os.makedirs(reports)
        return reports

#___________________________________________________________________________________________________ getPrefix
    def getPrefix(self):
        return Base64.to64(TimeUtils.getNowSeconds() - self._zeroTime)

#___________________________________________________________________________________________________ clear
    def clear(self):
        """Clears the log entries currently stored in the buffer."""
        self._buffer = []

#___________________________________________________________________________________________________ add
    def add(self, data):
        """Adds a report to the buffer."""
        self._buffer.append({'prefix':self.getPrefix(), 'data':data})

#___________________________________________________________________________________________________ flush
    def flush(self):
        if not self._buffer:
            return

        if sys.platform.startswith('win'):
            return

        items = []
        for b in self._buffer:
            try:
                d    = DictUtils.merge(self._meta, b['data'])
                item = b['prefix'] + u' ' + JSON.asString(d)
            except Exception as err:
                item = '>> EXCEPTION: JSON ENCODING FAILED >> ' + str(err).replace('\n', '\t')

            try:
                item = item.encode('utf8', 'ignore')
            except Exception as err:
                item = '>> EXCEPTION: UNICODE DECODING FAILED >> ' + str(err).replace('\n', '\t')

            items.append(item)

        count   = self._fileCount
        offset  = random.randint(0, count - 1)
        success = False
        path    = self.getReportFolder() + self._timeCode + '/'
        if not os.path.exists(path):
            os.makedirs(path)

        for i in range(count):
            index = (i + offset) % count
            p     = path + str(index) + '.report'
            lock  = FileLock(p)
            if lock.i_am_locking() and i < count - 1:
                continue

            try:
                lock.acquire()
            except Exception:
                continue

            try:
                out = StringUtils.toUnicode(u'\n'.join(items) + u'\n')
                f   = open(p, 'a+')
                f.write(out.encode('utf8'))
                f.close()
                success = True
            except Exception as err:
                print("REPORTER ERROR: Unable to write report file.")
                print(err)

            lock.release()
            if success:
                break

        self.clear()
        return success

#___________________________________________________________________________________________________ __call__
    def __call__(self, data):
        self.add(data)

#___________________________________________________________________________________________________ __del__
    def __del__(self):
        """ Flush the buffer if not empty."""
        self.flush()

#___________________________________________________________________________________________________ getSecondsFromTimecode
    @classmethod
    def getSecondsFromTimecode(cls, timecode, zeroTime =None):
        if zeroTime is None:
            zeroTime = cls._ZERO_TIME

        if timecode is None:
            return zeroTime

        return 60*(Base64.from64(timecode)) + zeroTime

#___________________________________________________________________________________________________ getTimecodeFromDatetime
    @classmethod
    def getTimecodeFromDatetime(cls, time =None, zeroTime =None, rotationInterval =None):
        if zeroTime is None:
            zeroTime = cls._ZERO_TIME

        if rotationInterval is None:
            rotationInterval = cls._ROTATION_INTERVAL

        if time is None:
            time = datetime.datetime.utcnow()

        t = float(TimeUtils.datetimeToSeconds(time) - zeroTime)/60.0
        t = float(rotationInterval)*math.floor(t/float(rotationInterval))
        return Base64.to64(int(t))
