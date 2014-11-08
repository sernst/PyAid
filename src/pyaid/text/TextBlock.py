# TextBlock.py
# (C)2012
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.text.TextBookmark import TextBookmark

#___________________________________________________________________________________________________ TextBlock
class TextBlock(TextBookmark):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, blockDef, start, end =None, data =None, **kwargs):
        """Creates a new instance of TextBlock."""
        name = kwargs.get('name', blockDef.name)
        TextBookmark.__init__(self, start, end, name, data)
        self._blockDef = blockDef

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: blockType
    @property
    def blockDef(self):
        return self._blockDef

#___________________________________________________________________________________________________ GS: findState
    @property
    def findState(self):
        return self._blockDef.findState

#___________________________________________________________________________________________________ GS: blockType
    @property
    def blockType(self):
        return self._blockDef.blockType

#___________________________________________________________________________________________________ GS: terminator
    @property
    def terminator(self):
        return self._blockDef.terminator

#___________________________________________________________________________________________________ GS: pattern
    @property
    def pattern(self):
        return self._blockDef.pattern

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<Block:%s(%s) %s:%s [original %s:%s]>' % (
            self.blockType,
            self.pattern,
            str(self.start),
            str(self.end),
            str(self.originalStart),
            str(self.originalEnd)
        )

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _cloneImpl
    def _cloneImpl(self, **kwargs):
        return TextBookmark._cloneImpl(self, blockDef=self._blockDef)
