# ValueUncertainty.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

import sys
import math

from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils

#*******************************************************************************
class ValueUncertainty(object):
    """A class for..."""

    #___________________________________________________________________________
    def __init__(self, value =0.0, uncertainty =1.0, **kwargs):
        """Creates a new instance of ValueUncertainty."""
        self._raw            = float(value)
        self._rawUncertainty = abs(float(uncertainty))
        self._asciiLabels    = kwargs.get('asciiLabels', False)

#===============================================================================
#                                                                 G E T / S E T

    #___________________________________________________________________________
    @property
    def asciiLabels(self):
        return self._asciiLabels

    #___________________________________________________________________________
    @property
    def raw(self):
        return self._raw

    #___________________________________________________________________________
    @property
    def rawUncertainty(self):
        return self._rawUncertainty

    #___________________________________________________________________________
    @property
    def value(self):
        uncertainty = self.uncertainty
        order       = NumericUtils.orderOfLeastSigFig(uncertainty)
        return NumericUtils.roundToOrder(self._raw, order)

    #___________________________________________________________________________
    @property
    def uncertainty(self):
        return NumericUtils.roundToSigFigs(abs(self._rawUncertainty), 1)

    #___________________________________________________________________________
    @property
    def label(self):
        if self._asciiLabels:
            return self.asciiLabel
        return '%s %s %s' % (
            self.value,
            StringUtils.unichr(0x00B1),
            self.uncertainty)

    #___________________________________________________________________________
    @property
    def rawLabel(self):
        if self._asciiLabels:
            return self.asciiRawLabel
        return '%s %s %s' % (
            NumericUtils.roundToSigFigs(self.raw, 6),
            StringUtils.unichr(0x00B1),
            self.uncertainty)

    #___________________________________________________________________________
    @property
    def asciiLabel(self):
        return '%s +/- %s' % (self.value, self.uncertainty)

    #___________________________________________________________________________
    @property
    def asciiRawLabel(self):
        return '%s +/- %s' % (
            NumericUtils.roundToSigFigs(self.raw, 6),
            self.uncertainty)

#===============================================================================
#                                                                   P U B L I C

    #___________________________________________________________________________
    def clone(self):
        """clone doc..."""
        return ValueUncertainty(
            value=self._raw,
            uncertainty=self._rawUncertainty,
            asciiLabels=self._asciiLabels)

    #___________________________________________________________________________
    def update(self, value =None, uncertainty =None):
        """update doc..."""

        if value is not None:
            self._raw = value

        if uncertainty is not None:
            self._rawUncertainty = uncertainty

    #___________________________________________________________________________
    @classmethod
    def createRandom(cls, minVal =-1.0, maxVal =1.0, minUnc =0.1, maxUnc =2.0):
        """createRandom doc..."""
        return ValueUncertainty(
            value=random.uniform(minVal, maxVal),
            uncertainty=random.uniform(minUnc, maxUnc))

#===============================================================================
#                                                             I N T R I N S I C

    #___________________________________________________________________________
    def __pow__(self, power, modulo=None):
        val = self.raw**power
        unc = abs(val*float(power)*self.rawUncertainty/self.raw)
        return ValueUncertainty(val, unc)

    #___________________________________________________________________________
    def __add__(self, other):
        try:
            val = self.raw + other.raw
            unc = math.sqrt(self.rawUncertainty**2 + other.rawUncertainty**2)
        except Exception:
            val = float(other) + self.raw
            unc = self.rawUncertainty

        return ValueUncertainty(val, unc)

    #___________________________________________________________________________
    def __radd__(self, other):
        return self.__add__(other)

    #___________________________________________________________________________
    def __sub__(self, other):
        try:
            val = self.raw - other.raw
            unc = math.sqrt(self.rawUncertainty**2 + other.rawUncertainty**2)
        except Exception:
            val = self.raw - float(other)
            unc = self.rawUncertainty

        return ValueUncertainty(val, unc)

    #___________________________________________________________________________
    def __rsub__(self, other):
        return self.__sub__(other)

    #___________________________________________________________________________
    def __mul__(self, other):
        try:
            val = self.raw*other.raw
            unc = abs(val)*math.sqrt(
                (self.rawUncertainty/self.raw)**2 +
                (other.rawUncertainty/other.raw)**2)
        except Exception:
            val = float(other)*self.raw
            unc = abs(float(other)*self.rawUncertainty)

        return ValueUncertainty(val, unc)

    #___________________________________________________________________________
    def __rmul__(self, other):
        return self.__mul__(other)

    #___________________________________________________________________________
    def __truediv__(self, other):
        try:
            val = self.raw/other.raw
            unc = abs(val)*math.sqrt(
                (self.rawUncertainty/self.raw)**2 +
                (other.rawUncertainty/other.raw)**2)
        except Exception:
            val = self.raw/float(other)
            unc = abs(self.rawUncertainty/float(other))

        return ValueUncertainty(val, unc)

    #___________________________________________________________________________
    def __rtruediv__(self, other):
        return self.__truediv__(other)

    #___________________________________________________________________________
    def __div__(self, other):
        return self.__truediv__(other)

    #___________________________________________________________________________
    def __rdiv__(self, other):
        return self.__rtruediv__(other)

    #___________________________________________________________________________
    def __repr__(self):
        return self.__str__()

    #___________________________________________________________________________
    def __unicode__(self):
        """__unicode__ doc..."""
        label = self.asciiLabel if sys.version < '3' else self.label
        return '<%s %s>' % (self.__class__.__name__, label)

    #___________________________________________________________________________
    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.asciiLabel)

