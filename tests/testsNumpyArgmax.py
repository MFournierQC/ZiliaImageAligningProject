import numpy as np
import unittest

class TestNumpyArgmax(unittest.TestCase):

    def testInit(self):
        self.assertTrue(True)

    def testArgmaxWithList(self):
        # I expect it to return the index of the biggest number in the list.
        data = [1,2,6,777,5,3,45]
        maxi = np.argmax(data)
        # print(max)
        self.assertTrue(maxi == 3)

    def testArgmaxWith2DMatrix(self):
        # Let's see if it's the same with a 2D array
        data = np.array([[14,123],[45,132],[789,132]])
        # print(matrix)
        # I expect to get (2,0), but it's not the case...
        maxi = np.argmax(data)
        self.assertTrue(maxi == 4)
        # print(maxi)

    def testArgmaxWith2DMatrixAndUnravelIndex(self):
        # Let's try to use unravel_index to get the right indexes
        data = np.array([[14,123],[45,132],[789,132]])
        maxi = np.argmax(data)
        realMax = np.unravel_index(maxi, data.shape)
        # print(realMax)
        self.assertTrue(realMax == (2,0))
        # YES!!! Now I get what I originally expected!!!

    def testArgmaxWithListAndUnravelIndex(self):
        # Let's see how the index unraveling would work with a list
        data = [1,2,6,777,5,3,45]
        maxi = np.argmax(data)
        realMax = np.unravel_index(maxi, len(data))
        # print(realMax)
        self.assertTrue(realMax == (3,))
        # Ok. It doesn't hurt to always unravel the index, but it's
        # useless for a 1D list.


if __name__ == "__main__":
    unittest.main()
