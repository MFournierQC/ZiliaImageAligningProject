import envtest
from spectrumAnalysisFromDatabase import *
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

    @envtest.skip("don't run systematically")
    def testGetAllSaturationValuesForSetRLP(self):
        pass

    def computeSaturationValues():
        ### Spectral analysis ###
        print('Starting spectral analysis.')
        # rawSpectra = self.db.getRawIntensities(monkey=monkey, rlp=rlp, timeline=timeline, limit=limit, region=region, eye=eye)
        rawSpectra = self.db.getRawIntensities(monkey=monkey, rlp=rlp, timeline=timeline, limit=limit)
        if rawSpectra is None:
            raise ImportError("No raw spectra was found in the database for theses input parameters.")
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        darkRefData = self.db.getBackgroundIntensities(rlp=rlp)
        darkRefData = wavelengths, darkRefData[1]
        oxygenSat, saturationFlags = mainAnalysis(darkRefData, rawSpectraData, self.componentsSpectra,
                self.whiteRefPath, self.whiteRefBackground)

if __name__ == "__main__":
    envtest.main()
