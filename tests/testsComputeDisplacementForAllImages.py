import envtest
from processImages import *
from getImageDisplacementData import *
from zilia import *

dir1 = r"Z:\labdata\dcclab\zilia\March2021\Baseline 3\Bresil 1511184\20210316-095955-bresil-od-onh-rlp2"
dir2 = r"Z:\labdata\dcclab\zilia\March2021\Baseline 3\Bresil 1511184\20210316-100153-bresil-od-onh-rlp6"

class TestComputeDisplacementForAllImages(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertTrue(True)

    def testComputeDisplacementForAllImages(self):
        pass

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
