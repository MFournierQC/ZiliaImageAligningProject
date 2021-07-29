import envtest
from skimage.io import imread
import matplotlib.pyplot as plt
from processImages import *
from getImageDisplacementData import *
from zilia import *

# Global variables to decide if some tests will run or not.
showPlots = False

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

    def testComputeRosaPositionFor3RosaImages(self):
        db = ZiliaDB()
        rosaImagesDict = db.getRGBImagesWithPaths(region="onh", content="rosa", limit=3)
        self.assertEqual(len(rosaImagesDict), 3)
        rosaAbsCoords: dict = computeRosaPositionForAllImages(rosaImagesDict)
        self.assertEqual(len(rosaAbsCoords), 3)
        for path, coords in rosaAbsCoords.items():
            self.assertIsInstance(path, str)
            self.assertIsInstance(coords, tuple)
            try:
                self.assertIsInstance(coords[0], int)
            except AssertionError:
                self.assertIsInstance(coords[0], str)
            try:
                self.assertIsInstance(coords[1], int)
            except AssertionError:
                self.assertIsInstance(coords[1], str)
        # print('rosaAbsCoords =', rosaAbsCoords)
        # Worked perfectly!

    def testSaveRosaDataFor1Image(self):
        db = ZiliaDB()
        rosaImagesDict = db.getRGBImagesWithPaths(region="onh", content="rosa", limit=1)
        self.assertEqual(len(rosaImagesDict), 1)
        rosaAbsCoords: dict = computeRosaPositionForAllImages(rosaImagesDict)
        self.assertEqual(len(rosaAbsCoords), 1)
        # print('rosaAbsCoords =', rosaAbsCoords)
        saveRosaData(rosaAbsCoords, fileName="rosaDisplacementDataTest1")

    def testSaveRosaDataFor1ImageTwiceInARow(self):
        # This test is necessary because the function saveRosaData will behave
        # a bit differently if a data file already exists or not.
        db = ZiliaDB()
        rosaImagesDict = db.getRGBImagesWithPaths(region="onh", content="rosa", limit=1)
        self.assertEqual(len(rosaImagesDict), 1)
        rosaAbsCoords: dict = computeRosaPositionForAllImages(rosaImagesDict)
        self.assertEqual(len(rosaAbsCoords), 1)
        # print('rosaAbsCoords =', rosaAbsCoords)
        saveRosaData(rosaAbsCoords, fileName="rosaDisplacementDataTest1")
        saveRosaData(rosaAbsCoords, fileName="rosaDisplacementDataTest1")

    def testSaveRosaDataFor3Images(self):
        db = ZiliaDB()
        rosaImagesDict = db.getRGBImagesWithPaths(region="onh", content="rosa", limit=3)
        self.assertEqual(len(rosaImagesDict), 3)
        rosaAbsCoords: dict = computeRosaPositionForAllImages(rosaImagesDict)
        self.assertEqual(len(rosaAbsCoords), 3)
        # print('rosaAbsCoords =', rosaAbsCoords)
        saveRosaData(rosaAbsCoords, fileName="rosaDisplacementDataTest2")

    def testSaveRosaDataFor10Images(self):
        db = ZiliaDB()
        rosaImagesDict = db.getRGBImagesWithPaths(region="onh", content="rosa", limit=10)
        self.assertEqual(len(rosaImagesDict), 10)
        rosaAbsCoords: dict = computeRosaPositionForAllImages(rosaImagesDict)
        self.assertEqual(len(rosaAbsCoords), 10)
        # print('rosaAbsCoords =', rosaAbsCoords)
        saveRosaData(rosaAbsCoords, fileName="rosaDisplacementDataTest3")

    @envtest.skip("Very long test!")
    def testGetNumberOfRosaImages(self):
        db = ZiliaDB()
        rosaImagesDict = db.getRGBImagesWithPaths(region="onh", content="rosa")
        print("number of rosa =", len(rosaImagesDict)) # 16599 files!

    # @envtest.skip("Very long test!")
    def testSaveRosaDataForAllImages(self):
        db = ZiliaDB()
        rosaImagesDict = db.getRGBImagesWithPaths(region="onh", content="rosa")
        rosaAbsCoords: dict = computeRosaPositionForAllImages(rosaImagesDict)
        saveRosaData(rosaAbsCoords, fileName="allRosaDisplacementData")

if __name__=="__main__":
    envtest.main()
