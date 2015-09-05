# Test_ValueUncertainty.py [UNIT TEST]
# (C) 2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

import math
import unittest

#*******************************************************************************
from pyaid.number.ValueUncertainty import ValueUncertainty


class Test_ValueUncertainty(unittest.TestCase):

#===============================================================================
#                                                                     C L A S S

#_______________________________________________________________________________
    def setUp(self):
        pass

#_______________________________________________________________________________
    def test_arithmetic(self):
        """ This test is from a problem in Taylor's Error Analysis 3.9 (p. 68)
        """
        l = ValueUncertainty(92.95, 0.1)
        T = ValueUncertainty(1.936, 0.004)

        g = 4.0*(math.pi**2)*l/(T**2)

        self.assertAlmostEqual(g.value, 979.0)
        self.assertAlmostEqual(g.uncertainty, 4.0)

################################################################################
################################################################################

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(Test_ValueUncertainty)
    unittest.TextTestRunner(verbosity=2).run(suite)



