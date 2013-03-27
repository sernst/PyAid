# SolrUtils.py
# (C)2011-2012
# Eric David Wills

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
