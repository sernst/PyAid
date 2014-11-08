# ConfigDataType.py
# (C)2011
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

#___________________________________________________________________________________________________ ConfigDataType
class ConfigDataType(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, dataOrValue, dataType):
        """Creates a new instance of ConfigDataType."""
        self._type = dataType
        self._data = self._parseData(dataOrValue)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: dataType
    @property
    def dataType(self):
        return self._type

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getAsData
    def getAsData(self):
        """Doc..."""
        return None

#___________________________________________________________________________________________________ getAsSerialData
    def getAsSerialData(self):
        """Doc..."""
        return None

#___________________________________________________________________________________________________ getAsInterchangeData
    def getAsInterchangeData(self):
        """Doc..."""
        return [self._type, self.getAsSerialData()]

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _parseData
    def _parseData(self, dataOrValue):
        """Doc..."""
        return None
