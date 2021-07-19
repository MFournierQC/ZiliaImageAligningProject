import envtest
import cv2
from skimage.io import imread
from skimage.filters import threshold_otsu
from skimage.feature import canny
from skimage.draw import ellipse
from skimage.exposure import adjust_gamma
from skimage.color import rgb2gray
import matplotlib.pyplot as plt
import numpy as np
from ellipse import LsqEllipse
from matplotlib.patches import Ellipse


class TestLsqEllipse(envtest.ZiliaTestCase):

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
    def testCannyGrayEllipse(self):
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

    def testLSQEllipseImport(self):
        self.assertIsNotNone(LsqEllipse)

    @envtest.skip("skip plots and prints")
    def testLsqEllipse_HorizontalEllipseImage(self):
        # This test is directly based on the example found here:
        # https://github.com/bdhammel/least-squares-ellipse-fitting
        testImage = self.testCannyDirectory+"/testPerfectBinaryEllipse.png"
        colorImage = imread(testImage)
        image = imread(testImage, as_gray=True)
        thresh = threshold_otsu(image)
        binaryImage = image > thresh
        canniedImage = canny(binaryImage)

        # Get index pairs of the contours:
        X, Y = np.where(canniedImage == True)
        indexes = np.array(list(zip(X, Y)))
        # print(indexes)

        reg = LsqEllipse().fit(indexes)
        self.assertIsNotNone(reg)
        center, width, height, phi = reg.as_parameters()
        [yCenter, xCenter] = center
        print("center:", center) # [64.77547671811857, 112.93235984883405]
        print("width:", width) # 32.33031473568739 This is the vertical axis
        print("height:", height) # 53.940531246424094 this is the horizontal axis
        print("phi:", phi) # 0.00013424143672583532 this is almost == 0
        # I think the "width" is, in fact, the minor axis and the "height" is
        # the major axis (WRONG! See next tests)

        cy, cx = ellipse(int(yCenter), int(xCenter), int(width), int(height), rotation=phi)
        canniedImage[cy, cx] = 130
        image[cy, cx] = 255
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(canniedImage, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(colorImage)
        plt.show()

    @envtest.skip("skip plots and prints")
    def testLsqEllipse_VerticalEllipseImage(self):
        testImage = self.testStudentDirectory+"/testImage3.png"
        colorImage = imread(testImage)
        image = imread(testImage, as_gray=True)
        thresh = threshold_otsu(image)
        binaryImage = image > thresh
        canniedImage = canny(binaryImage)

        # Get index pairs of the contours:
        X, Y = np.where(canniedImage == True)
        indexes = np.array(list(zip(X, Y)))
        # print(indexes)

        reg = LsqEllipse().fit(indexes)
        self.assertIsNotNone(reg)
        center, width, height, phi = reg.as_parameters()
        [yCenter, xCenter] = center
        print("center:", center) # [82.3802224537652, 170.2780107167497]
        print("width:", width) # 41.1606929880854 This is the vertical axis
        print("height:", height) # 34.02078884419442 this is the horizontal axis
        print("phi:", phi) # 0.005528654260259732 this is almost == 0
        # It looks like "width" is the half length of the axis normal to the
        # angle. Height is the half length of the axis parallel to the angle.

        cy, cx = ellipse(int(yCenter), int(xCenter), int(width), int(height), rotation=phi)
        canniedImage[cy, cx] = 130
        image[cy, cx] = 255
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(canniedImage, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(colorImage)
        plt.show()

    @envtest.skip("skip plots and prints")
    def testLsqEllipse_AngledEllipseImage5(self):
        testImage = self.testStudentDirectory+"/testImage5.png"
        colorImage = imread(testImage)
        image = imread(testImage, as_gray=True)
        thresh = threshold_otsu(image)
        binaryImage = image > thresh
        canniedImage = canny(binaryImage)

        # Get index pairs of the contours:
        X, Y = np.where(canniedImage == True)
        indexes = np.array(list(zip(X, Y)))
        # print(indexes)

        reg = LsqEllipse().fit(indexes)
        self.assertIsNotNone(reg)
        center, width, height, phi = reg.as_parameters()
        [yCenter, xCenter] = center
        print("center:", center) # [46.792511360088255, 102.45029016530684]
        print("width:", width) # 24.409772295496847
        print("height:", height) # 48.72489440636081
        print("phi:", phi) # 0.36668821755544195
        # YES! It looks like "width" is the half length of the axis normal to
        # the angle. Height is the half length of the axis parallel to the angle.

        cy, cx = ellipse(int(yCenter), int(xCenter), int(width), int(height), rotation=phi)
        canniedImage[cy, cx] = 130
        image[cy, cx] = 255
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(canniedImage, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(colorImage)
        plt.show()

    @envtest.skip("skip plots and prints")
    def testLsqEllipse_AngledEllipseImage6(self):
        testImage = self.testStudentDirectory+"/testImage6.png"
        colorImage = imread(testImage)
        image = imread(testImage, as_gray=True)
        thresh = threshold_otsu(image)
        binaryImage = image > thresh
        canniedImage = canny(binaryImage)

        # Get index pairs of the contours:
        X, Y = np.where(canniedImage == True)
        indexes = np.array(list(zip(X, Y)))
        # print(indexes)

        reg = LsqEllipse().fit(indexes)
        self.assertIsNotNone(reg)
        center, width, height, phi = reg.as_parameters()
        [yCenter, xCenter] = center
        print("center:", center) # [72.74021686048583, 133.815298340835]
        print("width:", width) # 26.48914913767351
        print("height:", height) # 56.634102159997255
        print("phi:", phi) # -0.35672971896029765
        # YES YES! I confirm "width" is the half length of the axis normal to
        # the angle, and Height is the half length of the axis parallel to the
        # angle. I will have to rename them in the final code.
        # Also, the fact that the angle is negative tells me it most likely
        # ranges from -pi/2 to pi/2.

        cy, cx = ellipse(int(yCenter), int(xCenter), int(width), int(height), rotation=phi)
        canniedImage[cy, cx] = 130
        image[cy, cx] = 255
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(canniedImage, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(colorImage)
        plt.show()

    @envtest.skip("skip plots")
    def testLsqEllipse_bresilMedium(self):
        testImage = self.testCannyDirectory+"/bresilMedium.jpg"
        colorImage = imread(testImage)
        image = imread(testImage, as_gray=True)
        thresh = threshold_otsu(image)
        binaryImage = image > thresh
        canniedImage = canny(binaryImage)

        # Get index pairs of the contours:
        X, Y = np.where(canniedImage == True)
        indexes = np.array(list(zip(X, Y)))
        # print(indexes)

        reg = LsqEllipse().fit(indexes)
        self.assertIsNotNone(reg)
        center, normalHalfAx, parallelHalfAx, phi = reg.as_parameters()
        [yCenter, xCenter] = center
        print("center:", center) # [627.4181525824515, 422.9409439110012]
        print("normalHalfAx:", normalHalfAx) # 221.492203402924
        print("parallelHalfAx:", parallelHalfAx) # 185.90812860271694
        print("phi:", phi) # -0.3855460868035675

        cy, cx = ellipse(int(yCenter), int(xCenter), int(normalHalfAx), int(parallelHalfAx), rotation=phi)
        canniedImage[cy, cx] = 130
        image[cy, cx] = 255
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(canniedImage, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(colorImage)
        plt.show()
        # Very good!!!

    @envtest.skip("skip plots")
    def testLsqEllipse_bresilHigh(self):
        testImage = self.testCannyDirectory+"/bresilHigh.jpg"
        colorImage = imread(testImage)
        image = imread(testImage, as_gray=True)
        image = adjust_gamma(image, gamma=100)
        thresh = threshold_otsu(image)
        binaryImage = image > thresh
        canniedImage = canny(binaryImage)

        # Get index pairs of the contours:
        X, Y = np.where(canniedImage == True)
        indexes = np.array(list(zip(X, Y)))

        reg = LsqEllipse().fit(indexes)
        self.assertIsNotNone(reg)
        center, normalHalfAx, parallelHalfAx, phi = reg.as_parameters()
        [yCenter, xCenter] = center

        cy, cx = ellipse(int(yCenter), int(xCenter), int(normalHalfAx), int(parallelHalfAx), rotation=phi)
        canniedImage[cy, cx] = 130
        image[cy, cx] = 255
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(canniedImage, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(colorImage)
        plt.show()
        # Without gamma correction, TERRIBLE.
        # Less bad with gamma==2.
        # Better with gamma==3, but still too big.
        # Really great with gamma==100!!!

    @envtest.skip("skip plots")
    def testLsqEllipse_kenyaLow(self):
        testImage = self.testCannyDirectory+"/kenyaLow.jpg"
        colorImage = imread(testImage)
        image = imread(testImage, as_gray=True)
        # image = adjust_gamma(image, gamma=50)
        thresh = threshold_otsu(image)
        binaryImage = image > thresh
        canniedImage = canny(binaryImage)

        # Get index pairs of the contours:
        X, Y = np.where(canniedImage == True)
        indexes = np.array(list(zip(X, Y)))

        reg = LsqEllipse().fit(indexes)
        self.assertIsNotNone(reg)
        center, normalHalfAx, parallelHalfAx, phi = reg.as_parameters()
        [yCenter, xCenter] = center

        cy, cx = ellipse(int(yCenter), int(xCenter), int(normalHalfAx), int(parallelHalfAx), rotation=phi)
        canniedImage[cy, cx] = 130
        image[cy, cx] = 255
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(canniedImage, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(colorImage)
        plt.show()
        # Without gamma correction, not too shaby!!!
        # Not better with higher gamma.

    @envtest.skip("skip plots")
    def testLsqEllipse_partiallyCut(self):
        testImage = self.testCannyDirectory+"/partiallyCut.jpg"
        colorImage = imread(testImage)
        image = imread(testImage, as_gray=True)
        image = adjust_gamma(image, gamma=3.5)
        thresh = threshold_otsu(image)
        binaryImage = image > thresh
        canniedImage = canny(binaryImage)

        # Get index pairs of the contours:
        X, Y = np.where(canniedImage == True)
        indexes = np.array(list(zip(X, Y)))

        reg = LsqEllipse().fit(indexes)
        self.assertIsNotNone(reg)
        center, normalHalfAx, parallelHalfAx, phi = reg.as_parameters()
        [yCenter, xCenter] = center

        cy, cx = ellipse(int(yCenter), int(xCenter), int(normalHalfAx), int(parallelHalfAx), rotation=phi)
        canniedImage[cy, cx] = 130
        image[cy, cx] = 255
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(canniedImage, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(colorImage)
        plt.show()
        # Without gamma correction, BEURK!
        # With gamma=3.5, less worse, but anything below that detects too much.

    @envtest.skip("skip plots")
    def testLsqEllipse_partiallyCut_NoBlueChannel(self):
        # I'll try to remove the blue channel to see if it's better...
        testImage = self.testCannyDirectory+"/partiallyCut.jpg"
        colorImage = imread(testImage)
        colorImageRed = colorImage[:,:,0]
        colorImageGreen = colorImage[:,:,1]
        self.assertTrue(len(colorImage[:,:,0].shape) == 2)
        colorImageBlue = np.zeros(colorImage[:,:,0].shape)
        colorImageNoBlue = np.dstack((colorImageRed, colorImageGreen, colorImageBlue))
        image = rgb2gray(colorImageNoBlue)

        image = adjust_gamma(image, gamma=4)
        thresh = threshold_otsu(image)
        binaryImage = image > thresh
        canniedImage = canny(binaryImage)

        # Get index pairs of the contours:
        X, Y = np.where(canniedImage == True)
        indexes = np.array(list(zip(X, Y)))

        reg = LsqEllipse().fit(indexes)
        self.assertIsNotNone(reg)
        center, normalHalfAx, parallelHalfAx, phi = reg.as_parameters()
        [yCenter, xCenter] = center

        cy, cx = ellipse(int(yCenter), int(xCenter), int(normalHalfAx), int(parallelHalfAx), rotation=phi)
        canniedImage[cy, cx] = 130
        image[cy, cx] = 255
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(canniedImage, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(colorImage)
        plt.show()
        # Without gamma correction, BEURK!
        # With gamma from about 3.3 to 4, "usable"... kind of...

    # @envtest.skip("skip plots")
    def testLsqEllipse_noONH(self):
        testImage = self.testCannyDirectory+"/noONH.jpg"
        colorImage = imread(testImage)
        image = imread(testImage, as_gray=True)
        image = adjust_gamma(image, gamma=50)
        thresh = threshold_otsu(image)
        binaryImage = image > thresh
        canniedImage = canny(binaryImage)

        # Get index pairs of the contours:
        X, Y = np.where(canniedImage == True)
        indexes = np.array(list(zip(X, Y)))

        reg = LsqEllipse().fit(indexes)
        self.assertIsNotNone(reg)
        center, normalHalfAx, parallelHalfAx, phi = reg.as_parameters()
        [yCenter, xCenter] = center

        cy, cx = ellipse(int(yCenter), int(xCenter), int(normalHalfAx), int(parallelHalfAx), rotation=phi)
        canniedImage[cy, cx] = 130
        image[cy, cx] = 255
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(canniedImage, cmap="gray")
        plt.subplot(1,2,2)
        plt.imshow(colorImage)
        plt.show()
        # Kind of finds an ONH that doesn't exist at high gammas...
        # but there's an almost oval bright spot in the image, so it's not
        # easy...

if __name__ == "__main__":
    envtest.main()
