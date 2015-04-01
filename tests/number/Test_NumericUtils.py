# Test_NumericUtils.py [UNIT TEST]
# (C) 2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import random
import unittest
import math

from pyaid.number.NumericUtils import NumericUtils

#*************************************************************************************************** Test_NumericUtils
class Test_NumericUtils(unittest.TestCase):

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ setUp
    def setUp(self):
        pass

#___________________________________________________________________________________________________ test_isNumber
    def test_isNumber(self):
        """test_isNumber doc..."""
        self.assertTrue(NumericUtils.isNumber(1.234))
        self.assertTrue(NumericUtils.isNumber(100))
        self.assertTrue(NumericUtils.isNumber(-24))
        self.assertFalse(NumericUtils.isNumber('12'))
        self.assertFalse(NumericUtils.isNumber(self))

#___________________________________________________________________________________________________ test_linearSpace
    def test_linearSpace(self):
        """test_linearSpace doc..."""

        result = NumericUtils.linearSpace(0.0, 1.0, 10)
        self.assertTrue(len(result) == 10)
        self.assertAlmostEqual(0, result[0])
        self.assertAlmostEqual(1.0, result[-1])

        result = NumericUtils.linearSpace(-25.0, 25.0, 51)
        self.assertTrue(len(result) == 51)
        self.assertAlmostEqual(-25.0, result[0])
        self.assertAlmostEqual(25.0, result[-1])

        try:
            self.assertTrue(result.index(0.0))
        except Exception:
            self.fail('Unexpected linear spacing')

#___________________________________________________________________________________________________ test_roundToOrder
    def test_roundToOrder(self):
        """test_roundToOrder doc..."""
        self.assertAlmostEqual(123.3, NumericUtils.roundToOrder(123.345, -1))

        # Using the round operator, which rounds 5 up when odd, down when even
        self.assertAlmostEqual(123.34, NumericUtils.roundToOrder(123.345, -2))
        self.assertAlmostEqual(123.36, NumericUtils.roundToOrder(123.355, -2))

        self.assertAlmostEqual(123, NumericUtils.roundToOrder(123.345, 0))
        self.assertAlmostEqual(120, NumericUtils.roundToOrder(123.345, 1))
        self.assertAlmostEqual(100, NumericUtils.roundToOrder(123.345, 2))

#___________________________________________________________________________________________________ test_orderOfMagnitude
    def test_orderOfMagnitude(self):
        """test_orderOfMagnitude doc..."""
        testOrder = -9
        while testOrder < 10:
            for i in range(25):
                value  = random.uniform(1.0, 9.9)*math.pow(10.0, testOrder)
                result = NumericUtils.orderOfMagnitude(value)
                msg    = 'Invalid Order %s != %s (%s)' % (result, testOrder, value)
                self.assertEqual(testOrder, result,  msg)
            testOrder += 1

#___________________________________________________________________________________________________ test_equivalent
    def test_equivalent(self):
        """test_equivalent doc..."""
        self.assertTrue(NumericUtils.equivalent(1.0, 1.001, 0.01))
        self.assertFalse(NumericUtils.equivalent(1.0, 1.011, 0.01))

#___________________________________________________________________________________________________ test_sqrtSumOfSquares
    def test_sqrtSumOfSquares(self):
        """test_sqrtSumOfSquares doc..."""
        self.assertEqual(1.0, NumericUtils.sqrtSumOfSquares(-1.0))
        self.assertEqual(math.sqrt(2), NumericUtils.sqrtSumOfSquares(1.0, 1.0))
        self.assertEqual(math.sqrt(4.25), NumericUtils.sqrtSumOfSquares(2.0, 0.5))

#___________________________________________________________________________________________________ test_toValueUncertainty
    def test_toValueUncertainty(self):
        """test_toValueUncertainty doc..."""
        value = NumericUtils.toValueUncertainty(math.pi, 0.00456)
        self.assertEqual(value.value, 3.142, 'Values do not match %s' % value.label)
        self.assertEqual(value.uncertainty, 0.005, 'Uncertainties do not match %s' % value.label)

        value = NumericUtils.toValueUncertainty(100.0*math.pi, 42.0)
        self.assertEqual(value.value, 310.0, 'Values do not match %s' % value.label)
        self.assertEqual(value.uncertainty, 40.0, 'Uncertainties do not match %s' % value.label)

        value = NumericUtils.toValueUncertainty(0.001*math.pi, 0.000975)
        self.assertEqual(value.value, 0.003, 'Values do not match %s' % value.label)
        self.assertEqual(value.uncertainty, 0.001, 'Uncertainties do not match %s' % value.label)

#___________________________________________________________________________________________________ test_weightedAverage
    def test_weightedAverage(self):
        """ doc... """
        values = [
            NumericUtils.toValueUncertainty(11.0, 1.0),
            NumericUtils.toValueUncertainty(12.0, 1.0),
            NumericUtils.toValueUncertainty(10.0, 3.0) ]

        result = NumericUtils.weightedAverage(*values)

        self.assertEqual(result.value, 11.4, 'Value Match')
        self.assertEqual(result.uncertainty, 0.7, 'Value Match')

####################################################################################################
####################################################################################################

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(Test_NumericUtils)
    unittest.TextTestRunner(verbosity=2).run(suite)



