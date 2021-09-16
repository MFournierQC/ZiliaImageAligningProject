import envtest
from displayResult import *
from spectrumAnalysisFromDatabase import *
from processImagesFromDatabase import *
from zilia import *
import matplotlib.pyplot as plt
import numpy as np

class TestShowFinalResult(envtest.ZiliaTestCase):

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
        region = 'onh'
        # rlp = None
        rlp = 6
        # timeline = None
        timeline = 'baseline 3'
        limit = 10
        gridsize = (8,6)
        mirrorLeftEye = True

        eye = 'os'
        print('Starting left eye analysis.')
        resultImageOS, oxygenSatOS, rosaLabelsOS, _, xCoordinatesOS, yCoordinatesOS, cleanMelaninOS = self.computeResultImageForOneEye(monkey=monkey, rlp=rlp, timeline=timeline, eye=eye, limit=limit, gridsize=gridsize, mirrorLeftEye=mirrorLeftEye, region=region)
        osOxygenSatMatrix = getOxygenSatMatrix(rosaLabelsOS, oxygenSatOS, gridsize=gridsize)
        print("First eye analysis done.")

        eye = 'od'
        print('Starting right eye analysis.')
        resultImageOD, oxygenSatOD, rosaLabelsOD, _, xCoordinatesOD, yCoordinatesOD, cleanMelaninOD = self.computeResultImageForOneEye(monkey=monkey, rlp=rlp, timeline=timeline, eye=eye, limit=limit, gridsize=gridsize, mirrorLeftEye=mirrorLeftEye, region=region)
        odOxygenSatMatrix = getOxygenSatMatrix(rosaLabelsOD, oxygenSatOD, gridsize=gridsize)
        print("Second eye analysis done.")

        display(resultImageOS, resultImageOD, osOxygenSatMatrix, odOxygenSatMatrix, xCoordinatesOS, yCoordinatesOS, xCoordinatesOD, yCoordinatesOD, cleanMelaninOS, cleanMelaninOD)

    def computeResultImageForOneEye(self, monkey='Bresil', rlp=6, timeline=None, eye='os', limit=10, gridsize=(10,10), mirrorLeftEye=True, region='onh'):
        retinaImages = self.db.getGrayscaleEyeImages(monkey=monkey, rlp=rlp, timeline=timeline, region=region, eye=eye, limit=limit, mirrorLeftEye=mirrorLeftEye)
        rosaImages = self.db.getRGBImages(monkey=monkey, rlp=rlp, timeline=timeline, region=region, content='rosa', eye=eye, limit=limit, mirrorLeftEye=mirrorLeftEye)
        # dark = findDarkImages(retinaImages)

        ### Image analysis ###
        print('Starting image analysis')
        rosaAbsoluteXY = getRosaProperties(rosaImages)
        shiftValueFromReferenceImage, imageIsValid = calculateValidShiftsInOneAcquisition(retinaImages)
        rosaLocationOnRefImage = applyShiftOnRosaCenter(rosaAbsoluteXY, shiftValueFromReferenceImage)
        refImage = findRefImage(imageIsValid, retinaImages)
        xONH, yONH, onhWidth, onhHeight = findOHNParamsInRefImage(refImage)
        # length is now onhWidth, onhHeight
        gridParameters = (xONH, yONH, onhWidth, onhHeight)
        absoluteRosaValue = calculateRosaDistanceFromOnhInRefImage(xONH, yONH, rosaLocationOnRefImage)
        rosaLabels = getRosaLabels(gridParameters, rosaLocationOnRefImage, gridsize=gridsize)

        ### Spectral analysis ###
        print('Importing spectra.')
        rawSpectra = self.db.getRawIntensities(monkey=monkey, rlp=rlp, timeline=timeline, limit=limit, region=region, eye=eye)
        if rawSpectra is None:
            raise ImportError("No raw spectra was found in the database for theses input parameters.")
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        darkRefData = self.db.getBackgroundIntensities(rlp=rlp)
        darkRefData = wavelengths, darkRefData[1]
        print('Starting spectral analysis.')
        oxygenSat, saturationFlags = mainAnalysis(darkRefData, rawSpectraData, self.componentsSpectra,
                self.whiteRefPath, self.whiteRefBackground)

        print('Preparing rescaled image with grid.')
        imageRGB = makeImageRGB(refImage)
        rescaledImage, lowSliceX, lowSliceY = rescaleImage(imageRGB, gridParameters)
        resultImageWithGrid = drawGrid(rescaledImage, gridParameters, gridsize=gridsize)

        xCoordinates, yCoordinates, cleanSaturationO2, _ = cleanResultValuesAndLocation(absoluteRosaValue, lowSliceX, lowSliceY, oxygenSat, gridParameters)

        return resultImageWithGrid, oxygenSat, rosaLabels, saturationFlags, xCoordinates, yCoordinates, cleanSaturationO2

if __name__ == "__main__":
    envtest.main()
