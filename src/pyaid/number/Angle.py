# Angle.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math

from pyaid.number.NumericUtils import NumericUtils

#*************************************************************************************************** Angle
class Angle(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of Angle."""
        self._angle = 0.0

        if 'degrees' in kwargs:
            self.degrees = kwargs.get('degrees')
        elif 'radians' in kwargs:
            self.radians = kwargs.get('radians')

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: radians
    @property
    def radians(self):
        return self._angle
    @radians.setter
    def radians(self, value):
        self._angle = value

#___________________________________________________________________________________________________ GS: degrees
    @property
    def degrees(self):
        return 180.0/math.pi*self._angle
    @degrees.setter
    def degrees(self, value):
        self._angle = math.pi/180.0*value

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ constrainToRevolution
    def constrainToRevolution(self):
        """revolvePositive doc..."""
        while self._angle < 0:
            self._angle += 2.0*math.pi
        self.degrees %= 360.0

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, NumericUtils.roundToSigFigs(self.degrees, 3))


