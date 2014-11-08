# ColorTransformType.py
# (C)2011
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.xml.types.ConfigDataType import ConfigDataType

#___________________________________________________________________________________________________ ColorTransformType
class ColorTransformType(ConfigDataType):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    DATA_TYPE = 'ct'

#___________________________________________________________________________________________________ __init__
    def __init__(self, dataOrValue):
        """Creates a new instance of ColorTransformType."""
        ConfigDataType.__init__(self, dataOrValue, ColorTransformType.DATA_TYPE)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getAsData
    def getAsData(self):
        """Doc..."""
        a = self._data
        if len(a) < 8:
            a = [1.0, 1.0, 1.0, 1.0, a[0], a[0], a[0], a[1]]

        return {
            'redMultiplier':a[0],
            'greenMultiplier':a[1],
            'blueMultiplier':a[2],
            'alphaMultiplier':a[3],
            'redOffset':a[4],
            'greenOffset':a[5],
            'blueOffset':a[6],
            'alphaOffset':a[7]
        }

#___________________________________________________________________________________________________ getAsSerialData
    def getAsSerialData(self):
        """Doc..."""
        return '|'.join(self._data)

#___________________________________________________________________________________________________ getAsInterchangeData
    def getAsInterchangeData(self):
        """Doc..."""
        return [self._type, self.getAsSerialData()]

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _parseData
    def _parseData(self, dataOrValue):
        """Doc..."""
        if isinstance(dataOrValue, list):
            return dataOrValue
        elif isinstance(dataOrValue, str):
            return dataOrValue.split('|')

        return [255, 255]
