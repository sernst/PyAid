# ConfigData.py
# (C)2011
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.xml.types.ConfigDataType import ConfigDataType
from pyaid.xml.types.ColorTransformType import ColorTransformType

#___________________________________________________________________________________________________ ConfigData
class ConfigData(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        """Creates a new instance of ConfigData."""
        self._data = {}

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ writeToInterchangeDict
    def writeToInterchangeDict(self, target =None):
        if target is None:
            target = {}

        for n,v in self._data.items():
            if isinstance(v, ConfigData):
                target[n] = v.writeToInterchangeDict()
            elif isinstance(v, ConfigDataType):
                target[n] = v.getAsInterchangeData()
            elif isinstance(v, list):
                l = []
                l.extend(v)
                target[n] = l
            else:
                target[n] = v

        return target

#___________________________________________________________________________________________________ writeToDict
    def writeToDict(self, target =None):
        if target is None:
            target = {}

        for n,v in self._data.items():
            if isinstance(v, ConfigData):
                target[n] = v.writeToDict()
            elif isinstance(v, ConfigDataType):
                target[n] = v.getAsData()
            elif isinstance(v, list):
                target[n] = v[1]
            else:
                target[n] = v

        return target

#___________________________________________________________________________________________________ setItem
    def setItem(self, name, itemType, value):
        """Doc..."""
        if isinstance(value, ConfigData):
            self._data[name] = value
            return

        itemType = str(itemType)

        d = ConfigData._deserializeValue(itemType, value)
        if itemType in ['s','n']:
            self._data[name] = d
        elif isinstance(d, ConfigDataType):
            self._data[name] = d
        else:
            self._data[name] = [itemType, d]

#___________________________________________________________________________________________________ getItem
    def getItem(self, name):
        """Doc..."""
        if hasattr(self._data, name):
            item = getattr(self._data, name)
            if isinstance(item, list):
                return item[1]
            elif isinstance(item, ConfigDataType):
                return item.getAsData()
            elif isinstance(item, ConfigData):
                return item.writeToDict()
            else:
                return item

        return None

#___________________________________________________________________________________________________ getItemData
    def getItemData(self, name):
        """Doc..."""
        if hasattr(self._data, name):
            return getattr(self._data, name)

        return None

#___________________________________________________________________________________________________ getItemType
    def getItemType(self, name):
        """Doc..."""

        if hasattr(self._data, name):
            item = getattr(self._data, name)

            if isinstance(item, list):
                return item[0]
            elif isinstance(item, ConfigData):
                return 'o'
            elif isinstance(item, ConfigDataType):
                return item.dataType
            elif isinstance(item, str):
                return 's'
            elif isinstance(item, (int, float)):
                return 'n'

        return None

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _deserializeValue
    @staticmethod
    def _deserializeValue(attrType, attrValue):
        t = attrType
        v = attrValue.encode('utf-8')

        #-------------------------------------------------------------------------------------------
        # Boolean
        if t == 'b':
            return (v != 'false') and (v != '0') and (v != 'off')

        #-------------------------------------------------------------------------------------------
        # Hex
        elif t == 'h':
            if v == '0':
                return 0

            return int(v, 16)

        #-------------------------------------------------------------------------------------------
        # Unsigned Int
        elif t == 'ui':
            return int(v)

        #-------------------------------------------------------------------------------------------
        # Number (float)
        elif t == 'n':
            return float(v)

        #-------------------------------------------------------------------------------------------
        # ColorTransform
        elif t == 'ct':
            return ColorTransformType(v)

        #-------------------------------------------------------------------------------------------
        # Vector of Strings
        elif t == 'vs':
            return v.split('|')

        #-------------------------------------------------------------------------------------------
        # Vector of Numbers (floats)
        elif t == 'vn':
            array = v.split('|')
            out   = []
            for item in array:
                out.append(float(item))

            return out

        #-------------------------------------------------------------------------------------------
        # Vector of Unsigned Ints
        elif t == 'vui':
            array = v.split('|')
            out   = []
            for item in array:
                out.append(int(item))

            return out

        else:
            return v
