# FocalColorBundle.py
# (C)2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.color.ColorBundle import ColorBundle

#___________________________________________________________________________________________________ FocalColorBundle
class FocalColorBundle(ColorBundle):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    _SOFT_COLOR_KEY      = 'softColor'
    _HIGHLIGHT_COLOR_KEY = 'highlightColor'
    _LINK_COLOR_KEY      = 'linkColor'
    _BUTTON_COLOR_KEY    = 'buttonColor'

#___________________________________________________________________________________________________ __init__
    def __init__(self, baseColor =None, softColor =None, highlightColor =None, linkColor =None,
                 buttonColor =None, colorClass =None, **kwargs):
        """Creates a new instance of FocalColorBundle."""
        ColorBundle.__init__(self, baseColor=baseColor, colorClass=colorClass, **kwargs)
        self._softColor      = softColor
        self._highlightColor = highlightColor
        self._linkColor      = linkColor
        self._buttonColor    = buttonColor

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: autoSoft
    @property
    def autoSoft(self):
        return self._softColor is None

#___________________________________________________________________________________________________ GS: softColor
    @property
    def softColor(self):
        return self._getColor(self.__class__._SOFT_COLOR_KEY, self._generateSoftColor)
    @softColor.setter
    def softColor(self, value):
        self._setColor(value, self.__class__._SOFT_COLOR_KEY)

#___________________________________________________________________________________________________ GS: autoHighlight
    @property
    def autoHighlight(self):
        return self._softColor is None

#___________________________________________________________________________________________________ GS: highlightColor
    @property
    def highlightColor(self):
        return self._getColor(self.__class__._HIGHLIGHT_COLOR_KEY, self._generateHighlightColor)
    @highlightColor.setter
    def highlightColor(self, value):
        self._setColor(value, self.__class__._HIGHLIGHT_COLOR_KEY)

#___________________________________________________________________________________________________ GS: autoLink
    @property
    def autoLink(self):
        return self._linkColor is None

#___________________________________________________________________________________________________ GS: linkColor
    @property
    def linkColor(self):
        return self._getColor(self.__class__._LINK_COLOR_KEY, self._generateLinkColor)
    @linkColor.setter
    def linkColor(self, value):
        self._setColor(value, self.__class__._LINK_COLOR_KEY)

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
        return self._createColorValue('#444')

#___________________________________________________________________________________________________ _generateSoftColor
    def _generateSoftColor(self):
        color = self.baseColor.clone()
        color.dodgeShift(0.2)
        return color

#___________________________________________________________________________________________________ _generateHighlightColor
    def _generateHighlightColor(self):
        color = self.baseColor.clone()
        if color.brightness > 0.5:
            color.burnShift(0.5)
        else:
            color.dodgeShift(0.5)

        return color

#___________________________________________________________________________________________________ _generateLinkColor
    def _generateLinkColor(self):
        color = self.baseColor.clone()
        color.burnShift(0.2)
        return color

#___________________________________________________________________________________________________ _generateButtonColor
    def _generateButtonColor(self):
        return self.baseColor.clone()
