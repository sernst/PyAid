# Base36.py
# (C)2010-2014
# Scott Ernst and Eric David Wills

import re
import uuid

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
        if n == '0':
            return 0

        if clean:
            n = Base36.ILLEGAL_CHAR_RE.sub('', n)

        return int(n, 36)

#___________________________________________________________________________________________________ random
    @classmethod
    def random(cls, n):
        """ Creates a random base-36 number with the specified length.

           n |int
            Length of the resulting random string

           returns: str """

        out = ''
        while n >= 16:
            out += cls._getRandom(16)
            n   -= 16
        if n != 0:
            out += cls._getRandom(n)
        return out

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getRandom
    @classmethod
    def _getRandom(cls, n):
        min   = 36**(n - 1)
        range = 36**n - 1 - min
        seed  = int(uuid.uuid1())/2 + int(uuid.uuid4())/2
        return cls.to36((seed % range) + min)
