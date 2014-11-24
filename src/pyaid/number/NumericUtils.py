# NumericUtils.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math
import sys

if sys.version > '3':
    long = int

#___________________________________________________________________________________________________ NumericUtils
class NumericUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ equivalent
    @classmethod
    def equivalent(cls, a, b, epsilon =None):
        """equivalent doc..."""
        if epsilon is None:
            epsilon = 10.0*sys.float_info.epsilon
        return abs(float(a) - float(b)) < epsilon

#___________________________________________________________________________________________________ roundToOrder
    @classmethod
    def roundToOrder(cls, value, orderOfMagnitude, roundOp =None):
        """roundToOrder doc..."""
        if orderOfMagnitude == 0:
            return int(value)

        if roundOp is None:
            roundOp = round

        scale = math.pow(10, orderOfMagnitude)
        return scale*roundOp(float(value)/scale)

#___________________________________________________________________________________________________ roundToSigFigs
    @classmethod
    def roundToSigFigs(cls, value, digits):
        """roundTo doc..."""
        if value == 0.0:
            return 0

        value = float(value)
        d = math.ceil(math.log10(-value if value < 0  else value))
        power = digits - int(d)

        magnitude = math.pow(10, power)
        shifted = round(value*magnitude)
        return shifted/magnitude

#___________________________________________________________________________________________________ orderOfLeastSigFig
    @classmethod
    def orderOfLeastSigFig(cls, value):
        """orderOfLeastSignificantDigit doc..."""

        om = 0

        if isinstance(value, (int, long)) or long(value) == value:
            value = long(value)

            while om < 10000:
                om += 1
                magnitude = math.pow(10, -om)
                test = float(value)*magnitude
                if long(test) != test:
                    return om
            return 0

        while om < 10000:
            om -= 1
            magnitude = math.pow(10, -om)
            test = value*magnitude
            if cls.equivalent(test, int(test)):
                return om
        return 0

#___________________________________________________________________________________________________ isNumber
    @classmethod
    def isNumber(cls, value):
        """isNumber doc..."""
        return isinstance(value, (int, long, float))

#___________________________________________________________________________________________________ linearSpace
    @classmethod
    def linearSpace(cls, minVal =0, maxVal =1.0, length =10, roundToIntegers =False):
        """ Returns a list of linear-spaced values with minVal and maxVal as the boundaries with
            the specified number (length) of entries. If roundToIntegers is True, each value will
            be rounded to the nearest integer. """

        out     = []
        value   = minVal
        length  = max(2, length)
        delta   = (float(maxVal) - float(minVal))/float(length - 1.0)

        for index in range(length - 1):
            out.append(round(value) if roundToIntegers else value)
            value += delta

        out.append(round(maxVal) if roundToIntegers else maxVal)
        return out
