import envtest
from spectrumAnalysisFromDatabase import *
from zilia import *

componentsSpectra = '.._components_spectra.csv'
whiteRefPath = "..int75_WHITEREFERENCE.csv"
whiteRefBackground = "..int75_LEDON_nothingInFront.csv"

class TestSpectrumAnalysisFromDatabase(envtest.ZiliaTestCase):

    def testImportDatabase(self):
        db = ZiliaDB()
        self.assertIsNotNone(db)

    def setUp(self):
        super().setUp()
        self.db = ZiliaDB()
        self.assertIsNotNone(self.db)

    def testGetWavelengths(self):
        wavelengths = self.db.getWavelengths()
        self.assertIsNotNone(wavelengths)
        self.assertEqual(len(wavelengths), 512)

    def testGetSpectraFor10(self):
        spectra = self.db.getRawIntensities(rlp=6, limit=10)
        wavelengths = self.db.getWavelengths()
        self.assertIsNotNone(spectra)
        self.assertEqual(spectra.shape[0], len(wavelengths))
        self.assertEqual(spectra.shape[1], 10)

    def testBackgroundForRlp6(self):
        background, backWavelengths = self.db.getBackgroundIntensities(rlp=6)
        wavelengths = self.db.getWavelengths()
        self.assertIsNotNone(background)
        self.assertEqual(background.shape[0], len(wavelengths))

    def testMainSpectrumAnalysisRlp6(self):
        pass


if __name__ == '__main__':
    envtest.main()
