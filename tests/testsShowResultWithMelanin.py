import envtest
from displayResult import *
from spectrumAnalysisFromDatabase import *

class TestShowResultWithMelanin(envtest.TestCase):

    def testInit(self):
        self.assertTrue(True)

    def setUp(self):
        super().setUp()
        self.db = ZiliaDB()
        self.assertIsNotNone(self.db)
        self.componentsSpectra = '../_components_spectra.csv'
        self.whiteRefPath = "../int75_WHITEREFERENCE.csv"
        self.whiteRefBackground = "../int75_LEDON_nothingInFront.csv"

    def testGetMelaninCoeffs(self):
        pass

    def testGetMainAnalysisOnRetinaImages(self):
        eye='os'
        retinaImages = self.db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh', eye=eye , limit= 10)
        rosaImages = slef.db.getRGBImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh', content='rosa', eye=eye , limit = 10)

        # dark = findDarkImages(retinaImages)

        rosaAbsoluteXY=getRosaProperties(rosaImages)
        # useful info:  int(['center']['x']) , int(['center']['y']) , ['rradius'] , and ['found']

        shiftValueFromReferenceImage , imageIsValid = calculateValidShiftsInOneAcquisition(retinaImages)

        rosaLocationOnRefImage = applyShiftOnRosaCenter(rosaAbsoluteXY,shiftValueFromReferenceImage)

        print(imageIsValid)
        refImage = findRefImage(imageIsValid , retinaImages)

        xONH,yONH,length = findOHNParamsInRefImage(refImage)

        absoluteRosaValue = calculateRosaDistanceFromOnhInRefImage (xONH, yONH , rosaLocationOnRefImage)

if __name__ == "__main__":
    envtest.main()
