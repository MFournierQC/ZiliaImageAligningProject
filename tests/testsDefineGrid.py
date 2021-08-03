import envtest
from processImages import defineGrid
from zilia import *
import numpy as np
from skimage.io import imread
from skimage.color import rgb2gray
import matplotlib.pyplot as plt

showPlots = False
showPlots = True

def importGrayImageFromPath(imagePath):
    image = imread(imagePath)
    image[:,:,2] = 0 # For eye images, always strip blue channel before conversion
    return rgb2gray(image)

def showGridSizeOnGrayPicture(grayImage, gridParams):
    onhCenterX, onhCenterY, gridRegionSize = gridParams
    xLine = [onhCenterX - gridRegionSize, onhCenterX + gridRegionSize]
    yForX = [onhCenterY, onhCenterY]
    yLine = [onhCenterY - gridRegionSize, onhCenterY + gridRegionSize]
    xForY = [onhCenterX, onhCenterX]
    plt.imshow(grayImage, cmap="gray")
    plt.plot(xLine, yForX, "r-")
    plt.plot(xForY, yLine, "r-")
    plt.show()

class TestDefineGrid(envtest.ZiliaTestCase):

    def testImportDefineGrid(self):
        self.assertIsNotNone(defineGrid)

    def testImportImageAsGrayscale(self):
        imagePath = self.testCannyDirectory+"/kenyaLow.jpg"
        grayImage = importGrayImageFromPath(imagePath)
        self.assertIsNotNone(grayImage)
        self.assertEqual(len(grayImage.shape), 2)

    def testDefineGridOnLowLightImage(self):
        imagePath = self.testCannyDirectory+"/kenyaLow.jpg"
        grayImage = importGrayImageFromPath(imagePath)
        gridParams = defineGrid(grayImage, xThresh=0.5, yThresh=0.5, showPlots=showPlots)
        if showPlots:
            showGridSizeOnGrayPicture(grayImage, gridParams)

    def testDefineGridOnLowLightImage1(self):
        # This one is very good
        imagePath = self.testCannyDirectory+"/kenyaLow.jpg"
        grayImage = importGrayImageFromPath(imagePath)
        gridParams = defineGrid(grayImage, xThresh=0.5, yThresh=0.5, showPlots=showPlots)
        if showPlots:
            showGridSizeOnGrayPicture(grayImage, gridParams)


    def testDefineGridOnMidLightImage1(self):
        # Good!
        imagePath = self.testCannyDirectory+"/kenyaMedium.jpg"
        grayImage = importGrayImageFromPath(imagePath)
        gridParams = defineGrid(grayImage, xThresh=0.5, yThresh=0.5, showPlots=showPlots)
        if showPlots:
            showGridSizeOnGrayPicture(grayImage, gridParams)

    def testDefineGridOnMidLightImage2(self):
        # Good!
        imagePath = self.testCannyDirectory+"/somalieMedium.jpg"
        grayImage = importGrayImageFromPath(imagePath)
        gridParams = defineGrid(grayImage, xThresh=0.5, yThresh=0.5, showPlots=showPlots)
        if showPlots:
            showGridSizeOnGrayPicture(grayImage, gridParams)

    def testDefineGridOnMidLightImage3(self):
        # Good!
        imagePath = self.testCannyDirectory+"/rwandaMedium.jpg"
        grayImage = importGrayImageFromPath(imagePath)
        gridParams = defineGrid(grayImage, xThresh=0.4, yThresh=0.4, showPlots=showPlots)
        if showPlots:
            showGridSizeOnGrayPicture(grayImage, gridParams)


    def testDefineGridOnHighLightImage1(self):
        # Good!
        imagePath = self.testCannyDirectory+"/somalieHigh.jpg"
        grayImage = importGrayImageFromPath(imagePath)
        gridParams = defineGrid(grayImage, xThresh=0.6, yThresh=0.6, showPlots=showPlots)
        if showPlots:
            showGridSizeOnGrayPicture(grayImage, gridParams)





    def testDefineGridOnHighLightImage2(self):
        # Good!
        imagePath = self.testCannyDirectory+"/rwandaHigh.jpg"
        grayImage = importGrayImageFromPath(imagePath)
        gridParams = defineGrid(grayImage, xThresh=.7, yThresh=.7, showPlots=showPlots)
        if showPlots:
            showGridSizeOnGrayPicture(grayImage, gridParams)

    def testDefineGridOnLowLightImage2(self):
        # This one has a good grid size, but not good center
        imagePath = self.testCannyDirectory+"/rwandaLow.jpg"
        grayImage = importGrayImageFromPath(imagePath)
        gridParams = defineGrid(grayImage, xThresh=0.35, yThresh=0.35, showPlots=showPlots)
        if showPlots:
            showGridSizeOnGrayPicture(grayImage, gridParams)

    def testDefineGridOnMidLightImage3(self):
        imagePath = self.testCannyDirectory+"/rwandaMedium.jpg"
        grayImage = importGrayImageFromPath(imagePath)
        gridParams = defineGrid(grayImage, xThresh=0.37, yThresh=0.37, showPlots=showPlots)
        if showPlots:
            showGridSizeOnGrayPicture(grayImage, gridParams)

if __name__=="__main__":
    envtest.main()
