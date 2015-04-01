# Test_Angle.py [UNIT TEST]
# (C) 2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import unittest
import random

from pyaid.number.Angle import Angle

#*************************************************************************************************** Test_Angle
class Test_Angle(unittest.TestCase):

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ setUp
    def setUp(self):
        pass

#___________________________________________________________________________________________________ test_degrees
    def test_degrees(self):
        """ doc... """
        for i in range(100):
            value = random.uniform(-2000.0, 5000.0)
            a = Angle(degrees=value)
            self.assertAlmostEqual(a.degrees, value)

        for i in range(100):
            value = random.uniform(-2000.0, 5000.0)
            a = Angle()
            a.degrees = value
            self.assertAlmostEqual(a.degrees, value)

#___________________________________________________________________________________________________ test_radians
    def test_radians(self):
        """test_radians doc..."""
        for i in range(100):
            value = random.uniform(-2000.0, 5000.0)
            a = Angle(radians=value)
            self.assertAlmostEqual(a.radians, value)

        for i in range(100):
            value = random.uniform(-2000.0, 5000.0)
            a = Angle()
            a.radians = value
            self.assertAlmostEqual(a.radians, value)

#___________________________________________________________________________________________________ test_constrainToRevolution
    def test_constrainToRevolution(self):
        """test_revolvePositive doc..."""

        for i in range(100):
            value = random.uniform(-2000.0, 5000.0)
            a = Angle(degrees=value)
            a.constrainToRevolution()
            self.assertLessEqual(a.degrees, 360.0)
            self.assertGreaterEqual(a.degrees, 0.0)

#___________________________________________________________________________________________________ test_differenceBetween
    def test_differenceBetween(self):
        """test_differenceBetween doc..."""

        for i in range(1000):
            value = random.uniform(-2000.0, 5000.0)
            a = Angle(degrees=value)
            a.constrainToRevolution()

            value = random.uniform(-2000.0, 5000.0)
            b = Angle(degrees=value)
            b.constrainToRevolution()
            self.assertLessEqual(abs(a.differenceBetween(b).degrees), 180.0)

####################################################################################################
####################################################################################################

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(Test_Angle)
    unittest.TextTestRunner(verbosity=2).run(suite)
