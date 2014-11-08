# TextSource.py
# (C)2012
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.ArgsUtils import ArgsUtils

#___________________________________________________________________________________________________ TextSource
class TextSource(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, *args, **kwargs):
        """Creates a new instance of TextSource."""
        self._raw      = ArgsUtils.get('source', '', kwargs, args, 0)
        self._analyzer = ArgsUtils.get('analyzer', None, kwargs, args, 1)
        self._blocks   = ArgsUtils.get('blocks', [], kwargs, args, 2)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: source
    @property
    def source(self):
        return self._raw
    @source.setter
    def source(self, value):
        self._raw = value

#___________________________________________________________________________________________________ GS: analyzer
    @property
    def analyzer(self):
        return self._analyzer
    @analyzer.setter
    def analyzer(self, value):
        self._analyzer = value

#___________________________________________________________________________________________________ GS: blocks
    @property
    def blocks(self):
        return self._blocks
    @blocks.setter
    def blocks(self, value):
        self._blocks = value
