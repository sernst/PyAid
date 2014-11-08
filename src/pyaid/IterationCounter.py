# IterationCounter.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math

from pyaid.string.StringUtils import StringUtils

#___________________________________________________________________________________________________ IterationCounter
class IterationCounter(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, count, startIndex =0, majorIntervalCount =1, minorIntervalCount =0):
        """Creates a new instance of IterationCounter, which is used to monitor iteration loops"""
        self.count               = count
        self.startIndex          = startIndex
        self.index               = self.startIndex
        self.majorIntervalCount  = majorIntervalCount
        self.minorIntervalCount  = minorIntervalCount

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: prettyPrintProgress
    @property
    def prettyPrintProgress(self):
        return StringUtils.toUnicode(int(self.progress*100.0)) + '5'

#___________________________________________________________________________________________________ GS: progress
    @property
    def progress(self):
        """ Current progress value of the entire counter process. """
        return float(self.index)/float(self.count)

#___________________________________________________________________________________________________ GS: currentMajorInterval
    @property
    def currentMajorIntervalIndex(self):
        """ Current index of the major interval, i.e. which major interval is the counter currently
            within. Values will be 0 to majorIntervalCount - 1. """

        if self.isDone or self.majorIntervalCount <= 0:
            return self.majorIntervalCount

        delta = 1.0/float(self.majorIntervalCount)
        return int(math.floor(self.progress/delta))

#___________________________________________________________________________________________________ GS: currentMinorInterval
    @property
    def currentMinorIntervalIndex(self):
        """ Current index of the major interval, i.e. which major interval is the counter currently
            within. Values will be 0 to majorIntervalCount - 1. """

        if self.isDone or self.minorIntervalCount <= 0:
            return self.minorIntervalCount

        delta             = 1.0/float(self.majorIntervalCount)
        currentMajorIndex = int(math.floor(self.progress/delta))
        majorProgress     = delta*float(currentMajorIndex)
        nextMajorProgress = delta*float(currentMajorIndex + 1.0)
        minorInterval     = nextMajorProgress - majorProgress
        minorProgress     = (self.progress - majorProgress)/minorInterval
        minorDelta        = 1.0/float(self.minorIntervalCount)

        return int(math.floor(minorProgress/minorDelta))

#___________________________________________________________________________________________________ GS: isMajorInterval
    @property
    def isMajorInterval(self):
        if self.majorIntervalCount <= 0:
            return False

        if self.isDone:
            return True

        indexDelta = int(float(self.count)/float(self.majorIntervalCount))

        return self.index % indexDelta == 0

#___________________________________________________________________________________________________ GS: isMinorInterval
    @property
    def isMinorInterval(self):
        if self.minorIntervalCount <= 0:
            return False

        if self.isDone:
            return True

        majorIndexDelta = int(
            float(self.count)/float(self.majorIntervalCount*self.minorIntervalCount))

        return self.index % majorIndexDelta

#___________________________________________________________________________________________________ GS: isDone
    @property
    def isDone(self):
        return self.index + 1 >= self.count

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ increment
    def increment(self):
        """Doc..."""
        self.index += 1

#___________________________________________________________________________________________________ reset
    def reset(self):
        self.index = self.startIndex

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        return StringUtils.toUnicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
