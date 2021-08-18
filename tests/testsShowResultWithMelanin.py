import envtest
from displayResult import *
from spectrumAnalysisFromDatabase import *
from processImagesFromDatabase import *
from zilia import *
import matplotlib.pyplot as plt
import numpy as np

class TestShowResultWithMelanin(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertTrue(True)

    def setUp(self):
        super().setUp()
        self.db = ZiliaDB()
        self.assertIsNotNone(self.db)
        self.componentsSpectra = '../_components_spectra.csv'
        self.whiteRefPath = "../int75_WHITEREFERENCE.csv"
        self.whiteRefBackground = "../int75_LEDON_nothingInFront.csv"

    def testGetMainAnalysisOnRetinaImagesForBresil(self):
        monkey = 'Bresil'
        rlp = None
        # timeline = 'baseline 3'
        timeline = None
        limit = 15
        gridsize = (10,10)

        eye='os'
        resultImageOS, melaninValuesOS, rosaLabelsOS, _ = self.computeResultImageForOneEye(monkey=monkey, rlp=rlp, timeline=timeline, eye=eye, limit=limit, gridsize=gridsize)
        osOxygenSatMatrix = matrixSO2(rosaLabelsOS, melaninValuesOS, leftEye=True)

        eye = 'od'
        resultImageOD, melaninValuesOD, rosaLabelsOD, _ = self.computeResultImageForOneEye(monkey=monkey, rlp=rlp, timeline=timeline, eye=eye, limit=limit, gridsize=gridsize)
        odOxygenSatMatrix = matrixSO2(rosaLabelsOD, melaninValuesOD, leftEye=False)

        display(resultImageOS, resultImageOD, osOxygenSatMatrix, odOxygenSatMatrix)

    def computeResultImageForOneEye(self, monkey='Bresil', rlp=6, timeline=None, eye='os', limit=10, gridsize=(10,10)):
        if eye == 'os':
            leftEye = True
        else:
            leftEye = False
        retinaImages = self.db.getGrayscaleEyeImages(monkey=monkey, rlp=rlp, timeline=timeline, region='onh', eye=eye , limit=limit)
        rosaImages = self.db.getRGBImages(monkey=monkey, rlp=rlp, timeline=timeline, region='onh', content='rosa', eye=eye , limit=limit)
        # dark = findDarkImages(retinaImages)

        ### Retina image analysis ###
        rosaAbsoluteXY = getRosaProperties(rosaImages)
        shiftValueFromReferenceImage, imageIsValid = calculateValidShiftsInOneAcquisition(retinaImages)
        rosaLocationOnRefImage = applyShiftOnRosaCenter(rosaAbsoluteXY, shiftValueFromReferenceImage)
        refImage = findRefImage(imageIsValid, retinaImages)
        xONH, yONH, length = findOHNParamsInRefImage(refImage)
        absoluteRosaValue = calculateRosaDistanceFromOnhInRefImage(xONH, yONH, rosaLocationOnRefImage)
        rosaLabels = getRosaLabels((xONH, yONH, length), rosaLocationOnRefImage, gridsize=gridsize)

        ### Spectral analysis ###
        rawSpectra = self.db.getRawIntensities(monkey=monkey, rlp=rlp, timeline=timeline, limit=limit)
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        darkRefData = self.db.getBackgroundIntensities(rlp=rlp)
        darkRefData = wavelengths, darkRefData[1]
        melaninValues, saturationFlags = getMelaninValues(darkRefData, rawSpectraData, self.componentsSpectra,
                self.whiteRefPath, self.whiteRefBackground)

        resultImage = plotResult(refImage, absoluteRosaValue, (xONH, yONH, length), melaninValues, leftEye=True)
        return resultImage, melaninValues, rosaLabels, saturationFlags

if __name__ == "__main__":
    envtest.main()
