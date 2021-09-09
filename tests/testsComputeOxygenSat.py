import envtest
from spectrumAnalysisFromDatabase import *
from zilia import *
import matplotlib.pyplot as plt
import numpy as np


# No spectra for Bresil ONH rlp24

class TestComputeOxygenSat(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertTrue(True)

    def setUp(self):
        super().setUp()
        self.db = ZiliaDB()
        self.assertIsNotNone(self.db)
        self.componentsSpectra = '../_components_spectra.csv'
        self.whiteRefPath = "../int75_WHITEREFERENCE.csv"
        self.whiteRefBackground = "../int75_LEDON_nothingInFront.csv"
        self.rlpValues = [2, 4, 6, 14, 24, 34] # rlp14 only for bresil mac in baseline 3

    @envtest.skip("long test")
    def test1_GetAllSaturationValuesFor10Spectra(self):
        monkey = 'Bresil'
        rlp = 6
        timeline = 'baseline 3'
        limit = 10
        region = 'onh'
        eye = 'os'

        oxygenSat, saturationFlags = self.computeSaturationValues(monkey=monkey, rlp=rlp, timeline=timeline, limit=limit, region=region, eye=eye)
        self.assertEqual(len(oxygenSat), limit)
        self.assertEqual(len(oxygenSat), len(saturationFlags))
        print(oxygenSat)
        print(saturationFlags)

    # @envtest.skip("long test")
    def test2_GetAllSaturationValuesFor25Spectra(self):
        monkey = 'Bresil'
        rlp = 6
        timeline = 'baseline 3'
        limit = 25
        region = 'onh'
        eye = 'os'

        oxygenSat, saturationFlags = self.computeSaturationValues(monkey=monkey, rlp=rlp, timeline=timeline, limit=limit, region=region, eye=eye)
        self.assertEqual(len(oxygenSat), limit)
        self.assertEqual(len(oxygenSat), len(saturationFlags))
        print(oxygenSat)
        print(saturationFlags)

    # @envtest.skip("long test")
    def test3_GetAllSaturationValuesFor25Spectra(self):
        monkey = 'Bresil'
        rlp = 2
        timeline = 'baseline 3'
        limit = 25
        region = 'onh'
        eye = 'os'

        oxygenSat, saturationFlags = self.computeSaturationValues(monkey=monkey, rlp=rlp, timeline=timeline, limit=limit, region=region, eye=eye)
        self.assertEqual(len(oxygenSat), limit)
        self.assertEqual(len(oxygenSat), len(saturationFlags))
        print(oxygenSat)
        print(saturationFlags)


    def computeSaturationValues(self, monkey='Bresil', rlp=6, timeline='baseline 3', limit=10, region='onh', eye='os'):
        print('Importing raw spectra.')
        rawSpectra = self.db.getRawIntensities(monkey=monkey, rlp=rlp, timeline=timeline, limit=limit, region=region, eye=eye)
        if rawSpectra is None:
            raise ImportError("No raw spectra was found in the database for theses input parameters.")
        print('Importing wavelengths.')
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        print('Importing the background.')
        darkRefData = self.db.getBackgroundIntensities(rlp=rlp)
        darkRefData = wavelengths, darkRefData[1]
        print('Starting spectral analysis.')
        oxygenSat, saturationFlags = mainAnalysis(darkRefData, rawSpectraData, self.componentsSpectra,
                self.whiteRefPath, self.whiteRefBackground)
        return oxygenSat, saturationFlags

if __name__ == "__main__":
    envtest.main()
