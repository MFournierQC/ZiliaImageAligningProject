import envtest
import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu
from skimage.io import imread
from skimage.color import rgb2gray
import numpy as np
from skimage.data import coffee
from skimage.draw import ellipse_perimeter, ellipse
from skimage.transform import hough_ellipse
from skimage.feature import canny
from skimage import color, img_as_ubyte
from skimage.transform import resize
from skimage.exposure import adjust_gamma
import time

class TestHoughEllipse(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertTrue(True)

    def testCoffee(self):
        image = coffee()
        self.assertIsNotNone(image)
        # plt.imshow(image)
        # plt.show()

    def testCropCoffee(self):
        image = coffee()[0:220, 160:420]
        self.assertIsNotNone(image)
        # plt.imshow(image)
        # plt.show()

    def testGrayscaleCoffee(self):
        image = coffee()
        grayImage = rgb2gray(image)
        self.assertIsNotNone(grayImage)
        # plt.imshow(grayImage, cmap=plt.cm.gray)
        # plt.show()

    def testOtsuThreshOnCoffee(self):
        image = coffee()
        grayImage = rgb2gray(image)
        thresh = threshold_otsu(grayImage)
        binaryImage = grayImage > thresh
        self.assertIsNotNone(binaryImage)
        # plt.imshow(binaryImage, cmap=plt.cm.gray)
        # plt.show()
        # Pretty bad, might not be a good reference for what we want to do
        # because there are much more color intensitites than in the
        # retina images...

    def testImreadGrayscaleOption(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaMedium.jpg", as_gray=True)
        self.assertIsNotNone(grayImage)
        self.assertTrue(len(grayImage.shape) == 2)

    def testDifferentGrayscaleMethods(self):
        image = imread(self.testCannyDirectory+"/kenyaMedium.jpg")
        grayImage1 = rgb2gray(image)
        grayImage2 = imread(self.testCannyDirectory+"/kenyaMedium.jpg", as_gray=True)
        equality = np.equal(grayImage1, grayImage2)
        self.assertTrue(equality.all())

    def testOtsuThreshOnMidLightRetina(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaMedium.jpg", as_gray=True)
        thresh = threshold_otsu(grayImage)
        binaryImage = grayImage > thresh
        self.assertIsNotNone(binaryImage)
        # plt.imshow(binaryImage, cmap=plt.cm.gray)
        # plt.show()

    def testOtsuThreshAndCanntOnMidLightRetina(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaMedium.jpg", as_gray=True)
        thresh = threshold_otsu(grayImage)
        binaryImage = grayImage > thresh
        canniedImage = canny(binaryImage)
        self.assertIsNotNone(canniedImage)
        # plt.imshow(canniedImage, cmap=plt.cm.gray)
        # plt.show()
        # Very good :)

    @envtest.skip("Way too long, about 157 seconds! I'll change default parameters to optimize.")
    def testHoughEllipseDefaultParameters(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaMedium.jpg", as_gray=True)
        thresh = threshold_otsu(grayImage)
        binaryImage = grayImage > thresh
        cannied = canny(binaryImage)
        houghResults = hough_ellipse(cannied)
        # plt.imshow(cannied, cmap=plt.cm.gray)
        # plt.show()
        # houghResults.sort(order="accumulator")

    def testImageShape(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaMedium.jpg", as_gray=True)
        shape = grayImage.shape
        self.assertIsNotNone(shape)
        self.assertTrue(len(shape) == 2)
        self.assertTrue(shape[0] < shape[1])
        # So the first dimension is the height,
        # and the second one is the width.

    @envtest.skip("Still too long, but about 60 seconds shorter than without ellipse parameter!")
    def testHoughEllipseWithChosenEllipseParameters(self):
        grayImage = imread(self.testCannyDirectory+"/kenyaMedium.jpg", as_gray=True)
        thresh = threshold_otsu(grayImage)
        binaryImage = grayImage > thresh
        canniedImage = canny(binaryImage)
        xSize = grayImage.shape[0]
        ySize = grayImage.shape[1]
        minMajorAxis = int((1/6)*ySize)
        maxMinorAxis = int(0.5*xSize)
        houghResults = hough_ellipse(canniedImage, min_size=minMajorAxis, max_size=maxMinorAxis)
        # Took about 96 seconds

    def plotEllipseResult(self, best, imageRgb, edges):
        # Code taken from an example in the scikit-image documentation.
        yc, xc, a, b = [int(round(x)) for x in best[1:5]]
        orientation = best[5]
        # Draw the ellipse on the original image
        cy, cx = ellipse_perimeter(yc, xc, a, b, orientation)
        imageRgb[cy, cx] = (0, 0, 255)
        # Draw the edge (white) and the resulting ellipse (red)
        edges = color.gray2rgb(img_as_ubyte(edges))
        edges[cy, cx] = (250, 0, 0)
        fig2, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=(8, 4),
                                        sharex=True, sharey=True)
        ax1.set_title('Original picture')
        ax1.imshow(imageRgb)
        ax2.set_title('Edge (white) and result (red)')
        ax2.imshow(edges)
        plt.show()

    def evaluateHoughEllipseFullSizePicture(self, fileName, accuracy=1, minMajorAxisScale=1/6, maxMinorAxisScale=0.5, threshold=4):
        # To prevent repetition of this code.
        imageRgb = imread(self.testCannyDirectory+"/"+fileName)
        grayImage = imread(self.testCannyDirectory+"/"+fileName, as_gray=True)
        thresh = threshold_otsu(grayImage)
        binaryImage = grayImage > thresh
        canniedImage = canny(binaryImage)
        xSize = grayImage.shape[0]
        ySize = grayImage.shape[1]
        minMajorAxis = int(minMajorAxisScale*ySize)
        maxMinorAxis = int(maxMinorAxisScale*xSize)
        houghResult = hough_ellipse(canniedImage, min_size=minMajorAxis,
            max_size=maxMinorAxis, accuracy=accuracy, threshold=threshold)
        houghResult.sort(order='accumulator')
        # Estimated parameters for the ellipse
        best = list(houghResult[-1])
        return best, imageRgb, canniedImage

    @envtest.skip("Skip the plots and the calculating time.")
    def testAccuracyParameter100(self):
        # Default accuracy == 1. Let's try 100, which should be extremely high.
        fileName = "/kenyaMedium.jpg"
        best, imageRgb, canniedImage = self.evaluateHoughEllipseFullSizePicture(fileName, accuracy=100)
        self.plotEllipseResult(best, imageRgb, canniedImage)
        # this test barely took about 14 seconds, but the result looks
        # like a straight line, which is very bad.

    @envtest.skip("Skip the plots and the calculating time.")
    def testAccuracyParameter50(self):
        # Default accuracy == 1. Let's try 50.
        startTime = time.time()
        fileName = "/kenyaMedium.jpg"
        best, imageRgb, canniedImage = self.evaluateHoughEllipseFullSizePicture(fileName, accuracy=50)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime)# 12.88 s
        self.plotEllipseResult(best, imageRgb, canniedImage)
        # Was pretty fast, and result looks pretty good, but not as much as 
        # accuracy 1...

    @envtest.skip("Skip the plots and the calculating time.")
    def testAccuracyParameter75(self):
        # Default accuracy == 1. Let's try 75.
        fileName = "/kenyaMedium.jpg"
        best, imageRgb, canniedImage = self.evaluateHoughEllipseFullSizePicture(fileName, accuracy=75)
        self.plotEllipseResult(best, imageRgb, canniedImage)
        # Looks like a circle.

    @envtest.skip("Skip the plots and the calculating time.")
    def testAccuracyParameter85(self):
        # Trying to find the limit before it becomes a straight line.
        fileName = "/kenyaMedium.jpg"
        best, imageRgb, canniedImage = self.evaluateHoughEllipseFullSizePicture(fileName, accuracy=85)
        self.plotEllipseResult(best, imageRgb, canniedImage)
        # Looks like a broken straight line.

    @envtest.skip("Skip the plots and the calculating time.")
    def testAccuracyParameter90(self):
        # Trying to look beyond the limits.
        fileName = "/kenyaMedium.jpg"
        best, imageRgb, canniedImage = self.evaluateHoughEllipseFullSizePicture(fileName, accuracy=90)
        self.plotEllipseResult(best, imageRgb, canniedImage)
        # Looks like a perfect line, beurk.

    @envtest.skip("Skip the plots and the calculating time.")
    def testAccuracyParameter60(self):
        # Test lower limits to the algorithm
        startTime = time.time()
        fileName = "/kenyaMedium.jpg"
        best, imageRgb, canniedImage = self.evaluateHoughEllipseFullSizePicture(fileName, accuracy=60)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime) # 12.9 s
        self.plotEllipseResult(best, imageRgb, canniedImage)
        # Is too close to a circle

    @envtest.skip("Skip the plots and the calculating time.")
    def testAccuracyParameter40(self):
        # Test lower limits to the algorithm
        startTime = time.time()
        fileName = "/kenyaMedium.jpg"
        best, imageRgb, canniedImage = self.evaluateHoughEllipseFullSizePicture(fileName, accuracy=40)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime) # 12.97 s
        self.plotEllipseResult(best, imageRgb, canniedImage)
        # less good than 50...

    @envtest.skip("Skip the plots and the calculating time.")
    def testAccuracyParameter30(self):
        # Test lower limits to the algorithm
        startTime = time.time()
        fileName = "/kenyaMedium.jpg"
        best, imageRgb, canniedImage = self.evaluateHoughEllipseFullSizePicture(fileName, accuracy=30)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime)# 13.14 s
        self.plotEllipseResult(best, imageRgb, canniedImage)
        # much better than 40!

    @envtest.skip("Skip the plots and the calculating time.")
    def testAccuracyParameter20(self):
        # Test lower limits to the algorithm
        startTime = time.time()
        fileName = "/kenyaMedium.jpg"
        best, imageRgb, canniedImage = self.evaluateHoughEllipseFullSizePicture(fileName, accuracy=20)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime)# 13.26 s
        self.plotEllipseResult(best, imageRgb, canniedImage)
        # better than 30!

    @envtest.skip("Skip the plots and the calculating time.")
    def testAccuracyParameter10(self):
        # Test lower limits to the algorithm
        startTime = time.time()
        fileName = "/kenyaMedium.jpg"
        best, imageRgb, canniedImage = self.evaluateHoughEllipseFullSizePicture(fileName, accuracy=10)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime)# 14.42 s
        self.plotEllipseResult(best, imageRgb, canniedImage)
        # very good

    @envtest.skip("Skip the plots and the calculating time.")
    def testAccuracyParameter5(self):
        # Test lower limits to the algorithm
        startTime = time.time()
        fileName = "/kenyaMedium.jpg"
        best, imageRgb, canniedImage = self.evaluateHoughEllipseFullSizePicture(fileName, accuracy=5)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime)# 16.82 s
        self.plotEllipseResult(best, imageRgb, canniedImage)
        # looks like a circle... very bad... why, though???

    @envtest.skip("Skip the plots and the calculating time.")
    def testAccuracyParameter3(self):
        # Test lower limits to the algorithm
        startTime = time.time()
        fileName = "/kenyaMedium.jpg"
        best, imageRgb, canniedImage = self.evaluateHoughEllipseFullSizePicture(fileName, accuracy=3)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime)# 22.48 s
        self.plotEllipseResult(best, imageRgb, canniedImage)
        # Another ugly circle... ok... bad...

    @envtest.skip("Skip the plots and the calculating time.")
    def testAccuracyParameter2(self):
        # Test lower limits to the algorithm
        startTime = time.time()
        fileName = "/kenyaMedium.jpg"
        best, imageRgb, canniedImage = self.evaluateHoughEllipseFullSizePicture(fileName, accuracy=2)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime)# 33.55 s
        self.plotEllipseResult(best, imageRgb, canniedImage)
        # Another ugly circle... ok... bad...

    @envtest.skip("Wayyyyy too long, never finishes... longer than 15 minutes!!!")
    def testHighLightPictureRwandaHighDefaultThreshold(self):
        # Default accuracy == 1. Let's try 50.
        startTime = time.time()
        fileName = "/rwandaHigh.jpg"
        best, imageRgb, canniedImage = self.evaluateHoughEllipseFullSizePicture(fileName, accuracy=50)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime)# 12.88 s
        self.plotEllipseResult(best, imageRgb, canniedImage)
        # Way too long... I never got it to even finish... longer than 15 minutes!!!

    @envtest.skip("Skip plots")
    def testCannyHighResPic(self):
        grayImage = imread(self.testCannyDirectory+"/rwandaHigh.jpg", as_gray=True)
        thresh = threshold_otsu(grayImage)
        binaryImage = grayImage > thresh
        canniedImage = canny(binaryImage)
        plt.imshow(canniedImage, cmap=plt.cm.gray)
        plt.show()

    @envtest.skip("Skip plots")
    def testSkimageResizeWithAntiAliasingScaleFactor5(self):
        startTime = time.time()
        grayImage = imread(self.testCannyDirectory+"/rwandaHigh.jpg", as_gray=True)
        thresh = threshold_otsu(grayImage)
        binaryImage = grayImage > thresh
        canniedImage = canny(binaryImage)
        smallGrayImage = resize(grayImage, (grayImage.shape[0]//5, grayImage.shape[1]//5), anti_aliasing=True)
        smallThresh = threshold_otsu(smallGrayImage)
        smallBinaryImage = smallGrayImage > smallThresh
        smallCanny = canny(smallBinaryImage)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime) # = 0.4966716766357422

        fig2, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=(8, 4))
        ax1.set_title('Original size')
        ax1.imshow(canniedImage, cmap=plt.cm.gray)
        ax2.set_title('Small one')
        ax2.imshow(smallCanny, cmap=plt.cm.gray)
        plt.show()

    @envtest.skip("Skip plots")
    def testSkimageResizeWithoutAntiAliasingScaleFactor5(self):
        startTime = time.time()
        grayImage = imread(self.testCannyDirectory+"/rwandaHigh.jpg", as_gray=True)
        thresh = threshold_otsu(grayImage)
        binaryImage = grayImage > thresh
        canniedImage = canny(binaryImage)
        smallGrayImage = resize(grayImage, (grayImage.shape[0]//5, grayImage.shape[1]//5))
        smallThresh = threshold_otsu(smallGrayImage)
        smallBinaryImage = smallGrayImage > smallThresh
        smallCanny = canny(smallBinaryImage)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime) # = 0.483705997467041

        fig2, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=(8, 4))
        ax1.set_title('Original size')
        ax1.imshow(canniedImage, cmap=plt.cm.gray)
        ax2.set_title('Small one')
        ax2.imshow(smallCanny, cmap=plt.cm.gray)
        plt.show()
        # Doesn't seem to make any difference... and computing time is almost
        # the same...

    def evaluateHoughEllipseWithRescale(self, fileName, accuracy=1, minMajorAxisScale=1/6, maxMinorAxisScale=0.5, threshold=4, scaleFactor=5, showSmallCanny=False, gamma=0):
        # To prevent repetition in subsequent tests.
        imageRgb = imread(self.testCannyDirectory+"/"+fileName)
        grayImage = imread(self.testCannyDirectory+"/"+fileName, as_gray=True)
        if gamma != 0:
            grayImage = adjust_gamma(grayImage, gamma=gamma)
        thresh = threshold_otsu(grayImage)
        binaryImage = grayImage > thresh
        canniedImage = canny(binaryImage)

        smallGrayImage = resize(grayImage, (grayImage.shape[0]//scaleFactor, grayImage.shape[1]//scaleFactor))
        if gamma != 0:
            smallGrayImage = adjust_gamma(smallGrayImage, gamma=gamma)
        smallThresh = threshold_otsu(smallGrayImage)
        smallBinaryImage = smallGrayImage > smallThresh
        smallCanniedImage = canny(smallBinaryImage)
        if showSmallCanny:
            plt.imshow(smallCanniedImage, cmap=plt.cm.gray)
            plt.show()

        xSize = smallGrayImage.shape[0]
        ySize = smallGrayImage.shape[1]
        minMajorAxis = int(minMajorAxisScale*ySize)
        maxMinorAxis = int(maxMinorAxisScale*xSize)

        houghResult = hough_ellipse(smallCanniedImage, min_size=minMajorAxis,
            max_size=maxMinorAxis, accuracy=accuracy, threshold=threshold)
        houghResult.sort(order='accumulator')
        # Estimated parameters for the ellipse
        smallBest = list(houghResult[-1])
        return smallBest, imageRgb, canniedImage

    def plotHoughEllipseWithRescale(self, smallBest, imageRgb, canniedImage, scaleFactor=5):
        # To prevent repetition in subsequent tests.
        yc, xc, a, b = [int(round(x)*scaleFactor) for x in smallBest[1:5]]
        print("amin =", a)
        print("bmax =", b)
        orientation = smallBest[5]
        print(orientation)
        # Draw the ellipse on the original image
        cy, cx = ellipse_perimeter(yc, xc, a, b, orientation)
        cye, cxe = ellipse(yc, xc, a, b, rotation=np.pi-orientation)
        imageRgbe = np.array(imageRgb)
        imageRgb[cy, cx] = (0, 0, 255)
        # Draw the edge (white) and the resulting ellipse (red)
        canniedImage = color.gray2rgb(img_as_ubyte(canniedImage))
        canniedImage[cy, cx] = (250, 0, 0)
        fig2, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=(8, 4),
                                        sharex=True, sharey=True)
        ax1.set_title('Original picture')
        ax1.imshow(imageRgb)
        ax2.set_title('Edge (white) and result (red)')
        ax2.imshow(canniedImage)
        plt.show()

        imageRgbe[cye, cxe] = (0, 0, 255)
        canniedImagee = color.gray2rgb(img_as_ubyte(canniedImage))
        canniedImagee[cye, cxe] = (250, 0, 0)
        fig2, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=(8, 4),
                                        sharex=True, sharey=True)
        ax1.set_title('Original picture')
        ax1.imshow(imageRgbe)
        ax2.set_title('Edge (white) and result (red)')
        ax2.imshow(canniedImagee)
        plt.show()

    @envtest.skip("Skip plots")
    def testHighLightPictureRwandaRescale50Accuracy(self):
        startTime = time.time()
        fileName = "rwandaHigh.jpg"
        scaleFactor = 5
        smallBest, imageRgb, canniedImage = self.evaluateHoughEllipseWithRescale(fileName, accuracy=50, scaleFactor=scaleFactor)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime)# 9.97 s
        self.plotHoughEllipseWithRescale(smallBest, imageRgb, canniedImage, scaleFactor=scaleFactor)
        # Way faster!!! But the accuracy has to be readjusted :)

    @envtest.skip("Skip plots")
    def testHighLightPictureRwandaRescale25Accuracy(self):
        startTime = time.time()
        fileName = "rwandaHigh.jpg"
        scaleFactor = 5
        smallBest, imageRgb, canniedImage = self.evaluateHoughEllipseWithRescale(fileName, accuracy=25, scaleFactor=scaleFactor)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime)# 9.97 s
        self.plotHoughEllipseWithRescale(smallBest, imageRgb, canniedImage, scaleFactor=scaleFactor)
        # This accuracy is better, but not as good as I would
        # like it to be, so I'll try decreasing it even more.

    @envtest.skip("Skip plots")
    def testHighLightPictureRwandaRescale15Accuracy(self):
        startTime = time.time()
        fileName = "rwandaHigh.jpg"
        scaleFactor = 5
        smallBest, imageRgb, canniedImage = self.evaluateHoughEllipseWithRescale(fileName, accuracy=15, scaleFactor=scaleFactor)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime) # 10.37 s
        self.plotHoughEllipseWithRescale(smallBest, imageRgb, canniedImage, scaleFactor=scaleFactor)
        # Better :)

    @envtest.skip("Skip plots")
    def testMidLightPictureBresilRescale15Accuracy(self):
        startTime = time.time()
        fileName = "bresilMedium.jpg"
        scaleFactor = 5
        smallBest, imageRgb, canniedImage = self.evaluateHoughEllipseWithRescale(fileName, accuracy=15, scaleFactor=scaleFactor)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime) # 4.15 s
        self.plotHoughEllipseWithRescale(smallBest, imageRgb, canniedImage, scaleFactor=scaleFactor)
        # Better :)

    @envtest.skip("Skip plots")
    def testMidLightPictureBresilRescaleAccuracy15ScaleFactor10(self):
        startTime = time.time()
        fileName = "bresilMedium.jpg"
        scaleFactor = 10
        smallBest, imageRgb, canniedImage = self.evaluateHoughEllipseWithRescale(fileName, accuracy=15, scaleFactor=scaleFactor, showSmallCanny=True)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime) # 2.85 s
        self.plotHoughEllipseWithRescale(smallBest, imageRgb, canniedImage, scaleFactor=scaleFactor)
        # Very good, and VERY FAAAAASSSTTTT

    @envtest.skip("Skip plots")
    def testHighLightPictureKenyaRescaleAccuracy15ScaleFactor10(self):
        startTime = time.time()
        fileName = "kenyaHigh.jpg"
        scaleFactor = 10
        smallBest, imageRgb, canniedImage = self.evaluateHoughEllipseWithRescale(fileName, accuracy=15, scaleFactor=scaleFactor)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime) # 2.70 s
        self.plotHoughEllipseWithRescale(smallBest, imageRgb, canniedImage, scaleFactor=scaleFactor)
        # Very bad, Otsu's threshold cannot stand it.

    @envtest.skip("Skip plots")
    def testHighLightPictureKenyaRescaleAccuracy15ScaleFactor5(self):
        startTime = time.time()
        fileName = "kenyaHigh.jpg"
        scaleFactor = 5
        smallBest, imageRgb, canniedImage = self.evaluateHoughEllipseWithRescale(fileName, accuracy=15, scaleFactor=scaleFactor)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime) # 16.25 s
        self.plotHoughEllipseWithRescale(smallBest, imageRgb, canniedImage, scaleFactor=scaleFactor)
        # Very bad, Otsu's threshold cannot stand it.

    @envtest.skip("Skip plots")
    def testLowLightPictureRwandaRescaleAccuracy15ScaleFactor10(self):
        startTime = time.time()
        fileName = "rwandaLow.jpg"
        scaleFactor = 10
        smallBest, imageRgb, canniedImage = self.evaluateHoughEllipseWithRescale(fileName, accuracy=15, scaleFactor=scaleFactor)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime) # 1.16 s
        self.plotHoughEllipseWithRescale(smallBest, imageRgb, canniedImage, scaleFactor=scaleFactor)
        # Looks like a offset circle even with multiple accuracies.
        # The image is very dim, tough...

    @envtest.skip("Skip plots")
    def testMidLightPictureKenyaRescaleAccuracy15ScaleFactor5(self):
        startTime = time.time()
        fileName = "kenyaMedium.jpg"
        scaleFactor = 5
        smallBest, imageRgb, canniedImage = self.evaluateHoughEllipseWithRescale(fileName, accuracy=10, scaleFactor=scaleFactor)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime) # 0.33 s
        self.plotHoughEllipseWithRescale(smallBest, imageRgb, canniedImage, scaleFactor=scaleFactor)
        # Accuracy 15 = baaaaadddd beurk!
        # Accuracy 10 = very good :)

    @envtest.skip("Skip plots")
    def testLowLightPictureRwandaRescaleFactor5(self):
        startTime = time.time()
        fileName = "rwandaLow.jpg"
        scaleFactor = 5
        smallBest, imageRgb, canniedImage = self.evaluateHoughEllipseWithRescale(fileName, accuracy=10, scaleFactor=scaleFactor, showSmallCanny=True)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime)
        self.plotHoughEllipseWithRescale(smallBest, imageRgb, canniedImage, scaleFactor=scaleFactor)
        # Good!

    @envtest.skip("Skip plots")
    def testHighLightPictureKenyaRescaleFactor5_withGamma5(self):
        startTime = time.time()
        fileName = "kenyaHigh.jpg"
        scaleFactor = 5
        smallBest, imageRgb, canniedImage = self.evaluateHoughEllipseWithRescale(fileName, accuracy=10, scaleFactor=scaleFactor, showSmallCanny=True, gamma=5)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime)
        self.plotHoughEllipseWithRescale(smallBest, imageRgb, canniedImage, scaleFactor=scaleFactor)
        # Not perfect with accuracy 10, but not bad thanks to gamma 5!!!

    @envtest.skip("Color jams the plot")
    def testPerfectBinaryEllipse(self):
        startTime = time.time()
        fileName = "testPerfectBinaryEllipse.png"
        scaleFactor = 1
        smallBest, imageRgb, canniedImage = self.evaluateHoughEllipseWithRescale(fileName, accuracy=10, scaleFactor=scaleFactor, showSmallCanny=True, gamma=5)
        totalAlgorithmTime = time.time() - startTime
        print(totalAlgorithmTime)
        self.plotHoughEllipseWithRescale(smallBest, imageRgb, canniedImage, scaleFactor=scaleFactor)
        # Angle of about pi, small axis still small and big one still bigger.

if __name__ == "__main__":
    envtest.main()
