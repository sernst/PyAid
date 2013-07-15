# Base36.py
# (C)2010-2013
# Scott Ernst and Eric David Wills

import re

#___________________________________________________________________________________________________ Base36
class Base36(object):

#===================================================================================================
#                                                                                       C L A S S

    CHAR_SET = '0123456789abcdefghijklmnopqrstuvwxyz'

    ILLEGAL_CHAR_RE = re.compile('[^0-9a-z]')

# __________________________________________________________________________________________________ to64
    @staticmethod
    def to36(n):
        if n == 0:
            return '0'

        out     = ''
        while n != 0:
            n, m = divmod(long(n), 36)
            out  = Base36.CHAR_SET[int(m)] + out
        return out

# __________________________________________________________________________________________________ from64
    @staticmethod
    def from36(n, clean =False):

        if clean:
            n = Base36.ILLEGAL_CHAR_RE.sub('', n)

        return int(n, 36)
