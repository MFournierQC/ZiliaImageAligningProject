import envtest
from skimage.io import imread
from skimage.filters import threshold_otsu as otsu
from processImages import getFiles
import matplotlib.pyplot as plt
import numpy as np

"""
WARNING: this test file will use absolute paths for data, which are necessary
due to the large amount of data that will be analyzed. These HAVE to be changed
to the correct paths if run on another copmuter.
"""

listOfFolderPaths = []

# These ones are very saturated
listOfFolderPaths.append(r"E:\Baseline3\Kenya 1512692\20210316-142504-kenya-od-onh-rlp24")
listOfFolderPaths.append(r"E:\Baseline3\Kenya 1512692\20210316-145131-kenya-os-onh-rlp24")
listOfFolderPaths.append(r"E:\Baseline3\Rwanda 1512436\20210317-092821-rwanda-od-onh-rlp24")
listOfFolderPaths.append(r"E:\Baseline3\Rwanda 1512436\20210317-092951-rwanda-od-onh-rlp24")
listOfFolderPaths.append(r"E:\Baseline3\Somalie 1508202\20210317-134930-somalie-od-onh-rlp24")
listOfFolderPaths.append(r"E:\Baseline3\Somalie 1508202\20210317-134957-somalie-od-onh-rlp24")
listOfFolderPaths.append(r"E:\Baseline3\Somalie 1508202\20210317-140843-somalie-os-onh-rlp24gooooodim")
listOfFolderPaths.append(r"E:\Baseline3\Somalie 1508202\20210317-140927-somalie-os-onh-rlp24gooooodim")
listOfFolderPaths.append(r"E:\Baseline3\Somalie 1508202\20210317-141034-somalie-os-onh-rlp24gooooodim")
listOfFolderPaths.append(r"E:\Baseline3\Somalie 1508202\20210317-141109-somalie-os-onh-rlp24gooooodim")
listOfFolderPaths.append(r"E:\Baseline3\Somalie 1508202\20210317-141139-somalie-os-onh-rlp24gooooodim")
# listOfFolderPaths.append(r"")


