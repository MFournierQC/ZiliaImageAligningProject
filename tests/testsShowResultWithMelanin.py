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

    # @envtest.skip("long test")
    def testGetMainAnalysisOnRetinaImagesForBresil(self):
        monkey = 'Bresil'
        rlp = None
        # rlp = 24
        timeline = None
        # timeline = 'baseline 3'
        limit = 10
        gridsize = (10,10)
        mirrorLeftEye = False

        eye='os'
        resultImageOS, oxygenSatOS, rosaLabelsOS, _, xCoordinatesOS, yCoordinatesOS, cleanMelaninOS = self.computeResultImageForOneEye(monkey=monkey, rlp=rlp, timeline=timeline, eye=eye, limit=limit, gridsize=gridsize, mirrorLeftEye=mirrorLeftEye)
        osOxygenSatMatrix = matrixSO2(rosaLabelsOS, oxygenSatOS, leftEye=False, gridsize=gridsize)
        print("First eye analysis done.")

        eye = 'od'
        resultImageOD, oxygenSatOD, rosaLabelsOD, _, xCoordinatesOD, yCoordinatesOD, cleanMelaninOD = self.computeResultImageForOneEye(monkey=monkey, rlp=rlp, timeline=timeline, eye=eye, limit=limit, gridsize=gridsize, mirrorLeftEye=mirrorLeftEye)
        odOxygenSatMatrix = matrixSO2(rosaLabelsOD, oxygenSatOD, leftEye=False, gridsize=gridsize)
        print("Second eye analysis done.")

        display(resultImageOS, resultImageOD, osOxygenSatMatrix, odOxygenSatMatrix, xCoordinatesOS, yCoordinatesOS, xCoordinatesOD, yCoordinatesOD, cleanMelaninOS, cleanMelaninOD, mirrorLeftEye=mirrorLeftEye)

    def computeResultImageForOneEye(self, monkey='Bresil', rlp=6, timeline=None, eye='os', limit=10, gridsize=(10,10), mirrorLeftEye=True):
        if eye == 'os' and mirrorLeftEye:
            leftEye = True
        else:
            leftEye = False
        retinaImages = self.db.getGrayscaleEyeImages(monkey=monkey, rlp=rlp, timeline=timeline, region='onh', eye=eye, limit=limit, mirrorLeftEye=mirrorLeftEye)
        rosaImages = self.db.getRGBImages(monkey=monkey, rlp=rlp, timeline=timeline, region='onh', content='rosa', eye=eye, limit=limit, mirrorLeftEye=mirrorLeftEye)
        # dark = findDarkImages(retinaImages)

        ### Image analysis ###
        print('Starting image analysis')
        rosaAbsoluteXY = getRosaProperties(rosaImages)
        shiftValueFromReferenceImage, imageIsValid = calculateValidShiftsInOneAcquisition(retinaImages)
        rosaLocationOnRefImage = applyShiftOnRosaCenter(rosaAbsoluteXY, shiftValueFromReferenceImage)
        refImage = findRefImage(imageIsValid, retinaImages)
        xONH, yONH, length = findOHNParamsInRefImage(refImage)
        absoluteRosaValue = calculateRosaDistanceFromOnhInRefImage(xONH, yONH, rosaLocationOnRefImage)
        rosaLabels = getRosaLabels((xONH, yONH, length), rosaLocationOnRefImage, gridsize=gridsize)

        ### Spectral analysis ###
        print('Starting spectral analysis.')
        rawSpectra = self.db.getRawIntensities(monkey=monkey, rlp=rlp, timeline=timeline, limit=limit)
        if rawSpectra is None:
            raise ImportError("No raw spectra was found.")
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        darkRefData = self.db.getBackgroundIntensities(rlp=rlp)
        darkRefData = wavelengths, darkRefData[1]
        oxygenSat, saturationFlags = mainAnalysis(darkRefData, rawSpectraData, self.componentsSpectra,
                self.whiteRefPath, self.whiteRefBackground)

        gridParameters = (xONH, yONH, length)
        imageRGB = makeImageRGB(refImage)
        rescaledImage, lowSliceX, lowSliceY = rescaleImage(imageRGB, gridParameters)
        resultImageWithGrid = drawGrid(rescaledImage, gridParameters)
        if leftEye:
            resultImage = resultImageWithGrid[:,::-1]
        else:
            resultImage = resultImageWithGrid

        xCoordinates, yCoordinates, cleanSaturationO2, _ = cleanResultValuesAndLocation(absoluteRosaValue, lowSliceX, lowSliceY, oxygenSat, gridParameters)

        return resultImage, oxygenSat, rosaLabels, saturationFlags, xCoordinates, yCoordinates, cleanSaturationO2

if __name__ == "__main__":
    envtest.main()
