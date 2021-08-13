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

    def testGetMainAnalysisOnRetinaImagesForBresilOS(self):
        ### Retina image analysis ###
        eye='os'
        retinaImages = self.db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh', eye=eye , limit=10)
        rosaImages = self.db.getRGBImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh', content='rosa', eye=eye , limit=10)
        # dark = findDarkImages(retinaImages)
        rosaAbsoluteXY=getRosaProperties(rosaImages)
        # useful info:  int(['center']['x']) , int(['center']['y']) , ['rradius'] , and ['found']
        shiftValueFromReferenceImage , imageIsValid = calculateValidShiftsInOneAcquisition(retinaImages)
        rosaLocationOnRefImage = applyShiftOnRosaCenter(rosaAbsoluteXY, shiftValueFromReferenceImage)
        # print(imageIsValid)
        refImage = findRefImage(imageIsValid, retinaImages)
        xONH, yONH, length = findOHNParamsInRefImage(refImage)
        absoluteRosaValue = calculateRosaDistanceFromOnhInRefImage(xONH, yONH , rosaLocationOnRefImage)
        # print("absoluteRosaValue =", absoluteRosaValue)

        firstImageIndex = 0
        for i, value in enumerate(imageIsValid):
            if value is not None:
                firstImageIndex = i
                break
        # print(firstImageIndex)

        ### Spectral analysis ###
        rawSpectra = self.db.getRawIntensities(rlp=6, limit=10)
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        darkRefData = self.db.getBackgroundIntensities(rlp=6)
        darkRefData = wavelengths, darkRefData[1]
        melaninValues, saturationFlags = getMelaninValues(darkRefData, rawSpectraData, self.componentsSpectra,
                self.whiteRefPath, self.whiteRefBackground)

        resultOS = plotResult(retinaImages[firstImageIndex], absoluteRosaValue, (xONH, yONH, length), melaninValues, leftEye=True)
        plt.imshow(resultOS)
        plt.show()

        # firstSO2Matrix = matrixSO2(melaninValues, saturationFlags, leftEye=False)
        # print(firstSO2Matrix)

        # display(resultOS, secondEye, firstSO2Matrix, secondSO2Matrix)

if __name__ == "__main__":
    envtest.main()
