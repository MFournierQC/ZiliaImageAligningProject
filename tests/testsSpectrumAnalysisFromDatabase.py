import envtest
from spectrumAnalysisFromDatabase import *
from zilia import *
import numpy as np


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

    def testFormatDarkRefWithGlobalWaveLengths(self):
        darkRefData = self.db.getBackgroundIntensities(rlp=6)
        wave = self.db.getWavelengths()
        darkRefData = wave, darkRefData[1]
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

    def testSetSaturationFlag(self):
        fakeSpectra = Spectrum()
        fakeSpectra.data = np.array([[1, 10, 11, 12, 13],[1, 10, 11, 10, 13], [1, 10, 11, 10, 13]])
        saturatedValue = 12
        self.assertEqual(fakeSpectra.data.shape, (3,5))
        flags = setSaturationFlag(fakeSpectra, saturatedValue=saturatedValue)
        # print(flags)
        saturatedIndexes = np.nonzero(flags)
        self.assertEqual(len(saturatedIndexes), 1)
        self.assertEqual(saturatedIndexes[0], 3)

    @envtest.expectedFailure
    def testNormalizationFailsIfNotSameWavelengthsForSpectraAndDarkRef(self):
        rawSpectra = self.db.getRawIntensities(rlp=6, limit=10)
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        spectra = formatSpectra(rawSpectraData)
        darkRefData = self.db.getBackgroundIntensities(rlp=6)
        darkRef = formatDarkRef(darkRefData)
        normalizedSpectrum = normalizeSpectrum(spectra, darkRef)

    def testNormalizeSpectrum(self):
        rawSpectra = self.db.getRawIntensities(rlp=6, limit=10)
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        spectra = formatSpectra(rawSpectraData)
        darkRefData = self.db.getBackgroundIntensities(rlp=6)
        _, darkRefSpectra = darkRefData
        darkRefData = wavelengths, darkRefSpectra
        darkRef = formatDarkRef(darkRefData)
        self.assertEqual(len(darkRef.wavelength.squeeze()), len(spectra.wavelength.squeeze()))

        normalizedSpectrum = normalizeSpectrum(spectra, darkRef)
        data = normalizedSpectrum.data
        wavelengths = normalizedSpectrum.wavelength
        self.assertIsNotNone(normalizedSpectrum)
        self.assertEqual(len(data.squeeze().shape), 2)
        self.assertEqual(len(wavelengths.squeeze().shape), 1)
        self.assertGreater(wavelengths.shape[0], 0)
        self.assertEqual(data.shape[0], wavelengths.shape[0])
        self.assertEqual(data.shape[1], 10)

    def testAbsorbanceSpectrum(self):
        rawSpectra = self.db.getRawIntensities(rlp=6, limit=10)
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        darkRefData = self.db.getBackgroundIntensities(rlp=6)

        whiteRefData = loadWhiteRef(self.whiteRefPath, self.whiteRefBackground)
        whiteRef = formatWhiteRef(whiteRefData)
        spectra = formatSpectra(rawSpectraData)
        _, darkRefSpectra = darkRefData
        darkRefData = wavelengths, darkRefSpectra
        darkRef = formatDarkRef(darkRefData)
        normalizedSpectrum = normalizeSpectrum(spectra, darkRef)

        absorbance = absorbanceSpectrum(whiteRef, normalizedSpectrum)
        self.assertIsNotNone(absorbance)
        data = absorbance.data
        self.assertIsNotNone(data)
        dataWave = absorbance.wavelength
        self.assertIsNotNone(dataWave)
        self.assertEqual(len(dataWave.squeeze().shape), 1)
        self.assertGreater(dataWave.shape[0], 0)
        self.assertEqual(len(data.squeeze().shape), 2)
        self.assertEqual(data.shape[0], dataWave.shape[0])
        self.assertEqual(data.shape[1], 10)


    def testCropComponents(self):
        rawSpectra = self.db.getRawIntensities(rlp=6, limit=10)
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        darkRefData = self.db.getBackgroundIntensities(rlp=6)
        whiteRefData = loadWhiteRef(self.whiteRefPath, self.whiteRefBackground)
        whiteRef = formatWhiteRef(whiteRefData)
        spectra = formatSpectra(rawSpectraData)
        _, darkRefSpectra = darkRefData
        darkRefData = wavelengths, darkRefSpectra
        darkRef = formatDarkRef(darkRefData)
        normalizedSpectrum = normalizeSpectrum(spectra, darkRef)
        absorbance = absorbanceSpectrum(whiteRef, normalizedSpectrum)

        croppedComponent = cropComponents(absorbance, self.componentsSpectra)
        # print(croppedComponent)
        self.assertIsNotNone(croppedComponent)
        self.assertIsInstance(croppedComponent, dict)
        self.assertEqual(len(croppedComponent), 5)
        for spectra in croppedComponent.values():
            self.assertIsInstance(spectra, np.ndarray)
            self.assertEqual(len(spectra.squeeze().shape), 1)
            self.assertEqual(spectra.shape[0], absorbance.wavelength.shape[0])

    def testComponentsToArray(self):
        rawSpectra = self.db.getRawIntensities(rlp=6, limit=10)
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        darkRefData = self.db.getBackgroundIntensities(rlp=6)
        whiteRefData = loadWhiteRef(self.whiteRefPath, self.whiteRefBackground)
        whiteRef = formatWhiteRef(whiteRefData)
        spectra = formatSpectra(rawSpectraData)
        _, darkRefSpectra = darkRefData
        darkRefData = wavelengths, darkRefSpectra
        darkRef = formatDarkRef(darkRefData)
        normalizedSpectrum = normalizeSpectrum(spectra, darkRef)
        absorbance = absorbanceSpectrum(whiteRef, normalizedSpectrum)
        croppedComponents = cropComponents(absorbance, self.componentsSpectra)

        features = componentsToArray(croppedComponents)
        self.assertIsNotNone(features)
        self.assertIsInstance(features, np.ndarray)
        self.assertEqual(len(features.squeeze().shape), 2)
        self.assertEqual(features.shape[1], len(absorbance.wavelength))
        self.assertEqual(features.squeeze().shape[0], 6)

    def testGetCoefficients(self):
        rawSpectra = self.db.getRawIntensities(rlp=6, limit=10)
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        darkRefData = self.db.getBackgroundIntensities(rlp=6)
        whiteRefData = loadWhiteRef(self.whiteRefPath, self.whiteRefBackground)
        whiteRef = formatWhiteRef(whiteRefData)
        spectra = formatSpectra(rawSpectraData)
        _, darkRefSpectra = darkRefData
        darkRefData = wavelengths, darkRefSpectra
        darkRef = formatDarkRef(darkRefData)
        normalizedSpectrum = normalizeSpectrum(spectra, darkRef)
        absorbance = absorbanceSpectrum(whiteRef, normalizedSpectrum)
        croppedComponents = cropComponents(absorbance, self.componentsSpectra)
        features = componentsToArray(croppedComponents)

        coefficients = getCoefficients(absorbance, features)
        self.assertIsNotNone(coefficients)
        self.assertEqual(len(coefficients.squeeze().shape), 2)
        self.assertEqual(coefficients.shape[0], absorbance.data.shape[1])
        self.assertEqual(coefficients.shape[1], features.shape[0])

    def testGetConcentration(self):
        rawSpectra = self.db.getRawIntensities(rlp=6, limit=10)
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        darkRefData = self.db.getBackgroundIntensities(rlp=6)
        whiteRefData = loadWhiteRef(self.whiteRefPath, self.whiteRefBackground)
        whiteRef = formatWhiteRef(whiteRefData)
        spectra = formatSpectra(rawSpectraData)
        _, darkRefSpectra = darkRefData
        darkRefData = wavelengths, darkRefSpectra
        darkRef = formatDarkRef(darkRefData)
        normalizedSpectrum = normalizeSpectrum(spectra, darkRef)
        absorbance = absorbanceSpectrum(whiteRef, normalizedSpectrum)
        croppedComponents = cropComponents(absorbance, self.componentsSpectra)
        features = componentsToArray(croppedComponents)
        coefficients = getCoefficients(absorbance, features)

        concentration = getConcentration(coefficients)
        self.assertIsNotNone(concentration)
        self.assertEqual(len(concentration.squeeze().shape), 1)
        self.assertEqual(concentration.shape[0], coefficients.shape[0])

    def testMainAnalysis(self):
        rawSpectra = self.db.getRawIntensities(rlp=6, limit=10)
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        darkRefData = self.db.getBackgroundIntensities(rlp=6)
        darkRefData = wavelengths, darkRefData[1]
        concentration, saturationFlags = mainAnalysis(darkRefData, rawSpectraData, self.componentsSpectra,
                self.whiteRefPath, self.whiteRefBackground)

        self.assertIsNotNone(concentration)
        self.assertEqual(len(concentration.squeeze().shape), 1)
        self.assertEqual(concentration.shape[0], 10)

        self.assertIsNotNone(saturationFlags)
        self.assertEqual(len(saturationFlags.squeeze().shape), 1)
        self.assertEqual(saturationFlags.shape[0], concentration.shape[0])
        saturationFlags = saturationFlags.squeeze()
        for value in saturationFlags:
            try:
                self.assertEqual(value, 1)
            except:
                self.assertEqual(value, 0)

    def testGetMelaninValues(self):
        rawSpectra = self.db.getRawIntensities(rlp=6, limit=10)
        wavelengths = self.db.getWavelengths()
        rawSpectraData = wavelengths, rawSpectra
        darkRefData = self.db.getBackgroundIntensities(rlp=6)
        darkRefData = wavelengths, darkRefData[1]
        melaninValues, saturationFlags = getMelaninValues(darkRefData, rawSpectraData, self.componentsSpectra,
                self.whiteRefPath, self.whiteRefBackground)

        self.assertIsNotNone(melaninValues)
        self.assertEqual(len(melaninValues.squeeze().shape), 1)
        self.assertEqual(melaninValues.shape[0], 10)

        self.assertIsNotNone(saturationFlags)
        self.assertEqual(len(saturationFlags.squeeze().shape), 1)
        self.assertEqual(saturationFlags.shape[0], melaninValues.shape[0])
        saturationFlags = saturationFlags.squeeze()
        for value in saturationFlags:
            try:
                self.assertEqual(value, 1)
            except:
                self.assertEqual(value, 0)

if __name__ == '__main__':
    envtest.main()
