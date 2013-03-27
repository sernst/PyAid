# FloatUtils.py
# (C)2012
# Scott Ernst

import random

#___________________________________________________________________________________________________ FloatUtils
class FloatUtils(object):
    """A class for integer related operations."""

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ jitter
    @staticmethod
    def jitter(nominal, deviation =0.25):
        """Returns a float that is randomly jittered by the specified deviation.

        @@@param nominal:float
            The normal value around which to jitter.

        @@@param deviation:float
            Fractional value specifying the max or min deviation from nominal.

        @@@returns float
            The jittered value.
        """

        return random.uniform((1.0 - deviation)*nominal, (1.0 + deviation)*nominal)
