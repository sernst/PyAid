# Logger.py
# (C)2010-2014
# Scott Ernst and Thomas Gilray

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
import os
import datetime
import traceback
import unicodedata

# WHEN AVAILABLE: import pytz

from pyaid.ArgsUtils import ArgsUtils
from pyaid.OsUtils import OsUtils
from pyaid.file.FileLock import FileLock
from pyaid.file.FileUtils import FileUtils
from pyaid.string.StringUtils import StringUtils

#___________________________________________________________________________________________________ Logger
class Logger(object):
    """A class for logging information in and operations/logs directory."""

#===================================================================================================
#                                                                                       C L A S S

    PACIFIC_TIMEZONE = 'US/Pacific'

#___________________________________________________________________________________________________ __init__
    def __init__(self, name=None, **kwargs):
        """Initializes settings."""
        self.timezone            = kwargs.get('timezone', None)
        self.headerless          = kwargs.get('headerless', False)
        self.logFileExtension    = kwargs.get('extension', 'log').lstrip('.')
        self.timestampFileSuffix = kwargs.get('timestampFileSuffix', True)
        self.removeIfExists      = kwargs.get('removeIfExists', False)

        self._time              = self.getTime()
        self._timeCode          = self._time.strftime('%y-%U')
        self._timestamp         = self._time.strftime('%Y|%m|%d|%H|%M|%S')
        self._htmlEscape        = kwargs.get('htmlEscape', False)
        self._storageBuffer     = [] if kwargs.get('useStorageBuffer', False) else None
        self._locationPrefix    = kwargs.get('locationPrefix', False)
        self._traceLogs         = kwargs.get('printOut', False)
        self._buffer            = []
        self._hasError          = False
        self._logPath           = None
        self._logFile           = None

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

        self._name = self.createLogName(name)
        self.loggingPath = kwargs.get('logFolder', None)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: logFilePath
    @property
    def logFilePath(self):
        return self._logFile

#___________________________________________________________________________________________________ GS: loggingPath
    @property
    def loggingPath(self):
        return self._logPath
    @loggingPath.setter
    def loggingPath(self, value):
        self._logPath = FileUtils.cleanupPath(value)

        logFolder = self.getLogFolder()
        if logFolder:
            name = self._name
            extension = self.logFileExtension
            if self.timestampFileSuffix:
                name += '_' + self._timeCode
            self._logFile = FileUtils.createPath(logFolder, name + '.' + extension)
            if self.removeIfExists:
                self.resetLogFile()
        else:
            self._logFile = None

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

#___________________________________________________________________________________________________ resetLogFile
    def resetLogFile(self):
        if self._logFile and os.path.exists(self._logFile):
            try:
                os.remove(StringUtils.toUnicode(self._logFile))
            except Exception:
                pass

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
            loc  = ' -> %s #%s]' % (item['file'], StringUtils.toUnicode(item['line']))
        else:
            loc = ']'

        return StringUtils.toUnicode(
            self.getTime(self.timezone).strftime('[%a %H:%M <%S.%f>') + loc)

#___________________________________________________________________________________________________ clear
    def clear(self, storage =False):
        """Clears the log entries currently stored in the buffer."""
        self._buffer    = []
        self._hasError  = False
        if storage and self._storageBuffer is not None:
            self._storageBuffer = []

#___________________________________________________________________________________________________ clearLogFile
    def clearLogFile(self):
        if not self._logFile or not os.path.exists(self._logFile):
            os.remove(StringUtils.toUnicode(self._logFile))

#___________________________________________________________________________________________________ add
    def add(self, s, traceStack =False, shaveStackTrace =0, htmlEscape =None, **kwargs):
        """Prints s to standard output and a log file."""

        out = self.createLogMessage(
            logValue=s,
            traceStack=traceStack,
            shaveStackTrace=shaveStackTrace,
            htmlEscape=self._htmlEscape if htmlEscape is None else htmlEscape,
            prefix=self.getPrefix() if not self.headerless else None, **kwargs)

        if self._traceLogs:
            self.traceLogMessage(out, self._printCallbacks, self)

        self._buffer.append(out)
        if self._storageBuffer is not None:
            self._storageBuffer.append(out)
        return out['log']

