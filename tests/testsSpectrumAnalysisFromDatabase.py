import envtest
from spectrumAnalysisFromDatabase import *
from zilia import *

class TestSpectrumAnalysisFromDatabase(envtest.ZiliaTestCase):

    def testImportDatabase(self):
        db = ZiliaDB()
        self.assertIsNotNone(db)

    def setUp(self):
        super().setUp()
        self.db = ZiliaDB()
        self.assertIsNotNone(self.db)

    # def testGetWavelengths(self):
    #     wavelengths = self.db.getWavelengths()
    #     self.assertIsNotNone(wavelengths)
    #     self.assertGreater(len(wavelengths), 50)

    def testGetSpectraFor10(self):
        # spectra = self.db.getRawIntensities(monkey='Rwanda', region='onh', timeline='baseline', column='raw')
        spectra = self.db.getRawIntensities()
        self.assertGreater(len(spectra), 500)
        print("spectraType =", type(spectra))
        # print(spectra)

    def testGetSpectraPathsFor10(self):
        pass

    def testGetDarkRefFor10(self):
        pass


if __name__ == '__main__':
    envtest.main()
