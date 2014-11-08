# TextBookmark.py
# (C)2012
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.ArgsUtils import ArgsUtils

#___________________________________________________________________________________________________ TextBookmark
class TextBookmark(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, start, end =None, name =None, data =None, **kwargs):
        """Creates a new instance of TextBookmark."""

        self._name  = name
        self._start = start
        self._end   = start if end is None else end
        self._data  = data

        self._originalStart = ArgsUtils.get('originalStart', self._start, kwargs)
        self._originalEnd   = ArgsUtils.get('originalEnd', self._end, kwargs)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: start
    @property
    def start(self):
        return self._start
    @start.setter
    def start(self, value):
        self._start = value

#___________________________________________________________________________________________________ GS: end
    @property
    def end(self):
        return self._end
    @end.setter
    def end(self, value):
        if (self._end is None and self._originalEnd is None) or \
                (self._end < self.start and self._originalEnd < self._originalStart):
            self._originalEnd = value

        self._end = value

#___________________________________________________________________________________________________ GS: name
    @property
    def name(self):
        return self._name

#___________________________________________________________________________________________________ GS: data
    @property
    def data(self):
        return self._data

#___________________________________________________________________________________________________ GS: originalStart
    @property
    def originalStart(self):
        return self._originalStart

#___________________________________________________________________________________________________ GS: originalEnd
    @property
    def originalEnd(self):
        return self._originalEnd

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ clone
    def clone(self):
        return self._cloneImpl()

#___________________________________________________________________________________________________ changeOffset
    def changeOffset(self, index, amount):
        """Doc..."""
        if index > self.end:
            return

        if index < self.start:
            self._start += amount

        if index < self._end:
            #self._end += amount
            self._end = max(self._start, self._end + amount)

#___________________________________________________________________________________________________ contains
    def contains(self, index):
        return self.start <= index < self.end

#___________________________________________________________________________________________________ distanceFromIndex
    def distanceFromIndex(self, index, allowContains =True, searchAhead =True, searchBack =True):
        if self.contains(index):
            return 0 if allowContains else float('inf')

        ahead = abs(self.start - index) if searchAhead else float('inf')
        back  = abs(self.end - index) if searchBack else float('inf')
        return min(ahead, back)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _cloneImpl
    def _cloneImpl(self, **kwargs):
        return self.__class__(
            start=self._start,
            end=self._end,
            name=self._name,
            data=self._data,
            originalStart=self._originalStart,
            originalEnd=self._originalEnd,
            **kwargs
        )
