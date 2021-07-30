import numpy as np
from skimage.color import rgb2gray
from skimage.transform import resize, hough_ellipse
from skimage.filters import threshold_otsu
from skimage.feature import canny
from skimage.exposure import adjust_gamma


class EllipseDetector:
    """
    This is the order in which this should be used:
        detector = EllipseDetector(image)
        detector.preProcessImage()
        bestEllipse = detector.findBestEllipse()
        (xCenter, yCenter), minorAxis, majorAxis, orientation = bestEllipse
    """

    def __init__(self, image, relativeMinMajorAxis=1/6, relativeMaxMinorAxis=0.5, accuracy=10):
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
        self.contours = self.applyCannyFilter()
        ellipseExpectedSize = self.defineEllipseExpectedSize()
        self.minMajorAxis = ellipseExpectedSize[0]
        self.maxMinorAxis = ellipseExpectedSize[1]

    def findBestEllipse(self):
        """
        If no ellipse is found, returns None.
        Else, returns a tuple of the best ellipse parameters.
        """
        houghResult = self.applyHoughTransform()
        bestHoughEllipse = self.sortBestHoughEllipse(houghResult)
        bestEllipse = self.getBestEllipseParameters(bestHoughEllipse)
        return bestEllipse

    def applyCannyFilter(self):
        return canny(self.grayImage)

    def defineEllipseExpectedSize(self):
        xSize = self.grayImage.shape[0]
        ySize = self.grayImage.shape[1]
        minMajorAxis = int(self.relativeMinMajorAxis*ySize)
        maxMinorAxis = int(self.relativeMaxMinorAxis*xSize)
        return minMajorAxis, maxMinorAxis

    def applyHoughTransform(self):
        houghResult = hough_ellipse(self.contours,
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
        yc, xc, a, b = [int(round(x)) for x in bestHoughEllipse[1:5]]
        orientation = np.pi - bestHoughEllipse[5]
        yCenter = yc
        xCenter = xc
        minorAxis = a
        majorAxis = b
        return (xCenter, yCenter), minorAxis, majorAxis, orientation


class ZiliaONHDetector(EllipseDetector):
    """
    This is the order in which this should be used:
        onhDetector = ZiliaONHDetector(image)
        onhDetector.getParamsCorrections()
        onhDetector.preProcessImage()
        bestEllipse = onhDetector.findOpticNerveHead()
        (xCenter, yCenter), minorAxis, majorAxis, orientation = bestEllipse
    """

    def __init__(self, image, scaleFactor=3, gamma=True, relativeMinMajorAxis=1/6, relativeMaxMinorAxis=0.5, accuracy=10):
        super(ZiliaONHDetector, self).__init__(image, relativeMinMajorAxis, relativeMaxMinorAxis, accuracy)
        self.fullSizeGrayImage = np.array(self.grayImage, copy=True)
        self.scaleFactor = scaleFactor
        self.gamma = gamma
        self.grayImage = self.getGrayRescaledImage()

    def getParamsCorrections(self, highGamma=3, gammaThresh=0.5):
        """Find the required gamma correction (min=1, max=?)"""
        self.highGamma = highGamma
        if self.gamma is True:
            # Automatically check if gamma correction is needed
            self.gamma = self.detectGammaNecessity(gammaThresh=gammaThresh)
        elif self.gamma is False:
            # Don't apply gamma correction whatsoever
            pass
        elif int(self.gamma) == 1:
            # No need to apply gamma correction
            self.gamma = False
        else:
            # Apply gamma correction with the input gamma value
            self.grayImage = self.adjustGamma()

    def preProcessImage(self):
        self.grayImage = self.adjustGamma()
        self.threshold = self.getThreshold()
        super(ZiliaONHDetector, self).preProcessImage()

    def findOpticNerveHead(self):
        smallScaleResult = super(ZiliaONHDetector, self).findBestEllipse()
        if smallScaleResult is None:
            return smallScaleResult
        else:
            result = self.upscaleResult(smallScaleResult)
            print("bestEllipse =", result)
            return result

    def detectGammaNecessity(self, gammaThresh=0.5):
        # Has to be improved with testing!!!
        tempThresh = self.getThreshold()
        print("tempThresh =", tempThresh)
        if tempThresh > gammaThresh:
            gamma = self.highGamma
            print("gamma done!")
        else:
            gamma = 1
        return gamma

    def adjustGamma(self):
        if self.gamma is False:
            return self.grayImage
        else:
            return adjust_gamma(self.grayImage, gamma=self.gamma)

    def getGrayRescaledImage(self):
        ySize = self.fullSizeGrayImage.shape[0]//self.scaleFactor
        xSize = self.fullSizeGrayImage.shape[1]//self.scaleFactor
        outputSize = ySize, xSize
        return resize(self.fullSizeGrayImage, outputSize)

    def getThreshold(self):
        # Between 0 and 1
        return threshold_otsu(self.grayImage)

    def applyCannyFilter(self):
        binaryImage = self.grayImage > self.threshold
        return canny(binaryImage)

    def upscaleResult(self, smallScaleResult):
        (xCenter, yCenter), minAxis, majAxis, orientation = smallScaleResult
        xCenter = self.scaleFactor*xCenter
        yCenter = self.scaleFactor*yCenter
        minAxis = self.scaleFactor*minAxis
        majAxis = self.scaleFactor*majAxis
        return (xCenter, yCenter), minAxis, majAxis, orientation