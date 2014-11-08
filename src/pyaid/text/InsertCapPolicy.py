# InsertCapPolicy.py
# (C)2012
# Scott Ernst

import re

from pyaid.string.StringUtils import StringUtils

#___________________________________________________________________________________________________ InsertCapPolicy
class InsertCapPolicy(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    AHEAD_TYPE = 'ahead'
    BACK_TYPE  = 'back'

    NEWLINE_BACK = re.compile('(?P<target>[\n]{1})(?P<suffix>[\s\t]*)$')
    NEWLINE_AHEAD = re.compile('^(?P<prefix>[\s\t]*)(?P<target>[\n]{1})')
    NEWLINE_BACK_MULTI_ONLY = re.compile(
        '(?P<prefix>[\n]+[\s\t]*)(?P<target>[\n]{1})(?P<suffix>[\s\t]*)$' )
    NEWLINE_NO_TAG_AHEAD = re.compile(
        '^(?P<prefix>[\s\t]*)(?P<target>[\n]{1})(?![\s\t\n]*\[#[A-Za-z0-9_]+)' )

#___________________________________________________________________________________________________ __init__
    def __init__(self, capType, addExp =None, addReplace =u'', removeExp =None, removeReplace =u''):
        """Creates a new instance of ClassTemplate."""
        self._addPattern    = re.compile(addExp) if StringUtils.isStringType(addExp) else addExp
        self._removePattern = re.compile(removeExp) if StringUtils.isStringType(removeExp) else removeExp
        self._addReplace    = addReplace
        self._removeReplace = removeReplace
        self._capType       = capType

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: capType
    @property
    def capType(self):
        return self._capType

#___________________________________________________________________________________________________ GS: addPattern
    @property
    def addPattern(self):
        return self._addPattern

#___________________________________________________________________________________________________ GS: addPattern
    @property
    def addReplace(self):
        return self._addReplace

#___________________________________________________________________________________________________ GS: removePattern
    @property
    def removePattern(self):
        return self._removePattern

#___________________________________________________________________________________________________ GS: addPattern
    @property
    def removeReplace(self):
        return self._removeReplace

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ modifyCap
    def modifyCap(self, processor, index):
        offset  = self.remove(processor, index)
        offset += self.add(processor, index + offset)
        return offset

#___________________________________________________________________________________________________ add
    def add(self, processor, index):
        """Doc..."""
        if self._addPattern is None:
            return 0

        res, span = self._search(processor, index, self._addPattern)
        if not res:
            return processor.insertCharacters(index, index, self._addReplace)

        return 0

#___________________________________________________________________________________________________ remove
    def remove(self, processor, index):
        """Doc..."""
        if self._removePattern is None:
            return 0

        res, span = self._search(processor, index, self._removePattern)
        if res:
            if self.capType == InsertCapPolicy.AHEAD_TYPE:
                s = index + span[0]
                e = index + span[1]
            else:
                s = index - len(res.group())
                e = s + span[1]
                s += span[0]

            return processor.insertCharacters(s, e, self._removeReplace)

        return 0

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _search
    def _search(self, processor, index, pattern):
        """Doc..."""
        if self.capType == InsertCapPolicy.AHEAD_TYPE:
            res = pattern.search(processor.result[index:])
        else:
            res = pattern.search(processor.result[:index])

        if res:
            d      = res.groupdict()
            prefix = len(d['prefix']) if 'prefix' in d else 0
            target = len(d['target']) if 'target' in d else 0
            span = (prefix, prefix + target)
        else:
            span = (0,0)

        return res, span

