import numpy as np
from ellipse import LsqEllipse
from skimage.color import rgb2gray
from skimage.transform import resize, hough_ellipse
from skimage.filters import threshold_otsu
from skimage.feature import canny
from skimage.exposure import adjust_gamma


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
    def __init__(self, image, relativeMinMajorAxis=1/6, relativeMaxMinorAxis=1/3,
                    relativeMaxMajorAxis=3/4, relativeMinMinorAxis=1/9, accuracy=10):
        self.image = image
        self.relativeMinMajorAxis = relativeMinMajorAxis
        self.relativeMaxMinorAxis = relativeMaxMinorAxis
        self.relativeMaxMajorAxis = relativeMaxMajorAxis
        self.relativeMinMinorAxis = relativeMinMinorAxis
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
        self.maxMajorAxis = ellipseExpectedSize[2]
        self.minMinorAxis = ellipseExpectedSize[3]

    def findBestEllipse(self):
        """
        If no ellipse is found, returns None.
        Else, returns a tuple of the best ellipse parameters.
        """
        leastSquaresResult = self.getLeastSquaresEllipseFit(self.contours)
        if leastSquaresResult is not None:
            bestEllipse = leastSquaresResult
            return bestEllipse
        else:
            # The least squares algorithm has failed.
            print("Doing hough transform")
            bestEllipse = self.getBestHoughEllipseResult(self.contours)
            if bestEllipse is None:
                print("No match was found")
                return None
            (xCenter, yCenter), minorAxis, majorAxis, orientation = bestEllipse
            minAxis = min([minorAxis, majorAxis])
            maxAxis = max([minorAxis, majorAxis])
            if self.ellipseHasTheRightSize(minAxis, maxAxis):
                return bestEllipse
            print("No match was found")
            return None

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
        maxMajorAxis = int(self.relativeMaxMajorAxis*maxSide)
        minMinorAxis = int(self.relativeMinMinorAxis*maxSide)
        return minMajorAxis, maxMinorAxis, maxMajorAxis, minMinorAxis

    def ellipseHasTheRightSize(self, minAxis, maxAxis):
        minAxis *= 2
        maxAxis *= 2
        if minAxis > self.minMinorAxis:
            if minAxis < self.maxMinorAxis:
                if maxAxis > self.minMajorAxis:
                    if maxAxis < self.maxMajorAxis:
                        return True
        return False

    def doLeastSquaresEllipseFit(self, contours):
        X, Y = np.where(contours == True)
        contoursIndexes = np.array(list(zip(X, Y)))
        lsqFit = LsqEllipse().fit(contoursIndexes)
        lsqResult = lsqFit.as_parameters()
        return lsqResult

    def getLeastSquaresEllipseFit(self, contours):
        gammas = [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 1]
        for gamma in gammas:
            # Try with 16 different gamma values
            lsqResult = self.doLeastSquaresEllipseFit(contours)
            (yCenter, xCenter), normalHalfAx, parallelHalfAx, orientation = lsqResult
            minAxis = min([normalHalfAx, parallelHalfAx])
            maxAxis = max([normalHalfAx, parallelHalfAx])
            if self.ellipseHasTheRightSize(minAxis, maxAxis):
                # Order the parameters before returning them
                if parallelHalfAx > normalHalfAx:
                    majorAxis = parallelHalfAx
                    minorAxis = normalHalfAx
                else:
                    orientation += (np.pi/2)
                    majorAxis = normalHalfAx
                    minorAxis = parallelHalfAx
                bestEllipse = (int(xCenter), int(yCenter)), int(minorAxis), int(majorAxis), orientation
                return bestEllipse
            else:
                if gamma == 1:
                    # stop at last iteration

                    # orientation += (np.pi/2)
                    # majorAxis = normalHalfAx
                    # minorAxis = parallelHalfAx
                    # bestEllipse = (int(xCenter), int(yCenter)), int(minorAxis), int(majorAxis), orientation
                    # return bestEllipse

                    break
                # Apply gamma correction and try again
                correctedImage = self.doGammaCorrection(gamma)
                contours = self.applyCannyFilter(correctedImage)
        # If the code goes here, no ellipse of the expected size was found
        return None

    def doGammaCorrection(self, gamma):
        correctedImage = adjust_gamma(self.grayImage, gamma=gamma)
        return correctedImage

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
        onhDetector.getParamsCorrections(highGamma=3, gammaThresh=0.5)
        onhDetector.preProcessImage()
        bestEllipse = onhDetector.findOpticNerveHead()
        (xCenter, yCenter), minorAxis, majorAxis, orientation = bestEllipse
    """
    def __init__(self, image, scaleFactor=5, gamma=True, relativeMinMajorAxis=1/6,
                    relativeMaxMinorAxis=1/3, relativeMaxMajorAxis=3/4, relativeMinMinorAxis=1/9, accuracy=10):
        super().__init__(image, relativeMinMajorAxis, relativeMaxMinorAxis,
                        relativeMaxMajorAxis, relativeMinMinorAxis, accuracy)
        self.fullSizeGrayImage = np.array(self.grayImage, copy=True)
        self.scaleFactor = scaleFactor
        self.gamma = gamma
        self.grayImage = self.getGrayRescaledImage()
        self.threshold = self.getThreshold()
        self.gammaCorrectedImage = None

    def getParamsCorrections(self, highGamma=3, gammaThresh=0.5):
        self.highGamma = highGamma
        if self.gamma is True:
            # Automatically check if gamma correction is needed
            self.gamma = self.detectGammaNecessity(gammaThresh)
        elif self.gamma is False:
            # Don't apply gamma correction whatsoever
            pass
        elif int(self.gamma) == 1:
            # No need to apply gamma correction
            self.gamma = False
        else:
            # Apply gamma correction with the input gamma value
            self.grayImage = self.doGammaCorrection(self.gamma)

    def preProcessImage(self):
        if self.gamma:
            self.gammaCorrectedImage = self.doGammaCorrection(self.gamma)
        super().preProcessImage()

    def findOpticNerveHead(self):
        """
        If no ellipse is found, returns None.
        Else, returns a tuple of the best ellipse parameters.
        """
        leastSquaresResult = self.getLeastSquaresEllipseFit(self.contours)
        if leastSquaresResult is not None:
            bestEllipse = leastSquaresResult
        else:
            # The least squares algorithm has failed.
            print("Doing hough transform")
            if self.gammaCorrectedImage is not None:
                # gamma correction is needed
                self.grayImage = self.gammaCorrectedImage
                self.contours = self.applyCannyFilter(self.grayImage)
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

    def detectGammaNecessity(self, gammaThresh):
        # Has to be improved with testing!!!
        imageThreshold = self.threshold
        if imageThreshold > gammaThresh:
            gamma = self.highGamma
            print("Gamma automatically applied")
        else:
            gamma = False
        return gamma

    def getGrayRescaledImage(self):
        ySize = self.fullSizeGrayImage.shape[0]//self.scaleFactor
        xSize = self.fullSizeGrayImage.shape[1]//self.scaleFactor
        outputSize = ySize, xSize
        return resize(self.fullSizeGrayImage, outputSize)

    def getThreshold(self):
        # From 0 to 1
        return threshold_otsu(self.grayImage)

    def applyCannyFilter(self, grayImage):
        binaryImage = self.grayImage > self.threshold
        return canny(binaryImage)

    def upscaleResult(self, smallScaleResult):
        (xCenter, yCenter), minAxis, majAxis, orientation = smallScaleResult
        xCenter *= self.scaleFactor
        yCenter *= self.scaleFactor
        minAxis *= self.scaleFactor
        majAxis *= self.scaleFactor
        return (xCenter, yCenter), minAxis, majAxis, orientation
