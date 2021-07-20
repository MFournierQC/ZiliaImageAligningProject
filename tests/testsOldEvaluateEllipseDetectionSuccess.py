import envtest
import os
import numpy as np
from skimage.io import imread
import matplotlib.pyplot as plt
from processImages import listFileNames, getFiles
from analyzeRetinaImages import ZiliaONHDetector
from skimage.draw import ellipse, ellipse_perimeter
import math
import json

"""
WARNING: These tests will fail on another computer if the test files path
is not changed!
"""

# The inputs are original retina images with visible ONH
# The outputs are the binary images that have been manually fitted
#inputsPath = r"E:\AAA_Reference images\ManuallySorted/inputs"
#outputsPath = r"E:\AAA_Reference images\ManuallySorted/outputs"
inputsPath = r"/Volumes/Data/AAA_Reference images/ManuallySorted/inputs"
outputsPath = r"/Volumes/Data/AAA_Reference images/ManuallySorted/outputs"

# These values will be to find which one gives the best success rate when they
# are used as thresholds to apply gamma correction
globalMean = 0.5301227941321696
meanMinHalfSigma = 0.4891183892357014
meanMinSigma = 0.4481139843392332
meanMin2Sigma = 0.36610517454629693

@envtest.skip("Will fail if path is not changed")
class TestEllipseDetectionSuccess(envtest.ZiliaTestCase):

    def testAccessData(self):
        listDirIn = os.listdir(inputsPath)
        listDirOut = os.listdir(outputsPath)
        self.assertTrue(len(listDirIn) > 1)
        self.assertTrue(len(listDirOut) > 1)
        # print(listDirOut)
        # print(listDirIn)

    def testSortFileNames(self):
        sortedFileNames = np.sort(listFileNames(inputsPath))
        self.assertTrue(len(sortedFileNames) > 1)
        # print(sortedFileNames)

    def testFileNamesAreTheSameForInsAndOuts(self):
        sortedInputs = np.sort(listFileNames(inputsPath))
        sortedOutputs = np.sort(listFileNames(outputsPath))
        self.assertTrue(len(sortedInputs) == len(sortedOutputs))
        for i in range(len(sortedInputs)):
            self.assertTrue(sortedInputs[i] == sortedOutputs[i])

    @envtest.skip("skip plots")
    def testOutputImageIntoBinary(self):
        sortedOutputs = getFiles(outputsPath, newImages=False)
        testImage = imread(sortedOutputs[0], as_gray=True)
        self.assertTrue(len(testImage.shape) == 2)
        lower = 0
        upper = 1
        threshold = 0.5
        binaryImage = np.where(testImage >= threshold, upper, lower)
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(testImage)
        plt.subplot(1,2,2)
        plt.imshow(binaryImage)
        plt.show()

    def binarizeImage(self, colorImagePath):
        grayImage = imread(colorImagePath, as_gray=True)
        lower = 0
        upper = 1
        threshold = 0.5
        binaryImage = np.where(grayImage >= threshold, upper, lower)
        return binaryImage

    @envtest.skip("skip plots")
    def testBinarizeImage(self):
        sortedInputs = getFiles(inputsPath, newImages=False)
        sortedOutputs = getFiles(outputsPath, newImages=False)
        testInput = imread(sortedInputs[0])
        testOutput = self.binarizeImage(sortedOutputs[0])
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(testInput)
        plt.subplot(1,2,2)
        plt.imshow(testOutput, cmap="gray")
        plt.show()

    @envtest.skip("skip plots")
    def testDrawFullEllipse(self):
        testImage = imread(self.testStudentDirectory+"/testImage1.png")
        onhDetector = ZiliaONHDetector(testImage)
        onhDetector.getParamsCorrections()
        onhDetector.preProcessImage()
        bestEllipse = onhDetector.findOpticNerveHead()
        if bestEllipse is None:
            self.assertFalse(True)
        (xCenter, yCenter), minorAxis, majorAxis, orientation = bestEllipse

        yPoints, xPoints = ellipse(yCenter, xCenter, minorAxis, majorAxis, rotation=orientation)

        imageWithEllipse = np.zeros((testImage.shape[0], testImage.shape[1]))
        imageWithEllipse[yPoints, xPoints] = 1
        # print(imageWithEllipse)
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(testImage)
        plt.subplot(1,2,2)
        plt.imshow(imageWithEllipse, cmap="gray")
        plt.show()

    def getBestEllipse(self, image, highGamma=3, gammaThresh=0.5, scaleFactor=3, accuracy=10):
        onhDetector = ZiliaONHDetector(image, scaleFactor=scaleFactor, accuracy=accuracy)
        onhDetector.getParamsCorrections(highGamma=highGamma, gammaThresh=gammaThresh)
        onhDetector.preProcessImage()
        bestEllipse = onhDetector.findOpticNerveHead()
        return bestEllipse

    def getImageWithFullEllipse(self, bestEllipse, originalImage):
        (xCenter, yCenter), minorAxis, majorAxis, orientation = bestEllipse
        if orientation > math.pi:
            orientation -= 2*math.pi
        yPoints, xPoints = ellipse(yCenter, xCenter, minorAxis, majorAxis, rotation=-orientation)

        indexesToRemove = []
        for i in range(len(yPoints)):
            if yPoints[i] > (originalImage.shape[0] - 1):
                # The ellipse is out of the image's boundaries
                indexesToRemove.append(i)
            elif xPoints[i] > (originalImage.shape[1] - 1):
                # The ellipse is out of the image's boundaries
                indexesToRemove.append(i)
            else:
                # The ellipse is in the image's boudaries
                continue

        # remove elements out of the image's boudaries:
        yPoints = np.delete(yPoints, indexesToRemove)
        xPoints = np.delete(xPoints, indexesToRemove)

        imageWithEllipse = np.zeros((originalImage.shape[0], originalImage.shape[1]))
        imageWithEllipse[yPoints, xPoints] = 1

        return imageWithEllipse

    def getImageWithEmptyEllipse(self, bestEllipse, originalImage):
        (xCenter, yCenter), minorAxis, majorAxis, orientation = bestEllipse
        if orientation > math.pi:
            orientation -= 2*math.pi
        yPoints, xPoints = ellipse_perimeter(yCenter, xCenter, minorAxis, majorAxis, orientation=orientation)
        imageWithEllipse = np.zeros((originalImage.shape[0], originalImage.shape[1]))
        imageWithEllipse[yPoints, xPoints] = 1
        return imageWithEllipse

    def plotOriginalImageNextToFit(self, originalImage, imageWithEllipse):
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(originalImage)
        plt.subplot(1,2,2)
        plt.imshow(imageWithEllipse, cmap="gray")
        plt.show()

    @envtest.skip("skip plots")
    def testEllipseFunctions(self):
        testInput = imread(self.testStudentDirectory+"/testImage1.png")
        bestEllipse = self.getBestEllipse(testInput)
        if bestEllipse is None:
            self.assertFalse(True)
        imageWithEllipse = self.getImageWithFullEllipse(bestEllipse, testInput)
        self.plotOriginalImageNextToFit(testInput, imageWithEllipse)

    @envtest.skip("skip plots")
    def testCompareEllipseAndEllipsePerimeter(self):
        testInput = imread(self.testStudentDirectory+"/testImage4.png")
        bestEllipse = self.getBestEllipse(testInput)
        if bestEllipse is None:
            self.assertFalse(True)
        imageWithEllipse = self.getImageWithFullEllipse(bestEllipse, testInput)
        imageWithEllipsePerimeter = self.getImageWithEmptyEllipse(bestEllipse, testInput)
        self.plotOriginalImageNextToFit(imageWithEllipsePerimeter, imageWithEllipse)
        # So "orientation" in ellipse_perimeter seems to be the same as
        # "-rotation" in ellipse.

    @envtest.skip("skip plots")
    def testEllipseFunctionsOnRealImage(self):
        sortedInputs = getFiles(inputsPath, newImages=False)
        testInput = imread(sortedInputs[0])
        bestEllipse = self.getBestEllipse(testInput)
        if bestEllipse is None:
            self.assertFalse(True)
        imageWithEllipse = self.getImageWithFullEllipse(bestEllipse, testInput)
        imageWithEllipsePerimeter = self.getImageWithEmptyEllipse(bestEllipse, testInput)
        self.plotOriginalImageNextToFit(testInput, imageWithEllipse)
        self.plotOriginalImageNextToFit(testInput, imageWithEllipsePerimeter)

    @envtest.skip("skip computing time")
    def testFindSuccessRateOn1File(self):
        sortedInputs = getFiles(inputsPath, newImages=False)
        sortedOutputs = getFiles(outputsPath, newImages=False)
        testInput = imread(sortedInputs[0])
        testOutput = self.binarizeImage(sortedOutputs[0])
        bestEllipse = self.getBestEllipse(testInput)
        if bestEllipse is None:
            self.assertFalse(True)
        imageWithEllipse = self.getImageWithFullEllipse(bestEllipse, testInput)
        resultMatrix = imageWithEllipse + testOutput
        self.assertTrue(np.max(resultMatrix) == 2)
        self.assertTrue(np.min(resultMatrix) == 0)

        values, counts = np.unique(resultMatrix, return_counts=True)
        results = dict(zip(values, counts))
        self.assertTrue(len(results) == 3)

        imageShape = testInput.shape
        numberOfValues = imageShape[0]*imageShape[1]

        result = ((numberOfValues - results[1])/numberOfValues)*100
        print("success % = ", result, "%") # 93.82956511054942 %

    @envtest.skip("skip plots computing time")
    def testFindSuccessRateOn4FileWithGammaThreshEqualsMean(self):
        sortedInputs = getFiles(inputsPath, newImages=False)[:4]
        sortedOutputs = getFiles(outputsPath, newImages=False)[:4]
        sortedFileNames = np.sort(listFileNames(inputsPath))
        resultsList = []
        # resultsDict = {}
        for i in range(len(sortedInputs)):
            print(f"image index {i} being analyzed")
            testInput = imread(sortedInputs[i])
            testOutput = self.binarizeImage(sortedOutputs[i])
            bestEllipse = self.getBestEllipse(testInput, highGamma=3, gammaThresh=globalMean)
            if bestEllipse is None:
                self.assertFalse(True)
            imageWithEllipse = self.getImageWithFullEllipse(bestEllipse, testInput)
            resultMatrix = imageWithEllipse + testOutput
            self.plotOriginalImageNextToFit(testInput, imageWithEllipse)

            values, counts = np.unique(resultMatrix, return_counts=True)
            results = dict(zip(values, counts))

            imageShape = testInput.shape
            numberOfValues = imageShape[0]*imageShape[1]

            result = (numberOfValues - results[1])/numberOfValues
            resultsList.append(result)

        mean = np.mean(resultsList)
        std = np.std(resultsList)

        print("resultsList = ", resultsList) # [0.9382956511054943, 0.966275084252451, 0.9911971746706495, 0.9869382771012051]
        print("mean = ", mean) # 0.97067654678245
        print("std = ", std) # 0.020937020556485244

    def testSaveDictToJsonFile(self):
        testDictionary = {0:51, 1:49, 2:72}
        with open('dictionarySaveTest.json', 'w') as file:
            json.dump(testDictionary, file, indent=4)

    def testFindAverageAreaOf1ONH(self):
        sortedOutputs = getFiles(outputsPath, newImages=False)[0]
        testOutput = self.binarizeImage(sortedOutputs)

        values, counts = np.unique(testOutput, return_counts=True)
        results = dict(zip(values, counts))
        self.assertTrue(len(results) == 2) # only zeros and ones
        imageShape = testOutput.shape
        numberOfValues = imageShape[0]*imageShape[1]
        areaFraction = results[1]/numberOfValues
        # print("areaFraction =", areaFraction) # 0.07803564133986927

    @envtest.skip("skip prints")
    def testFindAverageAreaOf4ONH(self):
        sortedOutputs = getFiles(outputsPath, newImages=False)[:4]
        sortedFileNames = np.sort(listFileNames(outputsPath))[:4]
        areasList = []
        for i in range(len(sortedOutputs)):
            print(f"image index {i} being analyzed")
            testOutput = self.binarizeImage(sortedOutputs[i])
            values, counts = np.unique(testOutput, return_counts=True)
            results = dict(zip(values, counts))
            self.assertTrue(len(results) == 2) # only zeros and ones
            imageShape = testOutput.shape
            numberOfValues = imageShape[0]*imageShape[1]
            areaFraction = results[1]/numberOfValues
            areasList.append(areaFraction)

        mean = np.mean(areasList)
        std = np.std(areasList)

        print("resultsList = ", areasList) # [0.07803564133986927, 0.07774303162020016, 0.0934344522314134, 0.09696372038398693]
        print("mean = ", mean) # 0.08654421139386743
        print("std = ", std) # 0.008744971643275513

    def findAreaOfONH(self, sortedOutputs):
        areasList = []
        for i in range(len(sortedOutputs)):
            print(f"image index {i} being analyzed")
            testOutput = self.binarizeImage(sortedOutputs[i])
            values, counts = np.unique(testOutput, return_counts=True)
            results = dict(zip(values, counts))
            imageShape = testOutput.shape
            numberOfValues = imageShape[0]*imageShape[1]
            areaFraction = results[1]/numberOfValues
            areasList.append(areaFraction)
        mean = np.mean(areasList)
        std = np.std(areasList)
        return areasList, mean, std

    @envtest.skip("skip prints")
    def testFindAverageAreaOf4ONH(self):
        sortedOutputs = getFiles(outputsPath, newImages=False)[:4]
        sortedFileNames = np.sort(listFileNames(outputsPath))[:4]
        areasList, mean, std = self.findAreaOfONH(sortedOutputs)
        print("resultsList = ", areasList) # [0.07803564133986927, 0.07774303162020016, 0.0934344522314134, 0.09696372038398693]
        print("mean = ", mean) # 0.08654421139386743
        print("std = ", std) # 0.008744971643275513

    @envtest.skip("skip file creation")
    def testSaveAreasOf4ONHInJsonFile(self):
        sortedOutputs = getFiles(outputsPath, newImages=False)[:4]
        sortedFileNames = np.sort(listFileNames(outputsPath))[:4]
        areasList, mean, std = self.findAreaOfONH(sortedOutputs)

        imageData = dict(zip(sortedFileNames, areasList))
        with open('areasSaveTest.json', 'w') as file:
            json.dump(imageData, file, indent=4)

    @envtest.skip("skip prints and file creation")
    def testFindAverageAreaOfAllONHAndSaveToJson(self):
        sortedOutputs = getFiles(outputsPath, newImages=False)
        sortedFileNames = np.sort(listFileNames(outputsPath))
        areasList, mean, std = self.findAreaOfONH(sortedOutputs)

        imageData = dict(zip(sortedFileNames, areasList))
        imageData["result"] = {"mean": mean, "std":std}
        with open('resultsONHAreas.json', 'w') as file:
            json.dump(imageData, file, indent=4)
        print("mean = ", mean) # 0.06992786356834266
        print("std = ", std) # 0.009001371815973887
        # 7.0 \pm 0.9

    def findSuccessRateOfONHDetection(self, sortedInputs, sortedOutputs, sortedFileNames,
                                        parameters, scaleFactor=3, accuracy=10, highGamma=3, gammaThresh=0.5, save=True, filename="resultsBestEllipse.json"):
        resultsList = []
        errorsIndexes = []
        for i in range(len(sortedInputs)):
            print(f"image index {i} being analyzed")
            testInput = imread(sortedInputs[i])
            testOutput = self.binarizeImage(sortedOutputs[i])
            bestEllipse = self.getBestEllipse(testInput, highGamma=highGamma, gammaThresh=gammaThresh,
                                            scaleFactor=scaleFactor, accuracy=accuracy)
            print(f"hough {i} done")
            if save:
                self.saveBestEllipse(sortedFileNames, i, bestEllipse, parameters, filename)
            if bestEllipse is None:
                # No ellipse has been found
                errorsIndexes.append(i)
                continue
            imageWithEllipse = self.getImageWithFullEllipse(bestEllipse, testInput)
            resultMatrix = imageWithEllipse + testOutput
            # self.plotOriginalImageNextToFit(testInput, imageWithEllipse)

            values, counts = np.unique(resultMatrix, return_counts=True)
            results = dict(zip(values, counts))

            imageShape = testInput.shape
            numberOfValues = imageShape[0]*imageShape[1]

            result = (numberOfValues - results[1])/numberOfValues
            resultsList.append(result)

        mean = np.mean(resultsList)
        std = np.std(resultsList)

        if errorsIndexes == []:
            errorsIndexes = None

        return resultsList, mean, std, errorsIndexes

    def saveBestEllipse(self, sortedFileNames, index, bestEllipse, parameters, fileName):
        imageName = sortedFileNames[index]
        imageData = {"bestEllipse":bestEllipse}
        if index != 0:
            with open(fileName, 'r') as file:
                data = json.load(file)
                data["parameters"] = parameters
                data[imageName] = imageData
            with open(fileName, 'w') as file:
                json.dump(data, file, indent=4)
        else:
            data = {}
            data["parameters"] = parameters
            data[imageName] = imageData
            with open(fileName, 'w') as file:
                json.dump(data, file, indent=4)

    @envtest.skip("skip file creation and computing time")
    def testFindSuccessRateOn4FileAndSaveToJson(self):
        sortedInputs = getFiles(inputsPath, newImages=False)[:4]
        sortedOutputs = getFiles(outputsPath, newImages=False)[:4]
        sortedFileNames = np.sort(listFileNames(inputsPath))
        resultsList, mean, std = self.findSuccessRateOfONHDetection(sortedInputs, sortedOutputs)
        imageData = dict(zip(sortedFileNames, resultsList))
        imageData["result"] = {"mean": mean, "std":std}
        with open('onhDetectionSuccessRateSaveTest.json', 'w') as file:
            json.dump(imageData, file, indent=4)
        print("mean = ", mean) #0.97067654678245
        print("std = ", std) #0.020937020556485244

    @envtest.skip("skip file creation and computing time")
    def testFindSuccessRateOn4FilesAndSaveToJsonWithQuickerParameters(self):
        sortedInputs = getFiles(inputsPath, newImages=False)[:4]
        sortedOutputs = getFiles(outputsPath, newImages=False)[:4]
        sortedFileNames = np.sort(listFileNames(inputsPath))
        resultsList, mean, std = self.findSuccessRateOfONHDetection(sortedInputs, sortedOutputs, scaleFactor=5, accuracy=10)
        imageData = dict(zip(sortedFileNames, resultsList))
        imageData["result"] = {"mean": mean, "std":std}
        with open('onhDetectionSuccessRateSaveTest.json', 'w') as file:
            json.dump(imageData, file, indent=4)
        print("mean = ", mean) #0.9677821639316534
        print("std = ", std) #0.019030374768215397

    @envtest.skip("skip file creation")
    def testSaveDictWithNumpyArrayThatHasStringToJsonFile(self):
        testDictionary = {0:51, 1:list(np.array(["a","b","c"])), 2:72}
        with open('dictionaryWithNumpySaveTest.json', 'w') as file:
            json.dump(testDictionary, file, indent=4)

    @envtest.skip("skip computing time")
    def testWeirdIndexError(self):
        # These parameters need to change in subsequent tests:
        scaleFactor = 10
        accuracy = 15
        highGamma = 2.5
        gammaThresh = meanMin2Sigma
        fileName = 'resultsONHAccuracy1_.json'

        sortedInputs = getFiles(inputsPath, newImages=False)[121:125]
        sortedOutputs = getFiles(outputsPath, newImages=False)[121:125]
        sortedFileNames = np.sort(listFileNames(inputsPath))[121:125]

        resultsList, mean, std, errorsIndexes = self.findSuccessRateOfONHDetection(sortedInputs, sortedOutputs,
                                                                    scaleFactor=scaleFactor, accuracy=accuracy,
                                                                    highGamma=highGamma, gammaThresh=gammaThresh)

    @envtest.skip("skip file creation and computing time")
    def testFindSuccessRateOnAllFilesAndSaveToJson_1_smallScaleFactor(self):
        # These parameters need to change in subsequent tests:
        scaleFactor = 10
        accuracy = 50
        highGamma = 2.5
        gammaThresh = meanMin2Sigma
        fileName = 'resultsONHAccuracy1_.json'

        parameters = {"scaleFactor":scaleFactor,
                        "accuracy":accuracy,
                        "highGamma":highGamma,
                        "gammaThresh":gammaThresh}

        sortedInputs = getFiles(inputsPath, newImages=False)
        sortedOutputs = getFiles(outputsPath, newImages=False)
        sortedFileNames = np.sort(listFileNames(inputsPath))

        resultsList, mean, std, errorsIndexes = self.findSuccessRateOfONHDetection(sortedInputs, sortedOutputs, sortedFileNames, parameters,
                                                                    scaleFactor=scaleFactor, accuracy=accuracy,
                                                                    highGamma=highGamma, gammaThresh=gammaThresh)

        self.saveAccuracyResults(errorsIndexes, sortedFileNames, resultsList, mean, std, parameters, fileName)
        print("mean = ", mean) # 0.9021230440208527
        print("std = ", std) # 0.10323497333112443
        # deb12h08
        # fin13h27

    @envtest.skip("skip file creation and computing time")
    def testFindSuccessRateOnAllFilesAndSaveToJson_2_threshMinSigma(self):
        # These parameters need to change in subsequent tests:
        scaleFactor = 10
        accuracy = 50
        highGamma = 2.5
        gammaThresh = meanMinSigma
        fileName = 'resultsONHAccuracy2.json'

        parameters = {"scaleFactor":scaleFactor,
                        "accuracy":accuracy,
                        "highGamma":highGamma,
                        "gammaThresh":gammaThresh}

        sortedInputs = getFiles(inputsPath, newImages=False)
        sortedOutputs = getFiles(outputsPath, newImages=False)
        sortedFileNames = np.sort(listFileNames(inputsPath))

        resultsList, mean, std, errorsIndexes = self.findSuccessRateOfONHDetection(sortedInputs, sortedOutputs, sortedFileNames, parameters,
                                                                    scaleFactor=scaleFactor, accuracy=accuracy,
                                                                    highGamma=highGamma, gammaThresh=gammaThresh)

        self.saveAccuracyResults(errorsIndexes, sortedFileNames, resultsList, mean, std, parameters, fileName)
        print("mean = ", mean) # 0.9021230440208527
        print("std = ", std) # 0.10323497333112443
        # deb13h42
        # fin14h58

    @envtest.skip("skip file creation and computing time")
    def testFindSuccessRateOnAllFilesAndSaveToJson_3_threshGlobalMean(self):
        # These parameters need to change in subsequent tests:
        scaleFactor = 10
        accuracy = 50
        highGamma = 2.5
        gammaThresh = globalMean
        fileName = 'resultsONHAccuracy3.json'

        parameters = {"scaleFactor":scaleFactor,
                        "accuracy":accuracy,
                        "highGamma":highGamma,
                        "gammaThresh":gammaThresh}

        sortedInputs = getFiles(inputsPath, newImages=False)
        sortedOutputs = getFiles(outputsPath, newImages=False)
        sortedFileNames = np.sort(listFileNames(inputsPath))

        resultsList, mean, std, errorsIndexes = self.findSuccessRateOfONHDetection(sortedInputs, sortedOutputs, sortedFileNames, parameters,
                                                                    scaleFactor=scaleFactor, accuracy=accuracy,
                                                                    highGamma=highGamma, gammaThresh=gammaThresh)

        self.saveAccuracyResults(errorsIndexes, sortedFileNames, resultsList, mean, std, parameters, fileName)
        print("mean = ", mean) # 0.9021230440208527
        print("std = ", std) # 0.10323497333112443
        # deb15h10
        # fin16h27

    """
    WARNING: test results obtained before this are NOT VALID. An error has been
    found in the ZiliaONHDetector class that prevented gamma correction from
    being applied to any image. This has now been corrected. However, running
    the code of the previous functions WILL give you the right results, but I
    will not do it because I'm going to change things anyway.
    """

    @envtest.skip("skip computing time and prints")
    def testFindSuccessRateOn7Files_threshGlobalMean(self):
        # These parameters need to change in subsequent tests:
        scaleFactor = 10
        accuracy = 50
        highGamma = 2.5
        gammaThresh = globalMean

        parameters = {"scaleFactor":scaleFactor,
                        "accuracy":accuracy,
                        "highGamma":highGamma,
                        "gammaThresh":gammaThresh}

        sortedInputs = getFiles(inputsPath, newImages=False)[:7]
        sortedOutputs = getFiles(outputsPath, newImages=False)[:7]
        sortedFileNames = np.sort(listFileNames(inputsPath))[:7]

        resultsList, mean, std, errorsIndexes = self.findSuccessRateOfONHDetection(sortedInputs, sortedOutputs, sortedFileNames, parameters,
                                                                    scaleFactor=scaleFactor, accuracy=accuracy,
                                                                    highGamma=highGamma, gammaThresh=gammaThresh, save=False)

        print("mean = ", mean) # 0.9190614274681226
        print("std = ", std) # 0.017543006158192546
        # indexes 4,5,6 have no gamma

    @envtest.skip("skip computing time and prints")
    def testFindSuccessRateOn7Files_threshMeanMinSigma(self):
        # These parameters need to change in subsequent tests:
        scaleFactor = 10
        accuracy = 50
        highGamma = 2.5
        gammaThresh = meanMinSigma

        parameters = {"scaleFactor":scaleFactor,
                        "accuracy":accuracy,
                        "highGamma":highGamma,
                        "gammaThresh":gammaThresh}

        sortedInputs = getFiles(inputsPath, newImages=False)[:7]
        sortedOutputs = getFiles(outputsPath, newImages=False)[:7]
        sortedFileNames = np.sort(listFileNames(inputsPath))[:7]

        resultsList, mean, std, errorsIndexes = self.findSuccessRateOfONHDetection(sortedInputs, sortedOutputs, sortedFileNames, parameters,
                                                                    scaleFactor=scaleFactor, accuracy=accuracy,
                                                                    highGamma=highGamma, gammaThresh=gammaThresh, save=False)

        print("mean = ", mean) # 0.9298124482540412
        print("std = ", std) # 0.01628619385363592
        # only index 6 has no gamma

    def saveAccuracyResults(self, errorsIndexes, sortedFileNames, resultsList, mean, std, parameters, fileName):
        if errorsIndexes is None:
            filesNamesWithErrors = []
            errorsIndexes = 0
            unmatched = {"number":errorsIndexes,
                "fileNames":filesNamesWithErrors}
        else:
            filesNamesWithErrors = list(np.array(sortedFileNames)[errorsIndexes])
            sortedFileNames = list(np.delete(sortedFileNames, errorsIndexes))
            unmatched = {"number":len(errorsIndexes),
                "fileNames":filesNamesWithErrors}
        imageData = dict(zip(sortedFileNames, resultsList))
        imageData["results"] = {"mean": mean, "std":std}
        imageData["parameters"] = parameters
        imageData["unmatched"] = unmatched

        with open(fileName, 'w') as file:
            json.dump(imageData, file, indent=4)

    @envtest.skip("skip file creation and computing time")
    def testFindSuccessRateOnAllFilesAndSaveToJson_3_threshMeanMin2Sigma_NoError(self):
        # These parameters need to change in subsequent tests:
        scaleFactor = 10
        accuracy = 50
        highGamma = 2.5
        gammaThresh = meanMin2Sigma
        fileName = 'resultsONHAccuracy_gammaMeanMin2Sigma.json'
        bestEllipsesFileName = "bestEllipseData_gammaMeanMin2Sigma.json"

        parameters = {"scaleFactor":scaleFactor,
                        "accuracy":accuracy,
                        "highGamma":highGamma,
                        "gammaThresh":gammaThresh}

        sortedInputs = getFiles(inputsPath, newImages=False)
        sortedOutputs = getFiles(outputsPath, newImages=False)
        sortedFileNames = np.sort(listFileNames(inputsPath))

        resultsList, mean, std, errorsIndexes = self.findSuccessRateOfONHDetection(sortedInputs, sortedOutputs, sortedFileNames, parameters,
                                                                    scaleFactor=scaleFactor, accuracy=accuracy,
                                                                    highGamma=highGamma, gammaThresh=gammaThresh, filename=bestEllipsesFileName)

        self.saveAccuracyResults(errorsIndexes, sortedFileNames, resultsList, mean, std, parameters, fileName)
        print("mean = ", mean) # 0.9145988638238178
        print("std = ", std) # 0.09334983598704147
        # deb 11h43
        # fin before 12h24
        # ancien plus vite : 1h16min

    @envtest.skip("skip file creation and computing time")
    def testFindSuccessRateOnAllFilesAndSaveToJson_3_threshMeanMinSigma_NoError(self):
        # These parameters need to change in subsequent tests:
        scaleFactor = 10
        accuracy = 50
        highGamma = 2.5
        gammaThresh = meanMinSigma
        fileName = 'resultsONHAccuracy_gammaMeanMinSigma.json'
        bestEllipsesFileName = "bestEllipseData_gammaMeanMinSigma.json"

        parameters = {"scaleFactor":scaleFactor,
                        "accuracy":accuracy,
                        "highGamma":highGamma,
                        "gammaThresh":gammaThresh}

        sortedInputs = getFiles(inputsPath, newImages=False)
        sortedOutputs = getFiles(outputsPath, newImages=False)
        sortedFileNames = np.sort(listFileNames(inputsPath))
        
        resultsList, mean, std, errorsIndexes = self.findSuccessRateOfONHDetection(sortedInputs, sortedOutputs, sortedFileNames, parameters,
                                                                   scaleFactor=scaleFactor, accuracy=accuracy,
                                                                   highGamma=highGamma, gammaThresh=gammaThresh, filename=bestEllipsesFileName)

        self.saveAccuracyResults(errorsIndexes, sortedFileNames, resultsList, mean, std, parameters, fileName)
        print("mean = ", mean) #0.9040605843079217
        print("std = ", std) #0.10120113566800364
        # deb 12h55
        # fin ???
        # ancien plus vite : 1h16min

# globalMean = 0.5301227941321696
# meanMinHalfSigma = 0.4891183892357014
# meanMinSigma = 0.4481139843392332
# meanMin2Sigma = 0.36610517454629693

if __name__ == "__main__":
    envtest.main()
