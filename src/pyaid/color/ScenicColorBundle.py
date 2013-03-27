# ScenicColorBundle.py
# (C)2013
# Scott Ernst

from pyaid.color.ColorBundle import ColorBundle

#___________________________________________________________________________________________________ ScenicColorBundle
class ScenicColorBundle(ColorBundle):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    _DODGE_COLOR_KEY  = 'dodgeColor'
    _BURN_COLOR_KEY   = 'burnColor'
    _BORDER_COLOR_KEY = 'borderColor'
    _BUTTON_COLOR_KEY = 'buttonColor'

#___________________________________________________________________________________________________ __init__
    def __init__(self, baseColor =None, burnColor =None, dodgeColor =None, borderColor =None,
                 buttonColor =None, colorClass =None, **kwargs):
        """Creates a new instance of ScenicColorBundle."""
        ColorBundle.__init__(self, baseColor=baseColor, colorClass=colorClass, **kwargs)
        self._dodgeColor  = self._createColorValue(dodgeColor)
        self._burnColor   = self._createColorValue(burnColor)
        self._borderColor = self._createColorValue(borderColor)
        self._buttonColor = self._createColorValue(buttonColor)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: autoDodge
    @property
    def autoDodge(self):
        return self._dodgeColor is None

#___________________________________________________________________________________________________ GS: dodgeColor
    @property
    def dodgeColor(self):
        return self._getColor(self.__class__._DODGE_COLOR_KEY, self._generateDodgeColor)
    @dodgeColor.setter
    def dodgeColor(self, value):
        self._setColor(value, self.__class__._DODGE_COLOR_KEY)

#___________________________________________________________________________________________________ GS: autoBurn
    @property
    def autoBurn(self):
        return self._burnColor is None

#___________________________________________________________________________________________________ GS: burnColor
    @property
    def burnColor(self):
        return self._getColor(self.__class__._BURN_COLOR_KEY, self._generateBurnColor)
    @burnColor.setter
    def burnColor(self, value):
        self._setColor(value, self.__class__._BURN_COLOR_KEY)

#___________________________________________________________________________________________________ GS: autoBorder
    @property
    def autoBorder(self):
        return self._borderColor is None

#___________________________________________________________________________________________________ GS: borderColor
    @property
    def borderColor(self):
        return self._getColor(self.__class__._BORDER_COLOR_KEY, self._generateBorderColor)
    @borderColor.setter
    def borderColor(self, value):
        self._setColor(value, self.__class__._BORDER_COLOR_KEY)

#___________________________________________________________________________________________________ GS: autoButton
    @property
    def autoButton(self):
        return self._buttonColor is None

#___________________________________________________________________________________________________ GS: buttonColor
    @property
    def buttonColor(self):
        return self._getColor(self.__class__._BUTTON_COLOR_KEY, self._generateButtonColor)
    @buttonColor.setter
    def buttonColor(self, value):
        self._setColor(value, self.__class__._BUTTON_COLOR_KEY)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _generateBaseColor
    def _generateBaseColor(self):
        return self._createColorValue(16777215)

#___________________________________________________________________________________________________ _generateDodgeColor
    def _generateDodgeColor(self):
        color = self.baseColor.clone()
        color.dodgeShift(0.75)
        return color

#___________________________________________________________________________________________________ _generateBurnColor
    def _generateBurnColor(self):
        color = self.baseColor.clone()
        color.burnShift(0.25)
        return color

#___________________________________________________________________________________________________ _generateBorderColor
    def _generateBorderColor(self):
        color = self.baseColor.clone()
        color.burnShift(0.4)
        return color

#___________________________________________________________________________________________________ _generateButtonColor
    def _generateButtonColor(self):
        color = self.baseColor.clone()
        color.burnShift(0.05)
        return color
