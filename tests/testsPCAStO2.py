import envtest
import unittest
from spectrumAnalysis import mainAnalysis, bloodTest
from processImages import getFiles
from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os


# Run tests in order they are written
unittest.TestLoader.sortTestMethodsUsing = None


# These 3 will always be the same for every test
whiteRefName = r"../int75_WHITEREFERENCE.csv"
refNameNothinInfront = r"../int75_LEDON_nothingInFront.csv"
componentsSpectra = r'../_components_spectra.csv'

# These will be different for every test
darkRefPath2 = r"./TestSpectrums/bresilODrlp2/background.csv"
spectrumPath2 = r"./TestSpectrums/bresilODrlp2/spectrum.csv"
darkRefPath6 = r"./TestSpectrums/bresilODrlp6/background.csv"
spectrumPath6 = r"./TestSpectrums/bresilODrlp6/spectrum.csv"
darkRefPath14 = r"./TestSpectrums/bresilODrlp14/background.csv"
spectrumPath14 = r"./TestSpectrums/bresilODrlp14/spectrum.csv"


class TestPCAStO2(envtest.ZiliaTestCase):

    @envtest.skip("not useful anymore")
    def testImport(self):
        features = mainAnalysis(darkRefPath2, spectrumPath2, whiteRefName=whiteRefName,
                                refNameNothinInfront=refNameNothinInfront,
                                componentsSpectra=componentsSpectra)
        self.assertIsNotNone(features)

    # @envtest.skip("not useful anymore")
    # def setUp(self):
    #     # this will get executed before every test
    #     super().setUp()
    #     self.features = mainAnalysis(darkRefPath2, spectrumPath2, whiteRefName=whiteRefName,
    #                             refNameNothinInfront=refNameNothinInfront,
    #                             componentsSpectra=componentsSpectra)

    @envtest.skip("not useful anymore")
    def testDataReturnTypeIsNumpyArray(self):
        features = mainAnalysis(darkRefPath2, spectrumPath2, whiteRefName=whiteRefName,
                                refNameNothinInfront=refNameNothinInfront,
                                componentsSpectra=componentsSpectra)
        self.assertTrue(type(features) == np.ndarray)

    def testJustInitiatePCA(self):
        pca = PCA()
        self.assertTrue(True)

    @envtest.skip("not useful anymore")
    def testFitPCAToTheData(self):
        features = mainAnalysis(darkRefPath2, spectrumPath2, whiteRefName=whiteRefName,
                                refNameNothinInfront=refNameNothinInfront,
                                componentsSpectra=componentsSpectra)
        pca = PCA()
        pca.fit(features)
        self.assertTrue(True)

    @envtest.skip("not useful anymore")
    def testGetNumberOfComponentsOnRLP2(self):
        features = mainAnalysis(darkRefPath2, spectrumPath2, whiteRefName=whiteRefName,
                                refNameNothinInfront=refNameNothinInfront,
                                componentsSpectra=componentsSpectra)
        pca = PCA()
        pca.fit(features)
        # print(pca.n_components_)
        # We get 6 components with default PCA parameters

    @envtest.skip("not useful anymore")
    def testGetNumberOfComponentsOnRLP4(self):
        features = mainAnalysis(darkRefPath6, spectrumPath6, whiteRefName=whiteRefName,
                                refNameNothinInfront=refNameNothinInfront,
                                componentsSpectra=componentsSpectra)
        pca = PCA()
        pca.fit(features)
        # print(pca.n_components_)
        # We get 6 components AGAIN with default PCA parameters

    @envtest.skip("old code jams")
    def testGetNumberOfComponentsOnRLP14(self):
        features = mainAnalysis(darkRefPath14, spectrumPath14, whiteRefName=whiteRefName,
                                refNameNothinInfront=refNameNothinInfront,
                                componentsSpectra=componentsSpectra)
        pca = PCA()
        pca.fit(features)
        # print(pca.n_components_)
        # We get 6 components AGAIN AGAIN with default PCA parameters



    def testFitPCA_BloodTest(self):
        refNameNothinInfront = r"./TestSpectrums/blood/int75_LEDON_nothingInFront.csv"
        whiteRefName = r"./TestSpectrums/blood/int75_WHITEREFERENCE.csv"
        spectrumPath = r"./TestSpectrums/blood/so66_int300_avg1_1.csv"
        darkRefPath = r"./TestSpectrums/blood/int300_LEDON_nothingInFront.csv"
        componentsSpectra = r"../_components_spectra.csv"
        _, absorbance = bloodTest(refNameNothinInfront=refNameNothinInfront,
                                whiteRefName=whiteRefName, spectrumPath=spectrumPath,
                                darkRefPath=darkRefPath, componentsSpectra=componentsSpectra)
        data = absorbance.data
        pca = PCA()
        pca.fit(data)

    def testGetPCAExplainedVarianceRatio_BloodTest(self):
        refNameNothinInfront = r"./TestSpectrums/blood/int75_LEDON_nothingInFront.csv"
        whiteRefName = r"./TestSpectrums/blood/int75_WHITEREFERENCE.csv"
        spectrumPath = r"./TestSpectrums/blood/so66_int300_avg1_1.csv"
        darkRefPath = r"./TestSpectrums/blood/int300_LEDON_nothingInFront.csv"
        componentsSpectra = r"../_components_spectra.csv"
        _, absorbance = bloodTest(refNameNothinInfront=refNameNothinInfront,
                                whiteRefName=whiteRefName, spectrumPath=spectrumPath,
                                darkRefPath=darkRefPath, componentsSpectra=componentsSpectra)
        data = absorbance.data
        pca = PCA()
        pca.fit(data)
        varianceRatio = pca.explained_variance_ratio_
        self.assertIsNotNone(varianceRatio)

    @envtest.skip("skip plots")
    def testPlotPCAExplainedVarianceRatio_BloodTest(self):
        refNameNothinInfront = r"./TestSpectrums/blood/int75_LEDON_nothingInFront.csv"
        whiteRefName = r"./TestSpectrums/blood/int75_WHITEREFERENCE.csv"
        spectrumPath = r"./TestSpectrums/blood/so66_int300_avg1_1.csv"
        darkRefPath = r"./TestSpectrums/blood/int300_LEDON_nothingInFront.csv"
        componentsSpectra = r"../_components_spectra.csv"
        _, absorbance = bloodTest(refNameNothinInfront=refNameNothinInfront,
                                whiteRefName=whiteRefName, spectrumPath=spectrumPath,
                                darkRefPath=darkRefPath, componentsSpectra=componentsSpectra)
        data = absorbance.data.T
        print(data.shape)
        plt.plot(data.T)
        plt.show()
        pca = PCA(n_components=5)
        pca.fit(data)
        plt.plot(pca.components_.T)
        plt.show()
        varianceRatio = pca.explained_variance_ratio_
        plt.plot(varianceRatio, "b.")
        plt.show()

    def testLoadingASpectraFile(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        spectraPath = getFiles(spectraDirectory, "csv", newImages=False)[0]
        eyeSpectra = pd.read_csv(spectraPath)
        eyeSpectra = eyeSpectra.drop([0,1,2]) # to remove first junk lines
        eyeSpectra = eyeSpectra.drop(columns=["wavelength", "ref", "bg"])
        self.assertIsNotNone(eyeSpectra)
        # print(eyeSpectra)

    def testCastingASpectraFileToNumpyArray(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        spectraPath = getFiles(spectraDirectory, "csv", newImages=False)[0]
        eyeSpectra = pd.read_csv(spectraPath)
        eyeSpectra = eyeSpectra.drop([0,1,2]) # to remove the first junk lines
        eyeSpectra = eyeSpectra.drop(columns=["wavelength", "ref", "bg"])
        eyeSpectra = eyeSpectra.to_numpy()
        self.assertIsNotNone(eyeSpectra)
        self.assertTrue(type(eyeSpectra) == np.ndarray)
        # print(eyeSpectra)

    @envtest.skip("skip plots")
    def testPCAOn1SpectrumFile(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        spectraPath = getFiles(spectraDirectory, "csv", newImages=False)[0]
        eyeSpectra = pd.read_csv(spectraPath)
        eyeSpectra = eyeSpectra.drop([0,1,2]) # to remove the first junk lines
        eyeSpectra = eyeSpectra.drop(columns=["wavelength", "ref", "bg"])
        eyeSpectra = eyeSpectra.to_numpy().T
        data = eyeSpectra
        print(data.shape)
        plt.plot(data.T)
        plt.show()
        # pca = PCA()
        pca = PCA(n_components=5)
        pca.fit(data)
        plt.plot(pca.components_.T)
        plt.show()
        varianceRatio = pca.explained_variance_ratio_
        plt.plot(varianceRatio, "b.")
        plt.show()

    def loadAllSpectrumFiles(self, spectraDirectory):
        spectraPaths = getFiles(spectraDirectory, "csv", newImages=False)
        data = None
        for spectraPath in spectraPaths:
            eyeSpectra = pd.read_csv(spectraPath)
            eyeSpectra = eyeSpectra.drop([0,1,2]) # to remove the first junk lines
            lightSpectra = eyeSpectra["ref"].to_numpy(dtype=np.float64).T
            eyeSpectra = eyeSpectra.drop(columns=["wavelength", "ref", "bg"])
            eyeSpectra = eyeSpectra.to_numpy(dtype=np.float64).T
            if data is None:
                # for the first iteration
                data = eyeSpectra
            else:
                data = np.vstack((data, eyeSpectra))
        return data

    @envtest.skip("skip plots")
    def testPlotLotsOfRosaSpectraExplainedVarianceRatio(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        data = self.loadAllSpectrumFiles(spectraDirectory)
        print(data.shape) # 776 spectra, 512 points each
        plt.plot(data.T)
        plt.show()
        pca = PCA()
        # pca = PCA(n_components=5)
        pca.fit(data)
        plt.plot(pca.components_.T)
        plt.show()
        varianceRatio = pca.explained_variance_ratio_
        plt.plot(varianceRatio, "b.")
        plt.show()

    @envtest.skip("skip plots")
    def testPlotLotsOfRosaSpectraExplainedVarianceRatio_croppedRange(self):
        # cropped to wavelengths from 530 to 585
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        data = self.loadAllSpectrumFiles(spectraDirectory)
        # index 174 to 230
        data = data[:,174:230]
        print(data.shape) # 776 spectra, 512 points each
        plt.plot(data.T)
        plt.show()
        pca = PCA()
        # pca = PCA(n_components=5)
        pca.fit(data)
        plt.plot(pca.components_.T)
        plt.show()
        varianceRatio = pca.explained_variance_ratio_
        plt.plot(varianceRatio, "b.")
        plt.show()

    def getWavelengthAxisValues(self, spectraDirectory):
        spectraPaths = getFiles(spectraDirectory, "csv", newImages=False)
        eyeSpectra = pd.read_csv(spectraPaths[0])
        eyeSpectra = eyeSpectra.drop([0,1,2]) # to remove the first junk lines
        wavelengths = eyeSpectra["wavelength"].to_numpy(dtype=np.float64)
        wavelengthArray = np.linspace(wavelengths[0], wavelengths[-1], num=len(wavelengths))
        return wavelengthArray

    @envtest.skip("skip prints")
    def testGetWavelengthAxisValues(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        wavelengths = self.getWavelengthAxisValues(spectraDirectory)
        print(wavelengths)

    @envtest.skip("skip plots")
    def testPlotPCAWithCalibratedWavelengthAxis(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        wavelengths = self.getWavelengthAxisValues(spectraDirectory)
        data = self.loadAllSpectrumFiles(spectraDirectory)
        print(data.shape) # 776 spectra, 512 points each
        plt.plot(wavelengths, data.T)
        plt.show()
        pca = PCA()
        # pca = PCA(n_components=5)
        pca.fit(data)
        plt.plot(pca.components_.T)
        plt.show()
        varianceRatio = pca.explained_variance_ratio_
        plt.plot(varianceRatio, "b.")
        plt.show()

    @envtest.skip("WILL NOT WORK, CODE WAS CHANGED!")
    def testPlotNormalizedPCA(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        wavelengths = self.getWavelengthAxisValues(spectraDirectory)
        data = self.loadAllSpectrumFiles(spectraDirectory, normalize=True)
        # the "ref" column is anything, it's not the light spectrum...
        print("data.shape:", data.shape) # 776 spectra, 512 points each
        plt.plot(wavelengths, data.T)
        plt.show()
        pca = PCA()
        # pca = PCA(n_components=5)
        pca.fit(data)
        plt.plot(wavelengths, pca.components_.T)
        plt.show()
        varianceRatio = pca.explained_variance_ratio_
        plt.plot(varianceRatio, "b.")
        plt.show()

    @envtest.skip("skip plots and prints")
    def testPlotWhiteRefFileSpectra(self):
        rowsToSkip = [i for i in range(22)]
        spectraPath = r"../int75_WHITEREFERENCE.csv"
        eyeSpectra = pd.read_csv(spectraPath, skiprows=rowsToSkip)
        eyeSpectra = eyeSpectra.drop([0]) # to remove the first junk lines
        eyeSpectra = eyeSpectra.drop(columns=["Pixel", "WaveLength"])# useless
        print("\n", eyeSpectra)
        eyeSpectra = eyeSpectra.drop(columns=["dark", "ref"])# only zeros
        data = eyeSpectra.to_numpy(dtype=np.float64)
        print(data.shape)
        plt.plot(data)
        plt.show()

    def normalizeSpectra(self, data, lightSpectraPath):
        normalizedSpectra = False
        rowsToSkip = [i for i in range(22)]
        spectraPath = r"../int75_WHITEREFERENCE.csv"
        lightSpectra = pd.read_csv(spectraPath, skiprows=rowsToSkip)
        lightSpectra = lightSpectra.drop([0]) # to remove the first junk lines

        wavelengths = lightSpectra["WaveLength"].to_numpy(dtype=np.float64)

        lightSpectra = lightSpectra.drop(columns=["Pixel", "WaveLength"])# useless
        lightSpectra = lightSpectra.drop(columns=["dark", "ref"])# only zeros
        lightSpectra = lightSpectra.to_numpy(dtype=np.float64).T[0,:]

        plt.figure()
        plt.subplot(1,2,1)
        plt.plot(wavelengths, lightSpectra)
        plt.subplot(1,2,2)
        plt.plot(wavelengths[174:230], lightSpectra[174:230])
        plt.show()

        for i in range(data.shape[0]):
            spectrumNorm = np.divide(data[i,:], lightSpectra)
            spectrumNorm[np.isnan(spectrumNorm)] = 0
            spectrumNorm[np.isinf(spectrumNorm)] = 0
            if normalizedSpectra is False:
                normalizedSpectra = spectrumNorm
            else:
                normalizedSpectra = np.vstack((normalizedSpectra, spectrumNorm))
        return normalizedSpectra

    @envtest.skip("skip plots")
    def testPlotNormalizedPCAWithTheRightWhiteReference(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        lightSpectraPath = r"../int75_WHITEREFERENCE.csv"
        wavelengths = self.getWavelengthAxisValues(spectraDirectory)
        data = self.loadAllSpectrumFiles(spectraDirectory)
        data = self.normalizeSpectra(data, lightSpectraPath)
        # the "ref" column is anything, it's not the light spectrum...
        print("data.shape:", data.shape) # 776 spectra, 512 points each
        plt.plot(wavelengths, data.T)
        plt.show()
        pca = PCA()
        pca = PCA(n_components=5)
        pca.fit(data)
        plt.plot(wavelengths, pca.components_.T)
        plt.show()
        varianceRatio = pca.explained_variance_ratio_
        plt.plot(varianceRatio, "b.")
        plt.show()

    @envtest.skip("skip plots")
    def testPlotNormalizedPCAWithTheRightWhiteReference_croppedRange(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        lightSpectraPath = r"../int75_WHITEREFERENCE.csv"
        wavelengths = self.getWavelengthAxisValues(spectraDirectory)[174:230]
        data = self.loadAllSpectrumFiles(spectraDirectory)
        data = self.normalizeSpectra(data, lightSpectraPath)
        data = data[:,174:230]
        # the "ref" column is anything, it's not the light spectrum...
        print("data.shape:", data.shape) # 776 spectra, 512 points each
        plt.plot(wavelengths, data.T)
        plt.show()
        pca = PCA()
        pca = PCA(n_components=5)
        pca.fit(data)
        plt.plot(wavelengths, pca.components_.T)
        plt.show()
        varianceRatio = pca.explained_variance_ratio_
        plt.plot(varianceRatio, "b.")
        plt.show()


    def removeSaturatedImages(self, data):
        indexesToRemove = []
        for i in range(data.shape[0]):
            if 65535 in [int(j) for j in data[i,:]]:
                indexesToRemove.append(i)
        data = np.delete(data, indexesToRemove, axis=0)
        print("numberOfSaturatedImages:", len(indexesToRemove))
        return data

    @envtest.skip("skip plots")
    def testPlotPCAWithoutSaturatedSpectra(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        lightSpectraPath = r"../int75_WHITEREFERENCE.csv"
        wavelengths = self.getWavelengthAxisValues(spectraDirectory)
        data = self.loadAllSpectrumFiles(spectraDirectory)
        data = self.removeSaturatedImages(data)
        # data = self.normalizeSpectra(data, lightSpectraPath)
        print("data.shape:", data.shape) # 776 spectra, 512 points each

        plt.figure()
        plt.subplot(3,2,1)
        plt.plot(wavelengths, data.T)
        plt.title("Non saturated data")
        # plt.show()
        pca = PCA()
        pca.fit(data)
        plt.subplot(3,2,2)
        plt.plot(wavelengths, pca.components_.T)
        plt.title("All components")
        # plt.show()
        varianceRatio = pca.explained_variance_ratio_
        plt.subplot(3,2,3)
        plt.plot(varianceRatio, "b.")
        plt.title("Explained variance ratio")
        # plt.show()

        pca5 = PCA(n_components=5)
        pca5.fit(data)
        plt.subplot(3,2,4)
        plt.plot(wavelengths, pca5.components_.T)
        plt.title("5 components")
        # plt.show()
        varianceRatio5 = pca5.explained_variance_ratio_
        plt.subplot(3,2,5)
        plt.plot(varianceRatio5, "b.")
        plt.title("Explained variance ratio 5 components")
        plt.show()

    @envtest.skip("skip plots")
    def testPlotNormalizedPCAWithoutSaturatedSpectra(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        lightSpectraPath = r"../int75_WHITEREFERENCE.csv"
        wavelengths = self.getWavelengthAxisValues(spectraDirectory)
        data = self.loadAllSpectrumFiles(spectraDirectory)
        data = self.removeSaturatedImages(data)
        data = self.normalizeSpectra(data, lightSpectraPath)
        print("data.shape:", data.shape) # 776 spectra, 512 points each

        plt.figure()
        plt.subplot(3,2,1)
        plt.plot(wavelengths, data.T)
        plt.title("Non saturated data")
        # plt.show()
        pca = PCA()
        pca.fit(data)
        plt.subplot(3,2,2)
        plt.plot(wavelengths, pca.components_.T)
        plt.title("All components")
        # plt.show()
        varianceRatio = pca.explained_variance_ratio_
        plt.subplot(3,2,3)
        plt.plot(varianceRatio, "b.")
        plt.title("Explained variance ratio")
        # plt.show()

        pca5 = PCA(n_components=5)
        pca5.fit(data)
        plt.subplot(3,2,4)
        plt.plot(wavelengths, pca5.components_.T)
        plt.title("5 components")
        # plt.show()
        varianceRatio5 = pca5.explained_variance_ratio_
        plt.subplot(3,2,5)
        plt.plot(varianceRatio5, "b.")
        plt.title("Explained variance ratio 5 components")
        plt.show()

    def normalizeWithNormalizedSpectra(self, data, lightSpectraPath):
        normalizedSpectra = False
        rowsToSkip = [i for i in range(22)]
        spectraPath = r"../int75_WHITEREFERENCE.csv"
        lightSpectra = pd.read_csv(spectraPath, skiprows=rowsToSkip)
        lightSpectra = lightSpectra.drop([0]) # to remove the first junk lines

        wavelengths = lightSpectra["WaveLength"].to_numpy(dtype=np.float64)

        lightSpectra = lightSpectra.drop(columns=["Pixel", "WaveLength"])# useless
        lightSpectra = lightSpectra.drop(columns=["dark", "ref"])# only zeros
        lightSpectra = lightSpectra.to_numpy(dtype=np.float64).T[0,:]
        maxi = np.amax(lightSpectra)
        lightSpectra = lightSpectra / maxi

        plt.figure()
        plt.subplot(1,2,1)
        plt.plot(wavelengths, lightSpectra)
        plt.subplot(1,2,2)
        plt.plot(wavelengths[174:230], lightSpectra[174:230])
        plt.show()

        for i in range(data.shape[0]):
            spectrumNorm = np.divide(data[i,:], lightSpectra)
            spectrumNorm[np.isnan(spectrumNorm)] = 0
            spectrumNorm[np.isinf(spectrumNorm)] = 0
            if normalizedSpectra is False:
                normalizedSpectra = spectrumNorm
            else:
                normalizedSpectra = np.vstack((normalizedSpectra, spectrumNorm))
        return normalizedSpectra

    @envtest.skip("skip plots")
    def testPlotNormalizedWithNormalizedSpectraPCAWithoutSaturatedSpectra(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        lightSpectraPath = r"../int75_WHITEREFERENCE.csv"
        wavelengths = self.getWavelengthAxisValues(spectraDirectory)
        data = self.loadAllSpectrumFiles(spectraDirectory)
        data = self.removeSaturatedImages(data)
        data = self.normalizeWithNormalizedSpectra(data, lightSpectraPath)
        print("data.shape:", data.shape) # 776 spectra, 512 points each

        plt.figure()
        plt.subplot(3,2,1)
        plt.plot(wavelengths, data.T)
        plt.title("Non saturated data")
        # plt.show()
        pca = PCA()
        pca.fit(data)
        plt.subplot(3,2,2)
        plt.plot(wavelengths, pca.components_.T)
        plt.title("All components")
        # plt.show()
        varianceRatio = pca.explained_variance_ratio_
        plt.subplot(3,2,3)
        plt.plot(varianceRatio, "b.")
        plt.title("Explained variance ratio")
        # plt.show()

        pca5 = PCA(n_components=5)
        pca5.fit(data)
        plt.subplot(3,2,4)
        plt.plot(wavelengths, pca5.components_.T)
        plt.title("5 components")
        # plt.show()
        varianceRatio5 = pca5.explained_variance_ratio_
        plt.subplot(3,2,5)
        plt.plot(varianceRatio5, "b.")
        plt.title("Explained variance ratio 5 components")
        plt.show()

    @envtest.skip("skip plots")
    def testPlotSpectraAndNormalizedSpectraSideBySide(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        lightSpectraPath = r"../int75_WHITEREFERENCE.csv"
        wavelengths = self.getWavelengthAxisValues(spectraDirectory)
        data = self.loadAllSpectrumFiles(spectraDirectory)[0:2,:]
        data2 = self.normalizeWithNormalizedSpectra(data, lightSpectraPath)
        print("data.shape:", data.shape) # 776 spectra, 512 points each
        plt.figure()
        plt.subplot(1,2,1)
        plt.plot(wavelengths, data.T)
        plt.title("Normal spectrum")
        plt.subplot(1,2,2)
        plt.plot(wavelengths, data2.T)
        plt.title("Normalized spectrum")
        plt.show()

    @envtest.skip("skip plots")
    def testPlotSpectraAndNormalizedSpectraSideBySide(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        lightSpectraPath = r"../int75_WHITEREFERENCE.csv"
        wavelengths = self.getWavelengthAxisValues(spectraDirectory)
        data = self.loadAllSpectrumFiles(spectraDirectory)[0:2,:]
        data2 = self.normalizeWithNormalizedSpectra(data, lightSpectraPath)
        print("data.shape:", data.shape) # 776 spectra, 512 points each
        plt.figure()
        plt.subplot(1,2,1)
        plt.plot(wavelengths, data.T)
        plt.title("Normal spectrum")
        plt.subplot(1,2,2)
        plt.plot(wavelengths, data2.T)
        plt.title("Normalized spectrum")
        plt.show()

    @envtest.skip("skip plots")
    def testPlotSpectraAndNormalizedSpectraSideBySide_croppedZiliaRange(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        lightSpectraPath = r"../int75_WHITEREFERENCE.csv"
        wavelengths = self.getWavelengthAxisValues(spectraDirectory)
        data = self.loadAllSpectrumFiles(spectraDirectory)[0:2,:]
        data2 = self.normalizeWithNormalizedSpectra(data, lightSpectraPath)
        loSlice = 200
        hiSlice = 260
        print("data.shape:", data.shape) # 776 spectra, 512 points each
        plt.figure()
        plt.subplot(1,2,1)
        plt.plot(wavelengths[loSlice:hiSlice], data.T[loSlice:hiSlice,:])
        plt.title("Normal spectrum")
        plt.subplot(1,2,2)
        plt.plot(wavelengths[loSlice:hiSlice], data2.T[loSlice:hiSlice,:])
        plt.title("Normalized spectrum")
        plt.show()

    @envtest.skip("skip plots")
    def testPCACroppedNonSaturatedNormalized_430To630(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        lightSpectraPath = r"../int75_WHITEREFERENCE.csv"
        loSlice = 100
        hiSlice = -200
        wavelengths = self.getWavelengthAxisValues(spectraDirectory)[loSlice:hiSlice]
        data = self.loadAllSpectrumFiles(spectraDirectory)
        data = self.removeSaturatedImages(data)
        data = self.normalizeWithNormalizedSpectra(data, lightSpectraPath)[:,loSlice:hiSlice]
        print("data.shape:", data.shape) # 776 spectra, 512 points each
        plt.figure()
        plt.subplot(3,2,1)
        plt.plot(wavelengths, data.T)
        plt.title("Non saturated data")
        # plt.show()
        pca = PCA()
        pca.fit(data)
        plt.subplot(3,2,2)
        plt.plot(wavelengths, pca.components_.T)
        plt.title("All components")
        # plt.show()
        varianceRatio = pca.explained_variance_ratio_
        plt.subplot(3,2,3)
        plt.plot(varianceRatio, "b.")
        plt.title("Explained variance ratio")
        # plt.show()

        pca5 = PCA(n_components=5)
        pca5.fit(data)
        plt.subplot(3,2,4)
        plt.plot(wavelengths, pca5.components_.T)
        plt.title("5 components")
        # plt.show()
        varianceRatio5 = pca5.explained_variance_ratio_
        plt.subplot(3,2,5)
        plt.plot(varianceRatio5, "b.")
        plt.title("Explained variance ratio 5 components")
        plt.show()

    @envtest.skip("skip plots")
    def testPCACroppedNonSaturatedNormalized_530To585(self):
        spectraDirectory = r"./TestSpectrums/rawRosaSpectraFromBaseline3"
        lightSpectraPath = r"../int75_WHITEREFERENCE.csv"
        loSlice = 200
        hiSlice = 260
        wavelengths = self.getWavelengthAxisValues(spectraDirectory)[loSlice:hiSlice]
        data = self.loadAllSpectrumFiles(spectraDirectory)
        data = self.removeSaturatedImages(data)
        data = self.normalizeWithNormalizedSpectra(data, lightSpectraPath)[:,loSlice:hiSlice]
        print("data.shape:", data.shape) # 776 spectra, 512 points each
        plt.figure()
        plt.subplot(3,2,1)
        plt.plot(wavelengths, data.T)
        plt.title("Non saturated data")
        # plt.show()
        pca = PCA()
        pca.fit(data)
        plt.subplot(3,2,2)
        plt.plot(wavelengths, pca.components_.T)
        plt.title("All components")
        # plt.show()
        varianceRatio = pca.explained_variance_ratio_
        plt.subplot(3,2,3)
        plt.plot(varianceRatio, "b.")
        plt.title("Explained variance ratio")
        # plt.show()

        pca5 = PCA(n_components=5)
        pca5.fit(data)
        plt.subplot(3,2,4)
        plt.plot(wavelengths, pca5.components_.T)
        plt.title("5 components")
        # plt.show()
        varianceRatio5 = pca5.explained_variance_ratio_
        plt.subplot(3,2,5)
        plt.plot(varianceRatio5, "b.")
        plt.title("Explained variance ratio 5 components")
        plt.show()

if __name__ == "__main__":
    envtest.main()
