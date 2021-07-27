import envtest
from processImages import *
from getImageDisplacementData import *
from zilia import *

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
        grayImagesDict = db.getRGBImagesWithPaths(region="onh", content="rosa", limit=10)
        self.assertIsInstance(grayImagesDict, dict)
        self.assertEqual(len(grayImagesDict), 10)
        for path in grayImagesDict.keys():
            self.assertIn("rosa", path)

    def testComputeRosaAbsolutePosition(self):
        pass

    # def testComputeDisplacementForAllImages(self):

    # @envtest.skip("Works fine, but skip file creation please.")
    # def testSave2Folders(self):
    #     dir1 = r".\TestImages\miniTestSampleNewData"
    #     dir2 = r".\TestImages\testAlignment"
    #     dirPaths = [dir1, dir2]
    #     for i in range(len(dirPaths)):
    #         data = computeDisplacementForAllImages(dirPaths[i])
    #         saveImageData(data, fileName="displacementDataTest")

    # @envtest.skip("Works fine, but skip file creation please.")
    # def testComputeDisplacementFor2OnhFolders(self):
    #     dataPath = "Z:/labdata/dcclab/zilia"
    #     sys.path.insert(0, dataPath)

    #     df = pd.read_csv("onhpaths.csv")
    #     paths = df["path"].to_list()
    #     dirPaths = paths[:2]
    #     for i in range(len(dirPaths)):
    #         data = computeDisplacementForAllImages(dirPaths[i])
    #         saveImageData(data, fileName="displacementDataTestOn2Folders")

if __name__=="__main__":
    envtest.main()
