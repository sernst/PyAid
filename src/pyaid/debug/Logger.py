# Logger.py
# (C)2010-2013
# Scott Ernst and Thomas Gilray

import sys
import os
import datetime
import traceback
import unicodedata

# WHEN AVAILABLE: import pytz

from pyaid.ArgsUtils import ArgsUtils
from pyaid.file.FileLock import FileLock
from pyaid.file.FileUtils import FileUtils
from pyaid.string.StringUtils import StringUtils

#___________________________________________________________________________________________________ Logger
class Logger(object):
    """A class for logging information in and operations/logs directory."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, name=None, **kwargs):
        """Initializes settings."""
        self.headerless  = kwargs.get('headerless', False)
        self._time       = self._getTime()
        self._timeCode   = self._time.strftime('%y-%U')
        self._timestamp  = self._time.strftime('%Y|%m|%d|%H|%M|%S')

        self._logPath    = kwargs.get('logFolder', None)
        if self._logPath:
            self._logPath = FileUtils.cleanupPath(self._logPath)

        self._htmlEscape    = kwargs.get('htmlEscape', False)
        self._storageBuffer = [] if kwargs.get('useStorageBuffer', False) else None

        writeCallbacks = kwargs.get('writeCallbacks', None)
        if writeCallbacks:
            cbs = writeCallbacks
            self._writeCallbacks = cbs if isinstance(cbs, list) else [cbs]
        else:
            self._writeCallbacks = []

        printCallbacks = kwargs.get('printCallbacks', None)
        if printCallbacks:
            cbs = printCallbacks
            self._printCallbacks = cbs if isinstance(cbs, list) else [cbs]
        else:
            self._printCallbacks = []

        self._locationPrefix = kwargs.get('locationPrefix', False)
        self._traceLogs      = kwargs.get('printOut', False)
        self._buffer         = []
        self._hasError       = False

        if isinstance(name, basestring) and len(name) > 0:
            self._name = name
        elif hasattr(name, '__class__'):
            try:
                self._name = name.__class__.__name__
            except Exception, err:
                self._name = 'UnknownObject'
        elif hasattr(name, '__name__'):
            try:
                self._name = name.__name__
            except Exception, err:
                self._name = 'UnknownClass'
        else:
            self._name = 'General'

        logFolder = self.getLogFolder()
        if logFolder:
            self._logFile = FileUtils.createPath(
                logFolder, self._name + '_' + self._timeCode + '.log')
        else:
            self._logFile = None

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: loggingPath
    @property
    def loggingPath(self):
        return self._logPath
    @loggingPath.setter
    def loggingPath(self, value):
        self._logPath = value

#___________________________________________________________________________________________________ GS: storageBuffer
    @property
    def storageBuffer(self):
        return self._storageBuffer

#___________________________________________________________________________________________________ GS: hasError
    @property
    def hasError(self):
        return self._hasError

#___________________________________________________________________________________________________ GS: trace
    @property
    def trace(self):
        return self._traceLogs
    @trace.setter
    def trace(self, value):
        self._traceLogs = bool(value)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ addPrintCallback
    def addPrintCallback(self, callback):
        if callback not in self._printCallbacks:
            self._printCallbacks.append(callback)
        return True

#___________________________________________________________________________________________________ removePrintCallback
    def removePrintCallback(self, callback):
        if callback not in self._printCallbacks:
            return False

        self._printCallbacks.remove(callback)
        return True

#___________________________________________________________________________________________________ addWriteCallback
    def addWriteCallback(self, callback):
        if callback not in self._writeCallbacks:
            self._writeCallbacks.append(callback)
        return True

#___________________________________________________________________________________________________ removeWriteCallback
    def removeWriteCallback(self, callback):
        if callback not in self._writeCallbacks:
            return False

        self._writeCallbacks.remove(callback)
        return True

#___________________________________________________________________________________________________ getLog
    def getLog(self):
        return ''.join(self._buffer)

#___________________________________________________________________________________________________ getLogFolder
    def getLogFolder(self):
        if not self._logPath:
            return None

        logs = self._logPath
        if not os.path.exists(logs):
            os.makedirs(logs)
        return logs

#___________________________________________________________________________________________________ getPrefix
    def getPrefix(self, *args, **kwargs):
        if self._locationPrefix:
            item = self.getStackData()[-1]
            loc  = u' -> %s #%s]' % (item['file'], unicode(item['line']))
        else:
            loc = u']'

        return unicode(self._getTime().strftime(u'[%a %H:%M <%S.%f>') + loc)

#___________________________________________________________________________________________________ clear
    def clear(self, storage =False):
        """Clears the log entries currently stored in the buffer."""
        self._buffer    = []
        self._hasError  = False
        if storage and self._storageBuffer is not None:
            self._storageBuffer = []

#___________________________________________________________________________________________________ clearLogFile
    def clearLogFile(self):
        if self._logFile and os.path.exists(self._logFile):
            os.remove(self._logFile)

#___________________________________________________________________________________________________ add
    def add(self, s, traceStack =False, shaveStackTrace =0, request =None, htmlEscape =False):
        """Prints s to standard output and a log file."""
        s = Logger._formatAsString(s)
        if traceStack:
            s += '\nStack Trace:\n' + Logger.getFormattedStackTrace(shaveStackTrace)

        if self._htmlEscape or htmlEscape:
            s = StringUtils.htmlEscape(s)

        if self._traceLogs:
            out = self._asASCII(s)
            print out
            for cb in self._printCallbacks:
                try:
                    cb(self, out)
                except Exception, err:
                    pass

        if len(self._name) < 1:
            return

        tp = '' if self.headerless else self.getPrefix() + ':\n\t'
        s  = s.replace('\n', '\n\t')
        try:
            logValue = (tp + s + "\n").encode('utf-8')
        except Exception, err:
            try:
                logValue = (tp + str(s) + "\n").encode('utf-8')
            except Exception, err:
                logValue = (tp + "FAILED TO LOG VALUE").encode('utf-8')

        self._buffer.append({'log':logValue, 'stack':traceStack})
        if self._storageBuffer is not None:
            self._storageBuffer.append({'log':logValue, 'stack':traceStack})

#___________________________________________________________________________________________________ addError
    def addError(self, s, err, request =None, htmlEscape =False):
        self._hasError = True

        try:
            errorType = unicode(sys.exc_info()[0])
        except Exception, err:
            try:
                errorType = str(sys.exc_info()[0])
            except Exception, err:
                errorType = '[[UNABLE TO PARSE]]'

        try:
            errorValue = unicode(sys.exc_info()[1])
        except Exception, err:
            try:
                errorValue = str(sys.exc_info()[1])
            except Exception, err:
                errorValue = '[[UNABLE TO PARSE]]'

        try:
            error = unicode(err)
        except Exception, err:
            try:
                error = str(err)
            except Exception, err:
                error = '[[UNABLE TO PARSE]]'

        try:
            es = (Logger._formatAsString(s) + "\n\tType: %s\n\tValue: %s\nError: %s\n") \
               % (errorType, errorValue, error)
        except Exception, err:
            try:
                es = Logger._formatAsString(s) + "\n\t[[ERROR ATTRIBUTE PARSING FAILURE]]"
            except Exception, err:
                es = 'FAILED TO PARSE EXCEPTION'

        self.add(es, True, htmlEscape=htmlEscape)

#___________________________________________________________________________________________________ __call__
    def __call__(self, s ='', *args, **kwargs):

        request = ArgsUtils.get('request', kwargs)

        # If the call is an error, write the error
        err = ArgsUtils.get('err', args=args, index=1)
        if err and isinstance(err, Exception):
            if self._buffer:
                self.addError(s, err, request=request)
            else:
                self.writeError(s, err, request=request)

            return

        # Handle the non-error case
        traceStack      = ArgsUtils.get('traceStack', False, kwargs, args, 1)
        shaveStackTrace = ArgsUtils.get('shaveStackTrace', 0, kwargs, args, 2)
        if self._buffer:
            self.add(s, traceStack, shaveStackTrace, request=request)
        else:
            self.write(s, traceStack, shaveStackTrace, request=request)

#___________________________________________________________________________________________________ write
    def write(self, s, traceStack =False, shaveStackTrace =0, request =None, htmlEscape =False):
        """Adds the log item and flushes the buffer to the log file."""
        self.add(s, traceStack, shaveStackTrace, htmlEscape=htmlEscape)
        self.flush()

#___________________________________________________________________________________________________ writeError
    def writeError(self, s, err, request =None, htmlEscape =False):
        self.addError(s, err, request=request, htmlEscape=htmlEscape)
        self.flush()

#___________________________________________________________________________________________________ flush
    def flush(self, **kwargs):
        if not self._buffer:
            return

        items = []
        for logItem in self._buffer:
            item = logItem['log']
            try:
                item = item.encode('utf8', 'ignore')
            except Exception, err:
                pass
            items.append(item)

        for cb in self._writeCallbacks:
            try:
                cb(self, items)
            except Exception, err:
                pass

        if sys.platform.startswith('win') and not self._logPath:
            self.clear()
            return
        elif self._logFile:
            try:
                exists = os.path.exists(self._logFile)
                with FileLock(self._logFile, 'a+') as lock:
                    lock.file.write('\n'.join(items))
                    lock.release()

                if not exists:
                    os.system('chmod 775 ' + self._logFile)

            except Exception, err:
                print "LOGGER ERROR: Unable to write log file."
                print err

        self.clear()

#___________________________________________________________________________________________________ getFormattedStackTrace
    @staticmethod
    def getFormattedStackTrace(skipStackLevels =0, maxLevels =0):
        # Get the exception stack trace if it exists, otherwise extract the generic stack trace
        # instead.
        stack = Logger.getStackData()
        stop  = len(stack) - skipStackLevels
        start = max(0, stop - maxLevels) if maxLevels > 0 else 0
        s     = u''
        index = start
        for item in stack[start:stop]:
            index    += 1
            if item['internal']:
                s += (u'\n\t[%s]: %s.%s [#%s]'
                      + '\n\t     code: %s') \
                  % (unicode(index), item['file'], item['function'], unicode(item['line']),
                     item['code'][:100])
            else:
                s += u'\n\t[%s] EXT: %s {line: %s}' % (
                    unicode(index), item['file'], unicode(item['line']))

        return s

#___________________________________________________________________________________________________ getStackData
    @staticmethod
    def getStackData():
        res   = []
        for item in Logger.getRawStack():
            s             = {}
            path          = unicode(item[0])
            s['path']     = path
            s['internal'] = True #path.lower().find('vizme') != -1
            s['dir']      = unicode(os.path.dirname(path))
            s['file']     = unicode(os.path.basename(path).replace('.py',''))

            s['line']     = item[1]
            s['function'] = unicode(item[2])
            s['code']     = unicode(item[3])
            res.append(s)

        return res

#___________________________________________________________________________________________________ getFormattedStackTrace
    @staticmethod
    def getRawStack():
        exceptStack = sys.exc_info()[2]
        if exceptStack is None:
            rawStack = traceback.extract_stack()
        else:
            rawStack = traceback.extract_tb(exceptStack)

        stack    = []
        for item in rawStack:
            if item[0].find('Logger') != -1:
                continue
            stack.append(item)

        return stack

#___________________________________________________________________________________________________ prettyPrint
    @staticmethod
    def prettyPrint(target, indentLevel =1):
        indent = u'\n' + (indentLevel*u'\t')
        s = u'\n'
        if isinstance(target, list):
            index = 0
            for t in target:
                try:
                    v = unicode(t)
                except Exception, err:
                    v = u'<UNPRINTABLE>'
                s += u'%s[%s]: %s' % (indent, index, v)
            return s

        if isinstance(target, dict):
            for n,v in target.iteritems():
                try:
                    v = unicode(v)
                except Exception, err:
                    v = u'<UNPRINTABLE>'
                s += u'%s%s: %s' % (indent, n, v)
            return s

        items = dir(target)
        for n in items:
            v = getattr(target, n)
            try:
                v = unicode(v)
            except Exception, err:
                v = u'<UNPRINTABLE>'
            s += u'%s%s: %s' % (indent, n, v)
        return s

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ __del__
    def __del__(self):
        """ Flush the buffer if not empty."""
        self.flush()

#___________________________________________________________________________________________________ _getTime
    def _getTime(self):
        try:
            import pytz
            dt = datetime.datetime.now(tz=pytz.utc)
            return dt.astimezone(tz=pytz.timezone('US/Pacific'))
        except Exception, err:
            return datetime.datetime.utcnow()

#___________________________________________________________________________________________________ _asASCII
    @staticmethod
    def _asASCII(string):
        if isinstance(string, unicode):
            try:
                return string.encode('utf8', 'ignore')
            except Exception, err:
                try:
                    return unicodedata.normalize('NFKD', string).encode('ascii', 'ignore')
                except Exception, err:
                    return '[[UNABLE TO DISPLAY LOG ENTRY IN ASCII CHARS]]'
        else:
            return string

#___________________________________________________________________________________________________ _formatAsString
    @staticmethod
    def _formatAsString(src, indentLevel =0):
        indents = u'    '*indentLevel
        if isinstance(src, list) or isinstance(src, tuple):
            out      = [indents + unicode(src[0]) + (u'' if src[0].endswith(u':') else u':')]
            indents  = indents + u'    '
            lines    = []
            maxIndex = 0

            for item in src[1:]:
                if not isinstance(item, basestring):
                    item = unicode(item)
                elif isinstance(item, str):
                    item = item.decode('utf-8')

                index    = item.find(':')
                index    = index if index != -1 and index < 12 else 0
                maxIndex = max(index, maxIndex)
                lines.append([index, item])

            for item in lines:
                if item[0] > 0:
                    out.append(indents + (u' '*max(0, maxIndex - item[0])) + item[1])
                else:
                    out.append(indents + item[1])
            return u'\n'.join(out)

        else:
            if not isinstance(src, basestring):
                src = unicode(src)
            elif isinstance(src, str):
                src = src.decode('utf-8')
            return indents + src
