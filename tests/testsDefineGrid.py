import envtest
from processImages import defineGrid
from zilia import *
import numpy as np
from skimage.io import imread
from skimage.color import rgb2gray

def importGrayImageFromPath(imagePath):
    image = imread(imagePath)
    image[:,:,2] = 0 # For eye images, always strip blue channel before conversion
    return rgb2gray(image)


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
        


if __name__=="__main__":
    envtest.main()
