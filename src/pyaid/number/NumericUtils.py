# NumericUtils.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math
import sys

# AS NEEDED: from pyaid.number.ValueUncertainty import ValueUncertainty
from pyaid.list.ListUtils import ListUtils

if sys.version > '3':
    long = int

try:
    import numpy as np
except Exception:
    np = None

#___________________________________________________________________________________________________ NumericUtils
class NumericUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ divideValueUncertainties
    @classmethod
    def divideValueUncertainties(cls, numeratorValue, denominatorValue):
        """ Divides two ValueUncertainty instances to produce a new one with error propagation. """

        n = numeratorValue
        d = denominatorValue

        val = n.raw/d.raw
        unc = val*math.sqrt((n.rawUncertainty/n.raw)**2 + (d.rawUncertainty/d.raw)**2)
        return cls.toValueUncertainty(val, unc)

#___________________________________________________________________________________________________ multiplyValueUncertainties
    @classmethod
    def multiplyValueUncertainties(cls, a, b):
        """ Divides two ValueUncertainty instances to produce a new one with error propagation. """

        val = n.raw*d.raw
        unc = val*math.sqrt((n.rawUncertainty/n.raw)**2 + (d.rawUncertainty/d.raw)**2)
        return cls.toValueUncertainty(val, unc)

#___________________________________________________________________________________________________ weightedAverage
    @classmethod
    def weightedAverage(cls, *values):
        """ Calculates the uncertainty weighted average of the provided values, where each value
            is a ValueUncertainty instance. For mathematical formulation of the weighted average
            see "An Introduction to Error Analysis, 2nd Edition" by John R. Taylor, Chapter 7.2. """

        if not values:
            return cls.toValueUncertainty(0.0, 0.0)

        if isinstance(values[0], (list, tuple)):
            values = values[0]
            if not values:
                return cls.toValueUncertainty(0.0, 0.0)

        wxs = 0.0
        ws  = 0.0
        for v in values:
            w = 1.0/(v.uncertainty*v.uncertainty)
            wxs += w*v.value
            ws  += w

        ave = wxs/ws
        unc =  1.0/math.sqrt(ws)

        return cls.toValueUncertainty(value=ave, uncertainty=unc)

#___________________________________________________________________________________________________ orderOfMagnitude
    @classmethod
    def orderOfMagnitude(cls, value):
        """ Returns the order of magnitude of the most significant digit of the specified number.
            A value of zero signifies the ones digit, as would be the case in [Number]*10^[Order]. """

        x = abs(float(value))
        offset = 0 if x >= 1.0 else -1
        return int(math.log10(x) + offset)

#___________________________________________________________________________________________________ sqrtSumOfSquares
    @classmethod
    def sqrtSumOfSquares(cls, *args):
        """sqrtSumOfSquares doc..."""
        out = 0.0
        for arg in args:
            out += float(arg)*float(arg)
        return math.sqrt(out)

#___________________________________________________________________________________________________ equivalent
    @classmethod
    def equivalent(cls, a, b, epsilon =None, machineEpsilonFactor =100.0):
        """equivalent doc..."""
        if epsilon is None:
            epsilon = machineEpsilonFactor*sys.float_info.epsilon
        return abs(float(a) - float(b)) < epsilon

#___________________________________________________________________________________________________ roundToOrder
    @classmethod
    def roundToOrder(cls, value, orderOfMagnitude, roundOp =None, asInt =False):
        """roundToOrder doc..."""
        if roundOp is None:
            roundOp = round

        if orderOfMagnitude == 0:
            value = round(float(value))
            return int(value) if asInt else value

        scale = math.pow(10, orderOfMagnitude)
        value = scale*roundOp(float(value)/scale)
        return int(value) if asInt else value

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
                    return om - 1
            return 0

        while om < 10000:
            om -= 1
            magnitude = math.pow(10, -om)
            test = value*magnitude
            if cls.equivalent(test, int(test)):
                return om
        return 0

#___________________________________________________________________________________________________ getMeanAndDeviation
    @classmethod
    def getMeanAndDeviation(cls, values):
        """getMeanAndDeviation doc..."""
        if np is None:
            raise ImportError('NumericUtils.getMeanAndDeviation() requires Numpy')

        if not values:
            return cls.toValueUncertainty(0.0, 0.0)

        mean    = np.mean(values, dtype=np.float64)
        std     = np.std(values, dtype=np.float64)
        return cls.toValueUncertainty(mean, std)

#___________________________________________________________________________________________________ getWeightedMeanAndDeviation
    @classmethod
    def getWeightedMeanAndDeviation(cls, *values):
        """ Returns the mean and standard deviation of a weighted set of values. For further info
            see: http://stats.stackexchange.com/questions/6534/
                 how-do-i-calculate-a-weighted-standard-deviation-in-excel """

        if np is None:
            raise ImportError('NumericUtils.getMeanAndDeviation() requires Numpy')

        if not values:
            return cls.toValueUncertainty(0.0, 0.0)

        if isinstance(values[0], (list, tuple)):
            values = values[0]
            if not values:
                return cls.toValueUncertainty(0.0, 0.0)

        if len(values) == 1:
            return values[0].clone()

        wxs = 0.0
        ws  = 0.0
        weights = []

        for v in values:
            w = 1.0/(v.uncertainty*v.uncertainty)
            weights.append(w)
            wxs += w*v.value
            ws  += w

        ave = wxs/ws
        dev = 0.0
        N = len(values)
        for i in ListUtils.range(N):
            dev += weights[i]*(values[i].value - ave)**2

        denom = ws*(N - 1.0)/N
        dev = math.sqrt(dev/denom)

        return cls.toValueUncertainty(value=ave, uncertainty=dev)

#___________________________________________________________________________________________________ toValueUncertainty
    @classmethod
    def toValueUncertainty(cls, value, uncertainty, asciiLabel =False):
        """toValueUncertaintyString doc..."""
        from pyaid.number.ValueUncertainty import ValueUncertainty
        return ValueUncertainty(value=value, uncertainty=uncertainty, asciiLabels=asciiLabel)

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
