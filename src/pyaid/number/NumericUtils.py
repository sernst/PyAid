# NumericUtils.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

#___________________________________________________________________________________________________ NumericUtils
class NumericUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

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
