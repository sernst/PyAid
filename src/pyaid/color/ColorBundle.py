# ColorBundle.py
# (C)2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.color.ColorValue import ColorValue

#___________________________________________________________________________________________________ ColorBundle
class ColorBundle(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    _BASE_COLOR_KEY = 'baseColor'

#___________________________________________________________________________________________________ __init__
    def __init__(self, baseColor =None, colorClass =None, **kwargs):
        """Creates a new instance of ColorBundle."""
        self._baseColor       = baseColor
        self._colorValueCache = dict()
        self._autoColorCache  = dict()
        self._colorClass      = colorClass if colorClass else ColorValue

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: autoBase
    @property
    def autoBase(self):
        return self._baseColor is None

#___________________________________________________________________________________________________ GS: baseColor
    @property
    def baseColor(self):
        return self._getColor(self.__class__._BASE_COLOR_KEY, self._generateBaseColor)
    @baseColor.setter
    def baseColor(self, value):
        self._setColor(value, self.__class__._BASE_COLOR_KEY)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ refresh
    def refresh(self):
        self._clearColorCaches()

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _generateBaseColor
    def _generateBaseColor(self):
        return self._createColorValue(0)

#___________________________________________________________________________________________________ _getColor
    def _getColor(self, key, autoFunc):
        colorValue = self._colorValueCache.get(key, None)
        if colorValue:
            return colorValue

        colorValue = self._autoColorCache.get(key, None)
        if colorValue:
            return colorValue

        rawColor = getattr(self, '_' + key, None)
        if rawColor is not None:
            color = self._createColorValue(rawColor)
            if color:
                self._colorValueCache[key] = color
                return color

        color = autoFunc()
        self._autoColorCache[key] = color
        return color

#___________________________________________________________________________________________________ _setColor
    def _setColor(self, value, key):
        self._clearColorCaches(key)
        setattr(self, '_' + key, value)

#___________________________________________________________________________________________________ _clearColorCaches
    def _clearColorCaches(self, key =None):
        if key is None:
            self._autoColorCache  = dict()
            self._colorValueCache = dict()
            return

        if key in self._autoColorCache:
            del self._autoColorCache[key]

        if key in self._colorValueCache:
            del self._colorValueCache[key]

#___________________________________________________________________________________________________ _createColorValue
    def _createColorValue(self, value):
        """Doc..."""
        if value is None:
            return None

        if isinstance(value, ColorValue):
            return value.clone()

        return self._colorClass(value)



#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