#___________________________________________________________________________________________________ echo
    def echo(self, s, traceStack =False, shaveStackTrace =0, htmlEscape =None, **kwargs):
        out = self.createLogMessage(
            s, traceStack, shaveStackTrace,
            self._htmlEscape if htmlEscape is None else htmlEscape,
            prefix=self.getPrefix() if not self.headerless else None, **kwargs)

        if self._traceLogs:
            self.traceLogMessage(out, self._printCallbacks, self)
        return out['log'] + '\n' + out['stack']

#___________________________________________________________________________________________________ echoError
    def echoError(self, s, err, htmlEscape =False, **kwargs):
        ArgsUtils.addIfMissing('traceStack', True, kwargs)
        return self.echo(self.createErrorMessage(s, err), htmlEscape=htmlEscape, **kwargs)

#___________________________________________________________________________________________________ addError
    def addError(self, s, err, htmlEscape =False, **kwargs):
        self._hasError = True
        ArgsUtils.addIfMissing('traceStack', True, kwargs)
        return self.add(self.createErrorMessage(s, err), htmlEscape=htmlEscape, **kwargs)

#___________________________________________________________________________________________________ write
    def write(self, s, traceStack =False, shaveStackTrace =0, htmlEscape =False, **kwargs):
        """Adds the log item and flushes the buffer to the log file."""
        result = self.add(s, traceStack, shaveStackTrace, htmlEscape=htmlEscape, **kwargs)
        self.flush()
        return result

#___________________________________________________________________________________________________ writeError
    def writeError(self, s, err, htmlEscape =False, **kwargs):
        result = self.addError(s, err, htmlEscape=htmlEscape)
        self.flush()
        return result

#___________________________________________________________________________________________________ flush
    def flush(self, **kwargs):
        if not self._buffer:
            return

        items = []
        for logItem in self._buffer:
            item = self.logMessageToString(logMessage=logItem) + '\n'
            item = StringUtils.toStr2(item)
            items.append(item)

        for cb in self._writeCallbacks:
            try:
                cb(self, items)
            except Exception:
                pass

        if not self._logPath:
            self.clear()
            return

        elif self._logFile:
            try:
                out = StringUtils.toStr2('\n').join(items)
                exists = os.path.exists(self._logFile)
                with FileLock(self._logFile, 'a') as lock:
                    lock.file.write(out)
                    lock.release()

                try:
                    if not exists and not OsUtils.isWindows():
                        os.system('chmod 775 %s' % self._logFile)
                except Exception:
                    pass

            except Exception as err:
                print("LOGGER ERROR: Unable to write log file.")
                print(err)

        self.clear()

#___________________________________________________________________________________________________ createLogName
    @classmethod
    def createLogName(cls, name):
        if StringUtils.isStringType(name) and len(name) > 0:
            return name
        elif hasattr(name, '__class__'):
            try:
                return name.__class__.__name__
            except Exception:
                return 'UnknownObject'
        elif hasattr(name, '__name__'):
            try:
                return name.__name__
            except Exception:
                return 'UnknownClass'
        else:
            return 'General'

#___________________________________________________________________________________________________ getFormattedStackTrace
    @classmethod
    def getFormattedStackTrace(cls, skipStackLevels =0, maxLevels =0, stackSource =None):
        """ Get the exception stack trace if it exists, otherwise extract the generic stack trace
            instead. """

        stack = Logger.getStackData(stackSource)
        stop  = len(stack) - skipStackLevels
        start = max(0, stop - maxLevels) if maxLevels > 0 else 0
        s     = ''
        index = start
        for item in stack[start:stop]:
            index    += 1
            if item['internal']:
                s +=('\n    [%s]: %s.%s [#%s]\n         code: %s' % (
                    StringUtils.toUnicode(index), item['file'], item['function'],
                    StringUtils.toUnicode(item['line']),
                    item['code'][:100] ))
            else:
                s += '\n    [%s] EXT: %s {line: %s}' % (
                    StringUtils.toUnicode(index), item['file'],
                    StringUtils.toUnicode(item['line']))

        return s

