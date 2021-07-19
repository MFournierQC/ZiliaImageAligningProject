import envtest
from cv2 import fitEllipse, findContours
import cv2
from skimage.io import imread
from skimage.filters import threshold_otsu
from skimage.feature import canny
from skimage.draw import ellipse
from skimage.exposure import adjust_gamma
import matplotlib.pyplot as plt
import numpy as np
from ellipse import LsqEllipse
from matplotlib.patches import Ellipse

class TestCV2FitEllipse(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertIsNotNone(fitEllipse)

    def testImportTestImage(self):
        testImage = self.testCannyDirectory+"/testPerfectBinaryEllipse.png"
        image = imread(testImage)
        self.assertIsNotNone(image)
        self.assertTrue(len(image.shape) == 3)

    def testImportGrayTestImage(self):
        testImage = self.testCannyDirectory+"/testPerfectBinaryEllipse.png"
        image = imread(testImage, as_gray=True)
        self.assertIsNotNone(image)
        self.assertTrue(len(image.shape) == 2)

    @envtest.skip("skip plots")
    def testThreshGrayEllipse(self):
        testImage = self.testCannyDirectory+"/testPerfectBinaryEllipse.png"
        image = imread(testImage, as_gray=True)
        thresh = threshold_otsu(image)
        binaryImage = image < thresh
        self.assertIsNotNone(image)
        self.assertTrue(len(binaryImage.shape) == 2)
        self.assertTrue(image.shape == binaryImage.shape)
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(image, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(binaryImage, cmap="gray")
        plt.show()

    @envtest.skip("skip plots")
    def testThreshGrayRetina(self):
        testImage = self.testCannyDirectory+"/bresilMedium.jpg"
        image = imread(testImage, as_gray=True)
        thresh = threshold_otsu(image)
        binaryImage = image > thresh
        self.assertIsNotNone(image)
        self.assertTrue(len(binaryImage.shape) == 2)
        self.assertTrue(image.shape == binaryImage.shape)
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(image, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(binaryImage, cmap="gray")
        plt.show()

    @envtest.skip("skip plots")
    def testThreshGrayEllipse(self):
        testImage = self.testCannyDirectory+"/testPerfectBinaryEllipse.png"
        image = imread(testImage, as_gray=True)
        thresh = threshold_otsu(image)
        binaryImage = image < thresh
        canniedImage = canny(binaryImage)
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(image, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(canniedImage, cmap="gray")
        plt.show()

    @envtest.skip("skip plots")
    def testCannyGrayRetina(self):
        testImage = self.testCannyDirectory+"/bresilMedium.jpg"
        image = imread(testImage, as_gray=True)
        thresh = threshold_otsu(image)
        binaryImage = image > thresh
        canniedImage = canny(binaryImage)
        self.assertIsNotNone(canniedImage)
        self.assertTrue(image.shape == canniedImage.shape)
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(image, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(canniedImage, cmap="gray")
        plt.show()

    def testExecuteFitEllipseOnCanniedImage(self):
        testImage = self.testCannyDirectory+"/testPerfectBinaryEllipse.png"
        image = cv2.imread(testImage, cv2.IMREAD_GRAYSCALE)
        thresh = threshold_otsu(image)
        binaryImage = image > thresh
        canniedImage = canny(binaryImage)
        contours, _ = findContours(image, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
        self.assertIsNotNone(contours)
        # print(contours)
        # print("len contours =", len(contours))
        ellipse = fitEllipse(contours[0])
        self.assertIsNotNone(ellipse)
        # print(ellipse)

    @envtest.skip("skip plots")
    def testPlotFittedEllipse(self):
        testImage = self.testCannyDirectory+"/testPerfectBinaryEllipse.png"
        image = cv2.imread(testImage, cv2.IMREAD_GRAYSCALE)
        thresh = threshold_otsu(image)
        binaryImage = image > thresh
        canniedImage = canny(binaryImage)
        contours, _ = findContours(image, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
        ellipse = fitEllipse(contours[0])
        image = np.zeros((image.shape[0], image.shape[1], 3))
        imageWithEllipse = cv2.ellipse(image, ellipse, (0,0,255))
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(canniedImage, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(imageWithEllipse, cmap="gray")
        plt.show()
        # Résultat épouvantable!!!

if __name__ == "__main__":
    envtest.main()
