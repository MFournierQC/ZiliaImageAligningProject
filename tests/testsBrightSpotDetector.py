import envtest
from skimage.io import imread
from skimage.filters import threshold_otsu as otsu
from analyzeBrightSpot import BrightSpotDetector
import matplotlib.pyplot as plt
import numpy as np

skipPlots = True
skipPlots = False

class TestBrightSpotDetector(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertTrue(True)

    def testImportTestImages(self):
        testDir = self.testStudentDirectory
        image1 = imread(testDir+"/testImage1.png")
        self.assertIsNotNone(image1)
        self.assertTrue(len(image1.shape) == 3)
        image2 = imread(testDir+"/testImage2.png")
        self.assertIsNotNone(image2)
        self.assertTrue(len(image2.shape) == 3)
        image3 = imread(testDir+"/testImage3.png")
        self.assertIsNotNone(image3)
        self.assertTrue(len(image3.shape) == 3)

    def plotBrightSpotOnImage(self, image, brightSpotParams):
        xSpot = brightSpotParams[1]
        ySpot = brightSpotParams[0]
        implot = plt.imshow(image)
        plt.plot([xSpot],[ySpot],'o')
        plt.show()

    @envtest.skip("skip plots")
    def testBrightSpotDetectorOnImage1(self):
        testDir = self.testStudentDirectory
        image = imread(testDir+"/testImage1.png", as_gray=True)
        thresh = otsu(image)
        image = image < thresh
        detector = BrightSpotDetector(image)
        self.assertIsNotNone(detector)
        brightSpotParams = detector.getBrightSpot()
        self.assertIsNotNone(brightSpotParams)
        for i in brightSpotParams:
            self.assertIsNotNone(i)
        print(brightSpotParams)
        self.plotBrightSpotOnImage(image, brightSpotParams)

    @envtest.skip("skip plots")
    def testBrightSpotDetectorOnImage3(self):
        testDir = self.testStudentDirectory
        image = imread(testDir+"/testImage3.png", as_gray=True)
        thresh = otsu(image)
        image = image < thresh
        detector = BrightSpotDetector(image)
        brightSpotParams = detector.getBrightSpot()
        print(brightSpotParams)
        self.plotBrightSpotOnImage(image, brightSpotParams)

    @envtest.skip("skip plots")
    def testBrightSpotDetectorOnImage4(self):
        testDir = self.testStudentDirectory
        image = imread(testDir+"/testImage4.png", as_gray=True)
        thresh = otsu(image)
        image = image < thresh
        detector = BrightSpotDetector(image)
        brightSpotParams = detector.getBrightSpot()
        print(brightSpotParams)
        self.plotBrightSpotOnImage(image, brightSpotParams)

    @envtest.skip("skip plots")
    def testBrightSpotDetectorOnImage5(self):
        testDir = self.testStudentDirectory
        image = imread(testDir+"/testImage5.png", as_gray=True)
        thresh = otsu(image)
        image = image < thresh
        detector = BrightSpotDetector(image)
        brightSpotParams = detector.getBrightSpot()
        print(brightSpotParams)
        self.plotBrightSpotOnImage(image, brightSpotParams)

    @envtest.skip("skip plots")
    def testBrightSpotDetectorOnImage6(self):
        testDir = self.testStudentDirectory
        image = imread(testDir+"/testImage6.png", as_gray=True)
        thresh = otsu(image)
        image = image < thresh
        detector = BrightSpotDetector(image)
        brightSpotParams = detector.getBrightSpot()
        print(brightSpotParams)
        self.plotBrightSpotOnImage(image, brightSpotParams)

    @envtest.skipIf(skipPlots, "skip plots")
    def testBrightSpotDetectorOnBresilMedium(self):
        testDir = self.testCannyDirectory
        image = imread(testDir+"/bresilMedium.jpg")
        # image[:,:,2] = 0
        detector = BrightSpotDetector(image)
        brightSpotParams = detector.getBrightSpot()
        print(brightSpotParams)
        self.plotBrightSpotOnImage(image, brightSpotParams)

    @envtest.skipIf(skipPlots, "skip plots")
    def testBrightSpotDetectorOnKenyaHigh(self):
        testDir = self.testCannyDirectory
        image = imread(testDir+"/kenyaHigh.jpg")
        # image[:,:,2] = 0
        detector = BrightSpotDetector(image)
        brightSpotParams = detector.getBrightSpot()
        print(brightSpotParams)
        self.plotBrightSpotOnImage(image, brightSpotParams)

    @envtest.skipIf(skipPlots, "skip plots")
    def testBrightSpotDetectorOnSomalieLow(self):
        testDir = self.testCannyDirectory
        image = imread(testDir+"/somalieLow.jpg")
        # image[:,:,2] = 0
        detector = BrightSpotDetector(image)
        brightSpotParams = detector.getBrightSpot()
        print(brightSpotParams)
        self.plotBrightSpotOnImage(image, brightSpotParams)

    @envtest.skipIf(skipPlots, "skip plots")
    def testBrightSpotDetectorOnPartiallyCut(self):
        testDir = self.testCannyDirectory
        image = imread(testDir+"/partiallyCut.jpg")
        # image[:,:,2] = 0
        detector = BrightSpotDetector(image)
        brightSpotParams = detector.getBrightSpot()
        print(brightSpotParams)
        # plt.hist(image.ravel(), bins=256)
        # plt.show()
        self.plotBrightSpotOnImage(image, brightSpotParams)

    @envtest.skipIf(skipPlots, "skip plots")
    def testPlotThresholdedImage(self):
        testDir = self.testCannyDirectory
        image = imread(testDir+"/150-150-150-50_psr__091.jpg", as_gray=True)
        midIntensity = np.amax(image)/2
        indexes = np.where(image < midIntensity)
        image[indexes] = 0
        plt.imshow(image, cmap="gray")
        plt.show()

    @envtest.skipIf(skipPlots, "skip plots")
    def testBrightSpotDetectorOnPartiallyCut(self):
        testDir = self.testCannyDirectory
        image = imread(testDir+"/150-150-150-50_psr__091.jpg")
        # image[:,:,2] = 0
        detector = BrightSpotDetector(image)
        brightSpotParams = detector.getBrightSpot()
        print(brightSpotParams)
        # plt.hist(image.ravel(), bins=256)
        # plt.show()
        self.plotBrightSpotOnImage(image, brightSpotParams)

    @envtest.skip(skipPlots, "requires modifying the bright spot detector")
    def testBrightSpotDetectorOnPartiallyCut(self):
        testDir = self.testCannyDirectory
        image = imread(testDir+"/Figure_2.png")
        # image[:,:,2] = 0
        detector = BrightSpotDetector(image)
        brightSpotParams = detector.getBrightSpot()
        print(brightSpotParams)
        # plt.hist(image.ravel(), bins=256)
        # plt.show()
        self.plotBrightSpotOnImage(image, brightSpotParams)

if __name__ == "__main__":
    envtest.main()