@envtest.skip("Will fail on other computers if path is not changed.")
class TestFindAverageThresholdHiBrightness(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertTrue(True)

    def testListOfFolderPaths(self):
        # print(listOfFolderPaths)
        self.assertTrue(len(listOfFolderPaths) > 0)

    def testGetFiles(self):
        eyesAndRosas = getFiles(listOfFolderPaths[0])
        # print(eyesAndRosas)
        self.assertTrue(len(eyesAndRosas) > 0)

    @envtest.skip("skip plots")
    def testPlotHistogram(self):
        fakeData = [1,1,1,1,2,2,3,3,4,4,4,5,5,6,6,7,7,8,9,7,8,9]
        plt.hist(fakeData, bins='auto')
        plt.show()

    def testGetMeanOfList(self):
        fakeData = [1,1,1,1,2,2,3,3,4,4,4,5,5,6,6,7,7,8,9,7,8,9]
        mean = np.mean(fakeData)
        # print(mean) #4.681818181818182

    def getOnlyRetinaImages(self, directory):
        # I only need to analyze the threshold of retina images, not rosa.
        images = getFiles(directory)
        retinaImages = []
        for image in images:
            if "rosa" in image.lower():
                # skip this image
                continue
            else:
                # keep the retina images
                retinaImages.append(image)
        return retinaImages

    def testGetOnlyEyeFiles(self):
        testDir = listOfFolderPaths[0]
        self.assertTrue(len(testDir) > 0)
        retinaImages = self.getOnlyRetinaImages(testDir)
        self.assertTrue(len(retinaImages) > 1)
        # print(retinaImages)
        for image in retinaImages:
            if "rosa" in image:
                self.assertFalse(True)
            else:
                self.assertTrue(True)

    def testGetThresholdOfOneEyeFile(self):
        testDir = listOfFolderPaths[0]
        retinaImages = self.getOnlyRetinaImages(testDir)
        image = imread(retinaImages[0], as_gray=True)
        self.assertTrue(len(image.shape) == 2)
        thresh = otsu(image)
        # print(thresh) # 0.5726463051470588

    def testGetMeanThresholdOfAFewFiles(self):
        testDir = listOfFolderPaths[0]
        retinaImages = self.getOnlyRetinaImages(testDir)
        testImages = []
        for image in retinaImages[:7]:
            grayImage = imread(image, as_gray=True)
            self.assertTrue(len(grayImage.shape) == 2)
            testImages.append(grayImage)
        self.assertTrue(len(testImages) == 7)

    def testLoadAFewFiles(self):
        testDir = listOfFolderPaths[0]
        retinaImages = self.getOnlyRetinaImages(testDir)
        testImages = []
        for image in retinaImages[:7]:
            grayImage = imread(image, as_gray=True)
            self.assertTrue(len(grayImage.shape) == 2)
            testImages.append(grayImage)
        self.assertTrue(len(testImages) == 7)

    def testGetMeanThresholdOfAFewFiles(self):
        testDir = listOfFolderPaths[0]
        retinaImages = self.getOnlyRetinaImages(testDir)
        testImages = []
        thresholds = []
        for image in retinaImages[:7]:
            grayImage = imread(image, as_gray=True)
            thresh = otsu(grayImage)
            testImages.append(grayImage)
            thresholds.append(thresh)
        self.assertTrue(len(thresholds) == len(testImages) == 7)
        # print(thresholds)
        mean = np.mean(thresholds)
        # print(mean) # 0.5780243949142158

    @envtest.skip("Long computing time, and skip plots")
    def testGetMeanThresholdOfWholeFolder(self):
        testDir = listOfFolderPaths[0]
        retinaImages = self.getOnlyRetinaImages(testDir)
        testImages = []
        thresholds = []
        for image in retinaImages:
            grayImage = imread(image, as_gray=True)
            thresh = otsu(grayImage)
            testImages.append(grayImage)
            thresholds.append(thresh)
        self.assertTrue(len(thresholds) == len(retinaImages) > 1)
        # print(len(thresholds))
        # print(thresholds)
        mean = np.mean(thresholds)
        # print(mean) # 0.5685028310973513
        plt.hist(thresholds, bins='auto')
        plt.show()

    @envtest.skip("Long computing time, and skip plots")
    def testGetMeanThresholdOf2Folders(self):
        testDirs = listOfFolderPaths[:2]
        self.assertTrue(len(testDirs) == 2)
        thresholds = []
        for directory in testDirs:
            retinaImages = self.getOnlyRetinaImages(directory)
            for image in retinaImages:
                grayImage = imread(image, as_gray=True)
                thresh = otsu(grayImage)
                thresholds.append(thresh)
        mean = np.mean(thresholds)
        std = np.std(thresholds)
        stdx2 = 2*std
        print("mean = ", mean) # 0.5225092022756542
        print("std = ", std) # 0.07512258531403286
        print("stdx2 = ", stdx2) # 0.15024517062806572
        plt.hist(thresholds, bins='auto')
        plt.show()

    @envtest.skip("Long computing time, and skip plots")
    def testGetMeanThresholdOfAllFolders(self):
        testDirs = listOfFolderPaths
        thresholds = []
        for directory in testDirs:
            retinaImages = self.getOnlyRetinaImages(directory)
            for image in retinaImages:
                grayImage = imread(image, as_gray=True)
                thresh = otsu(grayImage)
                thresholds.append(thresh)
        mean = np.mean(thresholds)
        std = np.std(thresholds)
        stdx2 = 2*std
        print("mean = ", mean) # 0.5301227941321696
        print("std = ", std) # 0.08200880979293632
        print("stdx2 = ", stdx2) # 0.16401761958587263
        plt.hist(thresholds, bins='auto')
        plt.show()
        # I think 1 std will be enough to catch the most saturated images...


if __name__ == "__main__":
    envtest.main()
