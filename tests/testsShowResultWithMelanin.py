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

if __name__ == "__main__":
    envtest.main()
