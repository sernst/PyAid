# FileLock.py
# (C)2012
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import os
import time
import errno

from pyaid.number.IntUtils import IntUtils

#___________________________________________________________________________________________________ FileLock
class FileLock(object):
    """A FIFO lock file implementation for atomic multi-threaded file IO."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, fileName, ioMode ='a', timeout =10, delay =None):
        """ Prepare the file locker. Specify the file to lock and optionally the maximum timeout
        and the _delay between each attempt to lock."""
        self._isLocked      = False
        self._lockFileName  = fileName + '.lock'
        self._fileName      = fileName
        self._timeout       = timeout
        self._delay         = float(IntUtils.jitter(50, 0.1))
        self._ioMode        = ioMode
        self._lockFile      = None
        self._file          = None

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: isLocked
    @property
    def isLocked(self):
        return self._isLocked

#___________________________________________________________________________________________________ GS: lockFileName
    @property
    def lockFileName(self):
        return self._lockFileName

#___________________________________________________________________________________________________ GS: fileName
    @property
    def fileName(self):
        return self._fileName

#___________________________________________________________________________________________________ GS: fileName
    @property
    def file(self):
        return self._file

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ acquire
    def acquire(self):
        """ Acquire the lock, if possible. If the lock is in use, it check again every `wait`
            seconds. It does this until it either gets the lock or exceeds `timeout` number of
            seconds, in which case it throws an exception.
        """
        start = time.time()
        while True:
            try:
                self._lockFile = os.open(self._lockFileName, os.O_CREAT|os.O_EXCL|os.O_RDWR)
                try:
                    self._file = open(self._fileName, self._ioMode)
                except Exception:
                    continue
                break

            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                if (time.time() - start) >= self._timeout:
                    raise FileLockException('Lock acquisition exceeded specified timeout.')
                time.sleep(self._delay)

        self._isLocked = True

#___________________________________________________________________________________________________ release
    def release(self):
        """ Get rid of the lock by deleting the _lockFileName.
            When working in a `with` statement, this gets automatically
            called at the end.
        """
        if self._isLocked:
            if self._file:
                try:
                    self._file.close()
                    self._file = None
                except Exception:
                    pass

            try:
                os.close(self._lockFile)
                os.unlink(self._lockFileName)
            except Exception as err:
                pass
            self._isLocked = False

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ __enter__
    def __enter__(self):
        """ Activated when used in the with statement. Should automatically acquire a lock to be
            used in the with block. """
        if not self._isLocked:
            self.acquire()
        return self

#___________________________________________________________________________________________________ __exit__
    def __exit__(self, type, value, traceback):
        """ Activated at the end of the with statement. It automatically releases the lock if it
            is locked."""
        self.release()

#___________________________________________________________________________________________________ __del__
    def __del__(self):
        """ Make sure that the FileLock instance doesn't leave a _lockFileName
            lying around.
        """
        self.release()


#___________________________________________________________________________________________________ FileLockException
class FileLockException(Exception):
    pass
