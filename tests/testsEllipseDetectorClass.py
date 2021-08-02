import envtest
from analyzeRetinaImages import EllipseDetector
from skimage.io import imread
from skimage.color import rgb2gray, gray2rgb
from skimage import img_as_ubyte
from skimage.draw import ellipse
import matplotlib.pyplot as plt

class TestEllipseDetectorClass(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertTrue(True)

    def testImportImage(self):
        image = imread(self.testCannyDirectory+"/testPerfectBinaryEllipse.png")
        self.assertIsNotNone(image)

    def testCreateDetectorColorImage(self):
        image = imread(self.testCannyDirectory+"/testPerfectBinaryEllipse.png")
        detector = EllipseDetector(image)
        self.assertIsNotNone(detector)
        # print(type(detector))

    def testCreateDetectorGrayImage(self):
        image = imread(self.testCannyDirectory+"/testPerfectBinaryEllipse.png")
        grayImage = rgb2gray(image)
        detector = EllipseDetector(grayImage)
        self.assertIsNotNone(detector)

    @envtest.skip("skip plot")
    def testPreProcessImage(self):
        image = imread(self.testCannyDirectory+"/testPerfectBinaryEllipse.png")
        detector = EllipseDetector(image)
        detector.preProcessImage()
        plt.imshow(detector.contours, cmap="gray")
        plt.show()
        self.assertIsNotNone(detector)

    @envtest.skip("skip computing time")
    def testFindBestEllipse(self):
        image = imread(self.testCannyDirectory+"/testPerfectBinaryEllipse.png")
        detector = EllipseDetector(image)
        detector.preProcessImage()
        result = detector.findBestEllipse()
        self.assertIsNotNone(result)
        for i in result:
            self.assertIsNotNone(i)

    def plotHoughEllipseWithRescale(self, result, imageRgb, canniedImage):
        # To prevent repetition in subsequent tests.
        (xCenter, yCenter), minorAxis, majorAxis, orientation = result
        # Draw the ellipse on the original image
        cy, cx = ellipse(yCenter, xCenter, minorAxis, majorAxis, rotation=orientation)
        imageRgb[cy, cx] = 130
        # Draw the edge (white) and the resulting ellipse (red)
        canniedImage = gray2rgb(img_as_ubyte(canniedImage))
        canniedImage[cy, cx] = (250, 0, 0)
        fig2, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=(8, 4),
                                        sharex=True, sharey=True)
        ax1.set_title('Original picture')
        ax1.imshow(imageRgb)
        ax2.set_title('Edge (white) and result (red)')
        ax2.imshow(canniedImage)
        plt.show()

    @envtest.skip("skip plots")
    def testPlotBestEllipse(self):
        image = imread(self.testCannyDirectory+"/testPerfectBinaryEllipse.png")
        detector = EllipseDetector(image)
        detector.preProcessImage()
        result = detector.findBestEllipse()
        print(result)
        self.plotHoughEllipseWithRescale(result, image, detector.contours)

    @envtest.skip("skip plots")
    def testRotatedEllipse(self):
        image = imread(self.testStudentDirectory+"/testImage5.png")
        detector = EllipseDetector(image)
        detector.preProcessImage()
        result = detector.findBestEllipse()
        print(result)
        self.plotHoughEllipseWithRescale(result, image, detector.contours)

    @envtest.skip("skip plots")
    def testWeirdEllipse(self):
        image = imread(self.testStudentDirectory+"/testImage4.png")
        detector = EllipseDetector(image)
        detector.preProcessImage()
        result = detector.findBestEllipse()
        print(result)
        self.plotHoughEllipseWithRescale(result, image, detector.contours)

if __name__ == "__main__":
    envtest.main()
