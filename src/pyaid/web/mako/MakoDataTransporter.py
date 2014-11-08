# MakoDataTransporter.py
# (C)2012
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.NullUtils import NullUtils
from pyaid.debug.Logger import Logger
from pyaid.string.StringUtils import StringUtils

#___________________________________________________________________________________________________ MakoDataTransporter
class MakoDataTransporter(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    _NULL = NullUtils.NULL('internal_null')

#___________________________________________________________________________________________________ __init__
    def __init__(self, data, logger =None):
        """Creates a new instance of MakoDataTransporter."""
        self._log       = logger if logger else Logger(self)
        self._data      = data if data else dict()
        self._traces    = []
        self._warns     = []
        self._rootData  = None

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getTraces
    def getTraces(self):
        return self._traces

#___________________________________________________________________________________________________ has
    def has(self, attribute):
        return attribute in self._data

#___________________________________________________________________________________________________ trace
    def trace(self, message):
        try:
            self._traces.append(StringUtils.toUnicode(message))
        except Exception as err:
            self._log.writeError('Unable to trace message', err)

#___________________________________________________________________________________________________ registerRootData
    def registerRootData(self, rootData):
        self._rootData = rootData

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ __getattr__
    def __getattr__(self, attr):
        if attr not in self._data:
            self._log.write('Missing render template attribute: ' + str(attr))
            return ''

        return self._data.get(attr, '')
