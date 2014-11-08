# DomUtils.py
# (C)2012-2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import re
from collections import namedtuple

#___________________________________________________________________________________________________ DomUtils
class DomUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    PRESERVE_BLOCK_DEFINITION = namedtuple('PreserveBlock', ['start', 'end', 'match'])

    _HTML_WHITESPACE_PATTERN = re.compile(
        '(?P<preSpace>[\t\n]*)(?P<tag></?[^\n\t\s>]+[^>]*>)(?P<postSpace>[\t\n]*)'
    )

    _EXTRA_SPACES_PATTERN = re.compile('[\s\t\n]{2,}')

    _SINGLE_TAG_CLOSER_PATTERN = re.compile('/[\s\t\n]*>')

    _PRESERVE_PATTERN = re.compile(
        '(<pre|<script|<style|\[#code|\[#raw|</pre>|</script>|</style>|\[/#code\]|\[/#raw\])'
    )

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ minifyDom
    @classmethod
    def minifyDom(cls, source):
        if not source:
            return source

        source = source.replace('\r', '').strip()

        if source.startswith('<!DOCTYPE'):
            offset = source.find('\n') + 1
            out    = source[0:offset]
        else:
            offset = 0
            out    = ''

        startIndex = offset
        endIndex   = offset

        preserveBlocks = cls.getPreserveBlocks(source)
        for b in preserveBlocks:
            if b.end < 0 or b.end < endIndex:
                continue

            startIndex = max(startIndex, b.start)
            endIndex   = max(endIndex, b.end)

            out += cls._EXTRA_SPACES_PATTERN.sub(' ',
                cls._HTML_WHITESPACE_PATTERN.sub('\g<tag>', source[offset:startIndex])
            ).replace('\n', '')
            out    += source[startIndex:endIndex]
            offset  = endIndex

        if offset < len(source):
            out += cls._EXTRA_SPACES_PATTERN.sub(' ',
                cls._HTML_WHITESPACE_PATTERN.sub('\g<tag>', source[offset:len(source)])
            ).replace('\n', '')

        out = out.strip()
        return out

#___________________________________________________________________________________________________ getPreserveBlocks
    @classmethod
    def getPreserveBlocks(cls, source):
        """ FIND PRE/SCRIPT/STYLE TAG BLOCKS SO THEY CAN BE IGNORED DURING WHITESPACE CLEANUP. """
        preserveBlocks = []
        res = cls._PRESERVE_PATTERN.finditer(source)
        if res:
            for r in res:
                match = r.group()
                if preserveBlocks and match[1] == '/':
                    i = 0
                    while i > -len(preserveBlocks):
                        i -= 1
                        b = preserveBlocks[i]
                        if b.match == match[2:-1] and b.end == -1:
                            preserveBlocks[i] = cls.PRESERVE_BLOCK_DEFINITION(
                                start=b.start,
                                end=r.end(),
                                match=b.match
                            )
                            break
                else:
                    preserveBlocks.append(
                        cls.PRESERVE_BLOCK_DEFINITION(start=r.start(), end=-1, match=match[1:])
                    )

        return preserveBlocks
