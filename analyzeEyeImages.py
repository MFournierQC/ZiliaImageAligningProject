import numpy as np
from skimage.color import rgb2gray
from skimage.transform import resize, hough_ellipse
from skimage.feature import canny


class EllipseDetector:
    """
    The relative size of the ellipse is defined as a fraction of the largest
    side of the input image.
    Ellipse orientation in radians, counterclockwise.

    This is the order in which this should be used:
        detector = EllipseDetector(image)
        detector.preProcessImage()
        bestEllipse = detector.findBestEllipse()
        (xCenter, yCenter), minorAxis, majorAxis, orientation = bestEllipse
    """
    def __init__(self, image, relativeMinMajorAxis=1/6, relativeMaxMinorAxis=1/3, accuracy=10):
        self.image = image
        self.relativeMinMajorAxis = relativeMinMajorAxis
        self.relativeMaxMinorAxis = relativeMaxMinorAxis
        self.accuracy = accuracy
        if self.imageIsGrayscale():
            self.grayImage = image
        else:
            self.grayImage = rgb2gray(image)

    def imageIsGrayscale(self):
        return len(self.image.shape) == 2

    def preProcessImage(self):
        self.contours = self.applyCannyFilter(self.grayImage)
        ellipseExpectedSize = self.defineEllipseExpectedSize()
        self.minMajorAxis = ellipseExpectedSize[0]
        self.maxMinorAxis = ellipseExpectedSize[1]

    def findBestEllipse(self):
        """
        If no ellipse is found, returns None.
        Else, returns a tuple of the best ellipse parameters.
        """
        bestEllipse = self.getBestHoughEllipseResult(self.contours)
        if bestEllipse is None:
            print("No match was found")
            return None
        (xCenter, yCenter), minorAxis, majorAxis, orientation = bestEllipse
        return bestEllipse

    def getBestHoughEllipseResult(self, contours):
        houghResult = self.applyHoughTransform(contours)
        bestHoughEllipse = self.sortBestHoughEllipse(houghResult)
        bestEllipse = self.getBestEllipseParameters(bestHoughEllipse)
        return bestEllipse

    def applyCannyFilter(self, grayImage):
        return canny(grayImage)

    def defineEllipseExpectedSize(self):
        xSize = self.grayImage.shape[1]
        ySize = self.grayImage.shape[0]
        maxSide = max([xSize, ySize])
        minMajorAxis = int(self.relativeMinMajorAxis*maxSide)
        maxMinorAxis = int(self.relativeMaxMinorAxis*maxSide)
        return minMajorAxis, maxMinorAxis

    def applyHoughTransform(self, contours):
        houghResult = hough_ellipse(contours,
                                    min_size=self.minMajorAxis,
                                    max_size=self.maxMinorAxis,
                                    accuracy=self.accuracy)
        return houghResult

    def sortBestHoughEllipse(self, houghResult):
        houghResult.sort(order='accumulator')
        try:
            best = list(houghResult[-1])
            return best
        except IndexError:
            # No ellipse corresponding to the input parameters was found
            return None

    def getBestEllipseParameters(self, bestHoughEllipse):
        if bestHoughEllipse is None:
            return None
        yCenter, xCenter, minorAxis, majorAxis = [int(round(x)) for x in bestHoughEllipse[1:5]]
        orientation = np.pi - bestHoughEllipse[5]
        return (int(xCenter), int(yCenter)), int(minorAxis), int(majorAxis), orientation


class ZiliaONHDetector(EllipseDetector):
    """
    The relative size of the ellipse is defined as a fraction of the largest
    side of the input image.
    Ellipse orientation in radians, counterclockwise.

    This is the order in which this should be used:
        onhDetector = ZiliaONHDetector(image)
        onhDetector.preProcessImage()
        bestEllipse = onhDetector.findOpticNerveHead()
        (xCenter, yCenter), minorAxis, majorAxis, orientation = bestEllipse
    """
    def __init__(self, image, scaleFactor=5, relativeMinMajorAxis=1/6,
                    relativeMaxMinorAxis=1/3, accuracy=10):
        super().__init__(image, relativeMinMajorAxis, relativeMaxMinorAxis, accuracy)
        self.fullSizeGrayImage = np.array(self.grayImage, copy=True)
        self.scaleFactor = scaleFactor
        self.grayImage = self.getGrayRescaledImage()

    def findOpticNerveHead(self):
        """
        If no ellipse is found, returns None.
        Else, returns a tuple of the best ellipse parameters.
        """
        print("Doing hough transform")
        bestEllipse = self.getBestHoughEllipseResult(self.contours)
        if bestEllipse is None:
            print("No match was found")
            return None
        (xCenter, yCenter), minorAxis, majorAxis, orientation = bestEllipse
        minAxis = min([minorAxis, majorAxis])
        maxAxis = max([minorAxis, majorAxis])
        if self.ellipseHasTheRightSize(minAxis, maxAxis):
            # a match has been found using the Hough transform
            pass
        else:
            return None
        result = self.upscaleResult(bestEllipse)
        return result

    def getGrayRescaledImage(self):
        ySize = self.fullSizeGrayImage.shape[0]//self.scaleFactor
        xSize = self.fullSizeGrayImage.shape[1]//self.scaleFactor
        outputSize = ySize, xSize
        return resize(self.fullSizeGrayImage, outputSize)

    def upscaleResult(self, smallScaleResult):
        (xCenter, yCenter), minAxis, majAxis, orientation = smallScaleResult
        xCenter *= self.scaleFactor
        yCenter *= self.scaleFactor
        minAxis *= self.scaleFactor
        majAxis *= self.scaleFactor
        return (xCenter, yCenter), minAxis, majAxis, orientation
