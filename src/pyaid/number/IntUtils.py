# IntUtils.py
# (C)2012
# Scott Ernst

import sys
import math
import random

if sys.version > '3':
    long = int

#___________________________________________________________________________________________________ IntUtils
class IntUtils(object):
    """A class for integer related operations."""

#===================================================================================================
#                                                                                     P U B L I C

    LONG = long

#___________________________________________________________________________________________________ isInt
    @classmethod
    def isInt(cls, value):
        """isInt doc..."""
        return isinstance(value, (int, long))

#___________________________________________________________________________________________________ jitter
    @staticmethod
    def jitter(nominal, deviation =0.25, additive =False):
        """Returns an integer that is randomly jittered by the specified deviation.

        @@@param nominal:int
            The normal value around which to jitter.

        @@@param deviation:float
            Fractional value specifying the max or min deviation from nominal.

        @@@returns int
            The jittered value.
        """

        nominal = float(nominal)

        if additive:
            return nominal + random.randint(0, int(math.floor(deviation*nominal)))

        return random.randint(int(math.floor((1.0 - deviation)*nominal)),
                              int(math.ceil((1.0 + deviation)*nominal)))
