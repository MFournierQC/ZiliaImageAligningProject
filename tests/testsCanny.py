import envtest
from skimage.io import imread
from skimage.feature import canny
from skimage.color import rgb2gray
import matplotlib.pyplot as plt
import numpy as np

class TestCanny(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertTrue(True)

    def testImportTestImage(self):
        image = imread(self.testCannyDirectory+"/kenyaMedium.jpg")
        self.assertIsNotNone(image)

    def testRGB2GrayCreatesA2DImage(self):
        image = imread(self.testCannyDirectory+"/kenyaMedium.jpg")
        self.assertTrue(image.shape[2] == 3)
        grayImage = rgb2gray(image)
        self.assertIsNotNone(grayImage)
        self.assertTrue(len(grayImage.shape) == 2)
        # processedImage = canny(image)
        # self.assertIsNotNone(processedImage)

    def testCannyNeedsA2DImage(self):
        image = imread(self.testCannyDirectory+"/kenyaMedium.jpg")
        grayImage = rgb2gray(image)
        processedImage = canny(grayImage)
        self.assertIsNotNone(processedImage)

    def testCannySigmaMediumLightKenyaMediumIsEnough(self):
        image = imread(self.testCannyDirectory+"/kenyaMedium.jpg")
        grayImage = rgb2gray(image)
        processedImage = canny(grayImage, sigma=3)
        # plt.imshow(processedImage)
        # plt.show()

    def testCannySigmaLowLightRwandaLowIsNotEnough(self):
        image = imread(self.testCannyDirectory+"/rwandaLow.jpg")
        grayImage = rgb2gray(image)
        processedImage = canny(grayImage, sigma=0.5)
        # plt.imshow(processedImage)
        # plt.show()

    def testCannySigmaMediumLightBresilMediumIsNotEnough(self):
        image = imread(self.testCannyDirectory+"/bresilMedium.jpg")
        grayImage = rgb2gray(image)
        # print(np.amax(grayImage))
        # print(np.amin(grayImage))
        grayImage = grayImage > .3
        processedImage = canny(grayImage, sigma=1)
        plt.imshow(processedImage)
        plt.show()

    def testCannySigmaHighLightSomalieHigh(self):
        image = imread(self.testCannyDirectory+"/somalieHigh.jpg")
        grayImage = rgb2gray(image)
        processedImage = canny(grayImage, sigma=1)
        # plt.imshow(processedImage)
        # plt.show()

    def testCannyThresholdSetup(self):
        image = imread(self.testCannyDirectory+"/kenyaMedium.jpg")
        grayImage = rgb2gray(image)
        maximum = np.max(grayImage)
        self.assertIsNotNone(maximum)
        multiplicator = maximum/100
        self.assertIsNotNone(multiplicator)

    def testCannyThresholdLowLightRwandaLow(self):
        image = imread(self.testCannyDirectory+"/rwandaLow.jpg")
        grayImage = rgb2gray(image)
        maximum = np.max(grayImage)
        multiplicator = maximum/100
        processedImage = canny(grayImage, sigma=3)
        # processedImage = canny(grayImage, sigma=3, low_threshold=0.1)
        # plt.imshow(processedImage)
        # plt.show()



if __name__ == "__main__":
    envtest.main()
