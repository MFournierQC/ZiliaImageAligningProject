import numpy as np
from skimage.color import rgb2gray
from skimage.transform import resize

class BrightSpotDetector:

    def __init__(self, image, rescaleFactor=5):
        self.image = image
        if self.imageIsGrayscale():
            self.grayImage = image
        else:
            self.grayImage = rgb2gray(image)
        self.rescaleFactor = rescaleFactor
        self.grayImage = self.getGrayRescaledImage()

    def imageIsGrayscale(self):
        return len(self.image.shape) == 2

    def getBrightSpot(self):
        brightSpotParams = self.findBrightSpot()
        upscaledResult = self.upscaleResult(brightSpotParams)
        return upscaledResult

    def findBrightSpot(self):
        image = self.grayImage
        midIntensity = np.amax(image)
        somme = 0
        sommei = 0
        sommej = 0
        sommei2 = 0
        sommej2 = 0

        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if image[i,j] < midIntensity:
                    # skip low intensities
                    continue
                somme += image[i,j]
                sommei += image[i,j] * i
                sommej += image[i,j] * j
                sommei2 += image[i,j] * (i**2)
                sommej2 += image[i,j] * (j**2)

        imoy = sommei / somme
        jmoy = sommej / somme

        i2moy = sommei2 / somme
        j2moy = sommej2 / somme

        deltai = (i2moy - (imoy)**2)**.5
        deltaj = (j2moy - (jmoy)**2)**.5

        verticAxis = deltai
        horizAxis = deltaj
        xCenter = jmoy
        yCenter = imoy
        return int(yCenter), int(xCenter), verticAxis, horizAxis

    def getGrayRescaledImage(self):
        ySize = self.image.shape[0]//self.rescaleFactor
        xSize = self.image.shape[1]//self.rescaleFactor
        outputSize = ySize, xSize
        return resize(self.grayImage, outputSize)

    def upscaleResult(self, smallScaleResult):
        yCenter, xCenter, verticAxis, horizAxis = smallScaleResult
        xCenter = self.rescaleFactor*xCenter
        yCenter = self.rescaleFactor*yCenter
        verticAxis = self.rescaleFactor*verticAxis
        horizAxis = self.rescaleFactor*horizAxis
        return yCenter, xCenter, verticAxis, horizAxis