#___________________________________________________________________________________________________ getStackData
    @staticmethod
    def getStackData(stackSource =None):
        res = []
        if not stackSource:
            stackSource = Logger.getRawStack()

        for item in stackSource:
            path = StringUtils.toUnicode(item[0])
            res.append(dict(
                path=path,
                internal=True,
                dir=StringUtils.toUnicode(os.path.dirname(path)),
                file=StringUtils.toUnicode(os.path.basename(path).replace('.py','')),
                line=item[1],
                function=StringUtils.toUnicode(item[2]),
                code=StringUtils.toUnicode(item[3]) ))

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
        indent = '\n' + (indentLevel*'    ')
        s = '\n'
        if isinstance(target, list):
            index = 0
            for t in target:
                try:
                    v = StringUtils.toUnicode(t)
                except Exception:
                    v = '<UNPRINTABLE>'
                s += '%s[%s]: %s' % (indent, index, v)
            return s

        if isinstance(target, dict):
            for n,v in target.items():
                try:
                    v = StringUtils.toUnicode(v)
                except Exception:
                    v = '<UNPRINTABLE>'
                s += '%s%s: %s' % (indent, n, v)
            return s

        items = dir(target)
        for n in items:
            v = getattr(target, n)
            try:
                v = StringUtils.toUnicode(v)
            except Exception:
                v = '<UNPRINTABLE>'
            s += '%s%s: %s' % (indent, n, v)
        return s

#___________________________________________________________________________________________________ createErrorMessage
    @classmethod
    def createErrorMessage(cls, message, error):
        try:
            errorType = StringUtils.toUnicode(sys.exc_info()[0])
        except Exception:
            try:
                errorType = str(sys.exc_info()[0])
            except Exception:
                errorType = '[[UNABLE TO PARSE]]'

        try:
            errorValue = StringUtils.toUnicode(sys.exc_info()[1])
        except Exception:
            try:
                errorValue = str(sys.exc_info()[1])
            except Exception:
                errorValue = '[[UNABLE TO PARSE]]'

        try:
            error = StringUtils.toUnicode(error)
        except Exception as err:
            try:
                error = str(err)
            except Exception:
                error = '[[UNABLE TO PARSE]]'

        try:
            es = '%s\n    TYPE: %s\n    VALUE: %s\nERROR: %s\n' % (
                cls.formatAsString(message), errorType, errorValue, error)
        except Exception:
            try:
                es = '%s\n    [[ERROR ATTRIBUTE PARSING FAILURE]]' % cls.formatAsString(message)
            except Exception:
                es = 'FAILED TO PARSE EXCEPTION'

        return es

#___________________________________________________________________________________________________ formatAsString
    @classmethod
    def formatAsString(cls, src, indentLevel =0):
        indents = '    '*indentLevel
        if isinstance(src, (list, tuple)):
            out = [StringUtils.toUnicode('%s%s' % (indents, src[0]))]

            indents += '    '
            lines    = []
            maxIndex = 0

            for item in src[1:]:
                item     = StringUtils.toUnicode(item)
                index    = item.find(':')
                index    = index if index != -1 and index < 12 else 0
                maxIndex = max(index, maxIndex)
                lines.append([index, item])

            for item in lines:
                if item[0] > 0:
                    out.append(indents + (' '*max(0, maxIndex - item[0])) + item[1])
                else:
                    out.append(indents + item[1])
            return StringUtils.toUnicode('\n'.join(out))

        else:
            return StringUtils.toUnicode(indents + src)

