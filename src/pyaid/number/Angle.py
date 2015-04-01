# Angle.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math

from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils

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
        self._angle = float(value)

#___________________________________________________________________________________________________ GS: degrees
    @property
    def degrees(self):
        return math.degrees(self._angle)
    @degrees.setter
    def degrees(self, value):
        self._angle = math.radians(float(value))

#___________________________________________________________________________________________________ GS: prettyPrint
    @property
    def prettyPrint(self):
        return StringUtils.toText(NumericUtils.roundToSigFigs(self.degrees, 3))

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ constrainToRevolution
    def constrainToRevolution(self):
        """ Constrains the angle to within the bounds [0, 360] by removing revolutions. """
        self.radians = self.constrainAngleToRevolution(self.radians)

#___________________________________________________________________________________________________ differenceBetween
    def differenceBetween(self, angle):
        """ Returns a new Angle instance that is the smallest difference between this angle the
            one specified in the arguments. """

        a = self.constrainAngleToRevolution(self.radians)
        b = self.constrainAngleToRevolution(angle.radians)

        result = math.degrees(a - b)
        return Angle(degrees=((result + 180.0) % 360.0) - 180.0)

#___________________________________________________________________________________________________ constrainAngleToRevolution
    @classmethod
    def constrainAngleToRevolution(cls, radians):
        """constrainAngleToRevolution doc..."""
        while radians < 0:
            radians += 2.0*math.pi
        degrees = math.degrees(radians) % 360.0
        return math.radians(degrees)

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, NumericUtils.roundToSigFigs(self.degrees, 3))


