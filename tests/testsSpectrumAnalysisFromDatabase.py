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
        self.componentsSpectra = '../_components_spectra.csv'
        self.whiteRefPath = "../int75_WHITEREFERENCE.csv"
        self.whiteRefBackground = "../int75_LEDON_nothingInFront.csv"

    def testGetWavelengths(self):
        wavelengths = self.db.getWavelengths()
        self.assertIsNotNone(wavelengths)
        self.assertEqual(len(wavelengths), 512)

    def testGetSpectraFor10(self):
        spectra = self.db.getRawIntensities(rlp=6, limit=10)
        wavelengths = self.db.getWavelengths()
        self.assertIsNotNone(spectra)
        self.assertEqual(len(spectra.shape), 2)
        self.assertEqual(spectra.shape[0], len(wavelengths))
        self.assertEqual(spectra.shape[1], 10)

    def testGetBackgroundForRlp6(self):
        backWavelengths, background = self.db.getBackgroundIntensities(rlp=6)
        self.assertIsNotNone(backWavelengths)
        self.assertIsNotNone(background)
        # print(backWavelengths)
        # print(background.shape)
        # print(backWavelengths.shape)
        self.assertEqual(len(backWavelengths), 512)
        self.assertEqual(len(backWavelengths), len(background))
        wavelengths = self.db.getWavelengths()
        self.assertEqual(background.shape[0], len(wavelengths))
        self.assertEqual(len(background.squeeze().shape), 2)
        self.assertEqual(len(backWavelengths.squeeze().shape), 1)

    def testLoadWhiteReference(self):
        whiteRefData = loadWhiteRef(self.whiteRefPath, self.whiteRefBackground)
        self.assertIsNotNone(whiteRefData)
        self.assertEqual(len(whiteRefData), 3)
        for elem in whiteRefData:
            self.assertIsNotNone(elem)
        wavelengths, spectra, background = whiteRefData
        # print(wavelengths)
        self.assertEqual(len(wavelengths), 512)
        self.assertEqual(len(spectra.squeeze().shape), 2)
        self.assertEqual(len(background.squeeze().shape), 2)

    def testFormatWhiteRef(self):
        whiteRefData = loadWhiteRef(self.whiteRefPath, self.whiteRefBackground)
        whiteRef = formatWhiteRef(whiteRefData)
        self.assertIsNotNone(whiteRef)
        whiteRefSpectrum = whiteRef.data
        whiteRefWave = whiteRef.wavelength
        self.assertIsNotNone(whiteRefSpectrum)
        self.assertIsNotNone(whiteRefWave)
        self.assertEqual(len(whiteRefSpectrum.squeeze().shape), 1)
        self.assertEqual(len(whiteRefWave.squeeze().shape), 1)
        self.assertGreater(len(whiteRefWave), 0)
        self.assertEqual(len(whiteRefSpectrum.squeeze().shape), len(whiteRefWave.squeeze().shape))

    def testFormatDarkRef(self):
        darkRefData = self.db.getBackgroundIntensities(rlp=6)
        darkRef = formatDarkRef(darkRefData)
        self.assertIsNotNone(darkRef)
        darkRefSpectrum = darkRef.data
        darkRefWave = darkRef.wavelength
        self.assertIsNotNone(darkRefSpectrum)
        self.assertIsNotNone(darkRefWave)
        self.assertEqual(len(darkRefSpectrum.squeeze().shape), 1)
        self.assertEqual(len(darkRefWave.squeeze().shape), 1)
        self.assertGreater(len(darkRefWave), 0)
        self.assertEqual(len(darkRefSpectrum), len(darkRefWave))

    def testFormatSpectra(self):
        rawSpectra = self.db.getRawIntensities(rlp=6, limit=10)
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        spectra = formatSpectra(rawSpectraData)
        self.assertIsNotNone(spectra)
        spectraData = spectra.data
        spectraWave = spectra.wavelength
        self.assertIsNotNone(spectraData)
        self.assertIsNotNone(spectraWave)
        self.assertEqual(len(spectraData.squeeze().shape), 2)
        self.assertEqual(len(spectraWave.squeeze().shape), 1)
        for shape in spectraData.squeeze().shape:
            self.assertGreater(shape, 0)
        self.assertGreater(len(spectraWave), 0)
        self.assertEqual(spectraData.shape[0], len(spectraWave))

    def testMainSpectrumAnalysisRlp6(self):
        pass

if __name__ == '__main__':
    envtest.main()
