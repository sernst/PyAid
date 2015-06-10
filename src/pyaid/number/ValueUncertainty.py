# ValueUncertainty.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sys

from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils

#*************************************************************************************************** ValueUncertainty
class ValueUncertainty(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, value =0.0, uncertainty =1.0, **kwargs):
        """Creates a new instance of ValueUncertainty."""
        self._raw            = float(value)
        self._rawUncertainty = abs(float(uncertainty))
        self._asciiLabels    = kwargs.get('asciiLabels', False)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: asciiLabels
    @property
    def asciiLabels(self):
        return self._asciiLabels

#___________________________________________________________________________________________________ GS: raw
    @property
    def raw(self):
        return self._raw

#___________________________________________________________________________________________________ GS: rawUncertainty
    @property
    def rawUncertainty(self):
        return self._rawUncertainty

#___________________________________________________________________________________________________ GS: value
    @property
    def value(self):
        uncertainty = self.uncertainty
        order       = NumericUtils.orderOfLeastSigFig(uncertainty)
        return NumericUtils.roundToOrder(self._raw, order)

#___________________________________________________________________________________________________ GS: uncertainty
    @property
    def uncertainty(self):
        return NumericUtils.roundToSigFigs(abs(self._rawUncertainty), 1)

#___________________________________________________________________________________________________ GS: label
    @property
    def label(self):
        if self._asciiLabels:
            return self.asciiLabel
        return '%s %s %s' % (self.value, StringUtils.unichr(0x00B1), self.uncertainty)

#___________________________________________________________________________________________________ GS: label
    @property
    def rawLabel(self):
        if self._asciiLabels:
            return self.asciiRawLabel
        return '%s %s %s' % (
            NumericUtils.roundToSigFigs(self.raw, 6),
            StringUtils.unichr(0x00B1),
            self.uncertainty)

#___________________________________________________________________________________________________ GS: asciiLabel
    @property
    def asciiLabel(self):
        return '%s +/- %s' % (self.value, self.uncertainty)

#___________________________________________________________________________________________________ GS: asciiLabel
    @property
    def asciiRawLabel(self):
        return '%s +/- %s' % (NumericUtils.roundToSigFigs(self.raw, 6), self.uncertainty)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ clone
    def clone(self):
        """clone doc..."""
        return ValueUncertainty(
            value=self._raw,
            uncertainty=self._rawUncertainty,
            asciiLabels=self._asciiLabels)

#___________________________________________________________________________________________________ update
    def update(self, value =None, uncertainty =None):
        """update doc..."""

        if value is not None:
            self._raw = value

        if uncertainty is not None:
            self._rawUncertainty = uncertainty

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        """__unicode__ doc..."""
        label = self.asciiLabel if sys.version < '3' else self.label
        return '<%s %s>' % (self.__class__.__name__, label)

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.asciiLabel)

