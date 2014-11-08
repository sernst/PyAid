# RedactionTextAnalyzer.py
# (C)2012
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import re

from pyaid.text.BlockSyntaxEnum import BlockSyntaxEnum
from pyaid.text.TextAnalyzer import TextAnalyzer

#___________________________________________________________________________________________________ RedactionTextAnalyzer
class RedactionTextAnalyzer(TextAnalyzer):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, src ='', debug =False, blockDefs =None, redactionCharacter =' '):
        """Creates a new instance of ClassTemplate."""
        TextAnalyzer.__init__(self, src, debug, blockDefs)
        self._redacted   = ''
        self._redactChar = redactionCharacter

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: redacted
    @property
    def redacted(self):
        return self._redacted

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ lookAhead
    def lookAhead(self, index, pattern, redacted =False):
        return self._lookAhead(self._redacted if redacted else self._raw, index, pattern)

#___________________________________________________________________________________________________ lookBack
    def lookBack(self, index, pattern, redacted =False):
        return self._lookBack(self._redacted if redacted else self._raw, index, pattern)

#___________________________________________________________________________________________________ matches
    def matches(self, index, pattern, matchReqs =None, redacted =False):
        return self._matches(self._redacted if redacted else self._raw, index, pattern, matchReqs)

#___________________________________________________________________________________________________ changeOffsets
    def changeOffsets(self, index, amount):
        TextAnalyzer.changeOffsets(self, index, amount)
        self._postAnalyzeImpl()

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _insertImpl
    def _insertImpl(self, start, end, value):
        self._raw      = self._raw[:start] + value + self._raw[end:]
        self._redacted = self._redacted[:start] + value + self._redacted[end:]

#___________________________________________________________________________________________________ _redactBlockImpl
    def _redactBlockImpl(self, block, source, replace):
        return replace

#___________________________________________________________________________________________________ _postAnalyzeImpl
    def _postAnalyzeImpl(self):
        res = self._raw
        p   = re.compile('[^\n]{1}')
        for b in self._blocks:
            if not b.blockType in [BlockSyntaxEnum.COMMENT, BlockSyntaxEnum.STRING,
                                   BlockSyntaxEnum.REGEX]:
                continue

            start = b.start
            end   = b.end
            blen  = end - start
            src   = self._raw[start:end]
            rep   = p.sub(self._redactChar, src)
            rep   = self._redactBlockImpl(b, src, rep)
            res   = res[:start] + rep + res[end:]

        self._redacted = res
