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

    def plotImageComparison(self, image1, image2):
        # To prevent repetition in subsequent tests.
        fig2, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=(8, 4),
                                        sharex=True, sharey=True)
        ax1.set_title('First image')
        ax1.imshow(image1, cmap=plt.cm.gray)
        ax2.set_title('Second image')
        ax2.imshow(image2, cmap=plt.cm.gray)
        plt.show()

    def plot3Images(self, image1, image2, image3):
        # To prevent repetition in subsequent tests.
        plt.figure()

        plt.subplot(221)
        plt.imshow(image1, cmap=plt.cm.gray)
        plt.title("First image")

        plt.subplot(222)
        plt.imshow(image2, cmap=plt.cm.gray)
        plt.title("Second image")

        plt.subplot(223)
        plt.imshow(image3, cmap=plt.cm.gray)
        plt.title("Third image")
        plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95,
                            hspace=0.25, wspace=0.35)

        plt.show()

    @envtest.skip("Skip plots")
    def testGamma1(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaHigh.jpg", as_gray=True)
        adjustedImage = adjust_gamma(grayImage)
        self.plotImageComparison(grayImage, adjustedImage)
        # looks pretty much unchanged...

    @envtest.skip("Skip plots")
    def testGamma2(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaHigh.jpg", as_gray=True)
        adjustedImage = adjust_gamma(grayImage, gamma=2)
        self.plotImageComparison(grayImage, adjustedImage)
        # looks better!!!

    @envtest.skip("Skip plots")
    def testLog_gain1(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaHigh.jpg", as_gray=True)
        adjustedImage = adjust_log(grayImage)
        self.plotImageComparison(grayImage, adjustedImage)
        # almost looks the same...

    @envtest.skip("Skip plots")
    def testLog_gain2(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaHigh.jpg", as_gray=True)
        adjustedImage = adjust_log(grayImage, gain=2)
        self.plotImageComparison(grayImage, adjustedImage)
        # looks a bit more blurry...

    @envtest.skip("Skip plots")
    def testLog_gain5(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaHigh.jpg", as_gray=True)
        adjustedImage = adjust_log(grayImage, gain=5)
        self.plotImageComparison(grayImage, adjustedImage)
        # looks a bit more blurry...

    @envtest.skip("Skip plots")
    def testLogGamma_gamma1_log1(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaHigh.jpg", as_gray=True)
        adjustedGamma = adjust_gamma(grayImage, gamma=1)
        adjustedlog = adjust_log(adjustedGamma, gain=1)
        self.plot3Images(grayImage, adjustedGamma, adjustedlog)
        # wayyyy too subtle

    @envtest.skip("Skip plots")
    def testLogGamma_gamma2_log1(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaHigh.jpg", as_gray=True)
        adjustedGamma = adjust_gamma(grayImage, gamma=2)
        adjustedlog = adjust_log(adjustedGamma, gain=1)
        self.plot3Images(grayImage, adjustedGamma, adjustedlog)
        # gamma 2 is not subtle. Log1 is visible a bit.

    @envtest.skip("Skip plots")
    def testLogGamma_gamma2_log10(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaHigh.jpg", as_gray=True)
        adjustedGamma = adjust_gamma(grayImage, gamma=2)
        adjustedlog = adjust_log(adjustedGamma, gain=10)
        self.plot3Images(grayImage, adjustedGamma, adjustedlog)
        # Even log 10 seems pretty subtle... let's try with another image.

    @envtest.skip("Skip plots")
    def testLogGamma_gamma2_log10_lowLight1(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaLow.jpg", as_gray=True)
        adjustedGamma = adjust_gamma(grayImage, gamma=2)
        adjustedlog = adjust_log(adjustedGamma, gain=10)
        self.plot3Images(grayImage, adjustedGamma, adjustedlog)
        # Log 10 makes close to no change... let's try with another image.

    @envtest.skip("Skip plots")
    def testLogGamma_gamma2_log10_midLight(self):
        grayImage = imread(self.testCannyDirectory+"/bresilMedium.jpg", as_gray=True)
        adjustedGamma = adjust_gamma(grayImage, gamma=2)
        adjustedlog = adjust_log(adjustedGamma, gain=10)
        self.plot3Images(grayImage, adjustedGamma, adjustedlog)
        # Log correction still looks very subtle... probably not useful for
        # what I want to do. I'll try one last picture with it.

    @envtest.skip("Skip plots")
    def testLogGamma_gamma2_log10_highLight(self):
        grayImage = imread(self.testCannyDirectory+"/bresilHigh.jpg", as_gray=True)
        adjustedGamma = adjust_gamma(grayImage, gamma=2)
        adjustedlog = adjust_log(adjustedGamma, gain=10)
        self.plot3Images(grayImage, adjustedGamma, adjustedlog)
        # Log correction looks like it smoothes transitions between light
        # levels, which I do not want. I will thus not use it at all.

if __name__ == "__main__":
    envtest.main()
