import envtest
from displayResult import *
# from zilia import *
import matplotlib.pyplot as plt
import numpy as np

class TestMatrixSO2(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertTrue(True)

    # def setUp(self):
    #     super().setUp()
    #     self.db = ZiliaDB()
    #     self.assertIsNotNone(self.db)
    #     self.componentsSpectra = '../_components_spectra.csv'
    #     self.whiteRefPath = "../int75_WHITEREFERENCE.csv"
    #     self.whiteRefBackground = "../int75_LEDON_nothingInFront.csv"

    def testMatrixSO2WithDifferentSaturations(self):
        labels = [(0,0), (1,0)]
        saturationValues = [49, -78]
        self.assertEqual(len(labels), len(saturationValues))
        concentrationMatrix = matrixSO2(labels, saturationValues, leftEye=False, gridsize=(2,2))
        self.assertEqual(concentrationMatrix[0,0], 49)
        self.assertEqual(concentrationMatrix[0,1], -78)
        self.assertEqual(concentrationMatrix[1,0], 0)
        self.assertEqual(concentrationMatrix[1,1], 0)

    def testMatrixSO2WithDifferentSaturationsInSameLocation(self):
        labels = [(0,0), (0,0)]
        saturationValues = [2, 1]
        self.assertEqual(len(labels), len(saturationValues))
        concentrationMatrix = matrixSO2(labels, saturationValues, leftEye=False, gridsize=(2,2))
        self.assertEqual(concentrationMatrix[0,0], 1.5)
        self.assertEqual(concentrationMatrix[1,0], 0)
        self.assertEqual(concentrationMatrix[0,1], 0)
        self.assertEqual(concentrationMatrix[1,1], 0)

    def testMatrixSO2WithLeftEye(self):
        labels = [(0,0), (1,0)]
        saturationValues = [49, -78]
        self.assertEqual(len(labels), len(saturationValues))
        concentrationMatrix = matrixSO2(labels, saturationValues, leftEye=True, gridsize=(2,2))
        self.assertEqual(concentrationMatrix[0,1], 49)
        self.assertEqual(concentrationMatrix[0,0], -78)
        self.assertEqual(concentrationMatrix[1,0], 0)
        self.assertEqual(concentrationMatrix[1,1], 0)

if __name__ == "__main__":
    envtest.main()
