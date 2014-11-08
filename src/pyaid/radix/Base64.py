# Base64.py
# (C) 2010-2013
# Eric David Wills and Scott Ernst

import re
import uuid

#___________________________________________________________________________________________________ Base64
class Base64(object):

#===================================================================================================
#                                                                                       C L A S S

    CHAR_SET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~'

    ILLEGAL_CHAR_RE = re.compile('[^0-9A-Za-z_~]+')

    CHAR_MAP = {
        '0':0,  '1':1,  '2':2,  '3':3,  '4':4,  '5':5,  '6':6,  '7':7,  '8':8,  '9':9,
        'A':10, 'B':11, 'C':12, 'D':13, 'E':14, 'F':15, 'G':16, 'H':17, 'I':18, 'J':19,
        'K':20, 'L':21, 'M':22, 'N':23, 'O':24, 'P':25, 'Q':26, 'R':27, 'S':28, 'T':29,
        'U':30, 'V':31, 'W':32, 'X':33, 'Y':34, 'Z':35, '_':36, 'a':37, 'b':38, 'c':39,
        'd':40, 'e':41, 'f':42, 'g':43, 'h':44, 'i':45, 'j':46, 'k':47, 'l':48, 'm':49,
        'n':50, 'o':51, 'p':52, 'q':53, 'r':54, 's':55, 't':56, 'u':57, 'v':58, 'w':59,
        'x':60, 'y':61, 'z':62, '~':63 }

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ to64
    @staticmethod
    def to64(n):
        """Creates the specified base-10 integer to base 64.
           @param n - Input integer [int]
           @return str
        """

        try:
            n = int(n)
        except Exception:
            return u''

        out = u''
        while n > 0:
            out = Base64.CHAR_SET[n & 63] + out
            n >>= 6

        return out

#___________________________________________________________________________________________________ from64
    @staticmethod
    def from64(n, clean =False):
        """Creates the specified base-64 number to base 10.
           @param n - Input number [str]
           @return int
        """

        if clean:
            n = Base64.ILLEGAL_CHAR_RE.sub(u'', n)

        base = 1
        out  = 0
        for c in n[::-1]:
            out += Base64.CHAR_MAP[c]*base
            base <<= 6

        return out

#___________________________________________________________________________________________________ listTo64
    @staticmethod
    def listTo64(l):
        """Converts the specified list of base-10 integers to base 64.
           @param l - Input list [list]
           @return list
        """

        for i in range(0, len(l)):
            l[i] = Base64.to64(l[i])
        return l

#___________________________________________________________________________________________________ listFrom64
    @staticmethod
    def listFrom64(l):
        """Converts the specified list of base-64 integers to base 10.
           @param l - Input list [list]
           @return list
        """

        for i in range(0, len(l)):
            l[i] = Base64.from64(l[i])
        return l

#___________________________________________________________________________________________________ random
    @staticmethod
    def random(n):
        """Creates a random base-64 number with the specified length.
           @param n - Number of characters [int]
           @return str
        """

        out = ''
        while n >= 16:
            out += Base64._getRandom(16)
            n   -= 16
        if n != 0:
            out += Base64._getRandom(n)
        return out

#___________________________________________________________________________________________________ random16
    @staticmethod
    def random16():
        """Creates a random base-64 number with the length 16.  Useful as a function pointer.
           @return str
        """
        return Base64.random(16)

#___________________________________________________________________________________________________ random40
    @staticmethod
    def random40():
        """Creates a random base-64 number with the length 40.  Useful as a function pointer.
           @return str
        """
        return Base64.random(40)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getRandom
    @staticmethod
    def _getRandom(n):
        mins   = 64**(n - 1)
        ranger = 64**n - 1 - mins
        seed  = int(uuid.uuid1())/2 + int(uuid.uuid4())/2
        return Base64.to64((seed % ranger) + mins)