#___________________________________________________________________________________________________ traceLogMessage
    @classmethod
    def traceLogMessage(cls, logMessage, callbacks =None, callbackTarget =None):

        log = logMessage['log']
        if 'stack' in logMessage:
            log += logMessage['stack']
        out = cls.asAscii(log)
        print(StringUtils.toText(out))

        try:
            for cb in callbacks:
                try:
                    cb(callbackTarget, out)
                except Exception:
                    pass
        except Exception:
            pass

        return out

#___________________________________________________________________________________________________ createLogMessage
    @classmethod
    def createLogMessage(
            cls, logValue, traceStack, shaveStackTrace, htmlEscape, prefix =None, **kwargs
    ):
        """ Formats log message data into a string for output """
        doIndent = kwargs.get('indent', True)

        if doIndent:
            logValue = cls.formatAsString(logValue)
        elif isinstance(logValue, (list, tuple)):
            logValue = '\n'.join(logValue)

        if htmlEscape:
            logValue = StringUtils.htmlEscape(logValue)

        if doIndent:
            logValue = logValue.replace('\n', '\n    ')
        logValue = StringUtils.strToUnicode(logValue)

        if not StringUtils.isStringType(logValue):
            logValue = 'FAILED TO LOG RESPONSE'

        out = {'log':logValue}

        if prefix:
            logPrefix = StringUtils.strToUnicode(prefix)
            if not StringUtils.isStringType(logPrefix):
                logPrefix = 'FAILED TO CREATE PREFIX'
            out['prefix'] = logPrefix

        if traceStack:
            logStack = StringUtils.strToUnicode(
                'Stack Trace:\n' + cls.getFormattedStackTrace(shaveStackTrace))
            if not StringUtils.isStringType(logStack):
                logStack = 'FAILED TO CREATE STACK'
            out['stack'] = logStack

        return out

#___________________________________________________________________________________________________ getTime
    @classmethod
    def getTime(cls, timezone =None):
        if timezone is None:
            return datetime.datetime.utcnow()

        try:
            import pytz
            dt = datetime.datetime.now(tz=pytz.utc)
            return dt.astimezone(tz=pytz.timezone(timezone))
        except Exception:
            return datetime.datetime.utcnow()

#___________________________________________________________________________________________________ asAscii
    @classmethod
    def asAscii(cls, string):
        if sys.version > '3':
            return StringUtils.toUnicode(string)

        if StringUtils.isStringType(string):
            try:
                return string.encode('utf8', 'ignore')
            except Exception:
                try:
                    return unicodedata.normalize('NFKD', string).encode('ascii', 'ignore')
                except Exception:
                    return '[[UNABLE TO DISPLAY LOG ENTRY IN ASCII CHARS]]'
        else:
            return string

#___________________________________________________________________________________________________ logMessageToString
    @classmethod
    def logMessageToString(
            cls, logMessage, includePrefix =True, includeStack =True, prefixSeparator ='\n    ',
            stackSeparator ='\n'
    ):
        out = []
        if includePrefix and 'prefix' in logMessage:
            out.append(StringUtils.toUnicode(logMessage['prefix']) + prefixSeparator)

        out.append(StringUtils.toUnicode(logMessage['log']))

        if includeStack and 'stack' in logMessage:
            out.append(stackSeparator + StringUtils.toUnicode(logMessage['stack']))

        return ''.join(out)

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __call__
    def __call__(self, s ='', *args, **kwargs):

        # If the call is an error, write the error
        err = ArgsUtils.get('err', args=args, index=1)
        if err and isinstance(err, Exception):
            if self._buffer:
                self.addError(s, err)
            else:
                self.writeError(s, err)

            return

        # Handle the non-error case
        traceStack      = ArgsUtils.get('traceStack', False, kwargs, args, 1)
        shaveStackTrace = ArgsUtils.get('shaveStackTrace', 0, kwargs, args, 2)
        if self._buffer:
            self.add(s, traceStack, shaveStackTrace)
        else:
            self.write(s, traceStack, shaveStackTrace)

#___________________________________________________________________________________________________ __del__
    def __del__(self):
        """ Attempt to flush the buffer if not empty as part of the deletion process."""
        try:
            self.flush()
        except Exception:
            pass
