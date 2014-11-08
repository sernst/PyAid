# SolrUtils.py
# (C)2011-2012
# Eric David Wills

from __future__ import print_function, absolute_import, unicode_literals, division

import re

#___________________________________________________________________________________________________ SolrUtils
class SolrUtils(object):

    _ENCODE_RE = re.compile(r'(?<!\\)(?P<char>[&|+\-!(){}[\]^"~*?:])')

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ encode
    @staticmethod
    def encode(text):
        return SolrUtils._ENCODE_RE.sub(r'\\\g<char>', text.lower())
