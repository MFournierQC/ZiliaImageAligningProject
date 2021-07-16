import envtest
import matplotlib.pyplot as plt
from skimage.io import imread
from skimage.color import rgb2gray
from skimage.exposure import is_low_contrast, adjust_gamma, adjust_log

# This will not work for what I want to do.

class TestContrast(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertTrue(True)

    def testImportImage(self):
        imageRgb = imread(self.testCannyDirectory+"/kenyaHigh.jpg")
        self.assertIsNotNone(imageRgb)

    def testImportGrayImage(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaHigh.jpg", as_gray=True)
        self.assertIsNotNone(grayImage)

    def testIsLowContrastOnBrightImage_doesntWorkOnIt(self):
        imageRgb = imread(self.testCannyDirectory+"/kenyaHigh.jpg")
        self.assertFalse(is_low_contrast(imageRgb))

    def testIsLowContrastOnBrightGRAYImage_doesntWorkOnIt(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaHigh.jpg", as_gray=True)
        self.assertFalse(is_low_contrast(grayImage))

    def testIsLowContrastOnBrightGRAYImage_addUpperPercentile(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaHigh.jpg", as_gray=True)
        self.assertTrue(is_low_contrast(grayImage, upper_percentile=12))
        # 12 is the highest value that returned True with this image.

    def testIsLowContrastOnDimGRAYImage_didNotWork1(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaLow.jpg", as_gray=True)
        self.assertFalse(is_low_contrast(grayImage))

    def testIsLowContrastOnDimGRAYImage_didNotWork2(self):
        grayImage = imread(self.testCannyDirectory+"/somalieLow.jpg", as_gray=True)
        self.assertFalse(is_low_contrast(grayImage))


if __name__ == "__main__":
    envtest.main()
