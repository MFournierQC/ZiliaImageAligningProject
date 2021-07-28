import envtest
from skimage.io import imread
import matplotlib.pyplot as plt
from processImages import *
from getImageDisplacementData import *
from zilia import *

showPlots = False
# showPlots = True

class TestComputeDisplacementForAllImages(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertTrue(True)

    def testGetRGBImagesFromDatabase(self):
        db = ZiliaDB()
        grayImagesDict = db.getRGBImagesWithPaths(limit=10)
        self.assertIsInstance(grayImagesDict, dict)
        self.assertEqual(len(grayImagesDict), 10)

    def testGetRGBOnhImagesFromDatabase(self):
        db = ZiliaDB()
        grayImagesDict = db.getRGBImagesWithPaths(region="onh", limit=10)
        self.assertIsInstance(grayImagesDict, dict)
        self.assertEqual(len(grayImagesDict), 10)
        # print(grayImagesDict)

    def testGetOnlyRosaImagesFromDatabase(self):
        db = ZiliaDB()
        rosaImagesDict = db.getRGBImagesWithPaths(region="onh", content="rosa", limit=10)
        self.assertIsInstance(rosaImagesDict, dict)
        self.assertEqual(len(rosaImagesDict), 10)
        for path in rosaImagesDict.keys():
            self.assertIn("rosa", path)

    def testComputeRosaAbsolutePosition(self):
        rosaImage = imread(self.testFilesDirectory+"/001-rosa.jpg")
        blobDict = findLaserSpot(rosaImage)
        self.assertIsNotNone(blobDict)
        # print(blobDict)
        rosaX = blobDict['center']['rx']
        rosaY = blobDict['center']['ry']
        if showPlots:
            plt.imshow(rosaImage)
            plt.plot([rosaX], [rosaY],'o')
            plt.show()
        # This worked wonderfully!

    @envtest.skip("needs to be readapted to the new code output.")
    def testComputeRosaPositionFor1RosaImage(self):
        db = ZiliaDB()
        rosaImagesDict = db.getRGBImagesWithPaths(region="onh", content="rosa", limit=3)
        self.assertEqual(len(rosaImagesDict), 3)
        rosaAbsX, rosaAbsY = computeRosaPositionForAllImages(rosaImagesDict)
        self.assertEqual(len(rosaAbsX), 3)
        self.assertEqual(len(rosaAbsY), 3)
        for path, value in rosaAbsX.items():
            self.assertIsInstance(path, str)
            try:
                self.assertIsInstance(value, int)
            except AssertionError:
                self.assertIsInstance(value, str)
        # print('rosaAbsX =', rosaAbsX)
        # print('rosaAbsY =', rosaAbsY)
        # Worked perfectly!

    @envtest.skip("needs to be readapted to the new code output.")
    def testComputeRosaPositionFor3RosaImages(self):
        db = ZiliaDB()
        rosaImagesDict = db.getRGBImagesWithPaths(region="onh", content="rosa", limit=3)
        self.assertEqual(len(rosaImagesDict), 3)
        rosaAbsX, rosaAbsY = computeRosaPositionForAllImages(rosaImagesDict)
        self.assertEqual(len(rosaAbsX), 3)
        self.assertEqual(len(rosaAbsY), 3)
        for path, value in rosaAbsX.items():
            self.assertIsInstance(path, str)
            try:
                self.assertIsInstance(value, int)
            except AssertionError:
                self.assertIsInstance(value, str)
        # print('rosaAbsX =', rosaAbsX)
        # print('rosaAbsY =', rosaAbsY)
        # Worked perfectly!


    @envtest.skip("Works fine, but skip file creation please.")
    def testSaveFolders(self):
        pass

if __name__=="__main__":
    envtest.main()
