import envtest
from skimage.io import imread
from skimage.color import rgb2gray
from scipy.stats.mstats import ttest_ind as ttest
from scipy.stats import ttest_ind as ttest2

class TestStudentTest(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertTrue(True)

    def testImportTestImages(self):
        testDir = self.testStudentDirectory
        image1 = imread(testDir+"/testImage1.png")
        self.assertIsNotNone(image1)
        self.assertTrue(len(image1.shape) == 3)
        image2 = imread(testDir+"/testImage2.png")
        self.assertIsNotNone(image2)
        self.assertTrue(len(image2.shape) == 3)
        image3 = imread(testDir+"/testImage3.png")
        self.assertIsNotNone(image3)
        self.assertTrue(len(image3.shape) == 3)

    def setUp(self):
        # will be called before each test
        super().setUp()
        testDir = self.testStudentDirectory
        self.image1 = imread(testDir+"/testImage1.png")
        self.image2 = imread(testDir+"/testImage2.png")
        self.image3 = imread(testDir+"/testImage3.png")

    def testPerfectCorrelationOnSimpleNumbers(self):
        tvalue, pvalue = ttest([1,2,3,4,5,6,7,8,9,10], [1,2,3,4,5,6,7,8,9,10])
        # print("tvalue = ", tvalue) # 0.0 == perfect correlation
        # print("pvalue = ", pvalue) # 1.0

    def testPerfectCorrelationOnRGBImages(self):
        tvalue, pvalue = ttest(self.image1, self.image1)
        # print("tvalue = ", tvalue)
        # print("pvalue = ", pvalue)
        # this outputs weird arrays... let's try a grayimage instead...

    def testPerfectCorrelationOnGrayImages(self):
        tvalue, pvalue = ttest(rgb2gray(self.image1), rgb2gray(self.image1))
        # print("tvalue = ", tvalue)
        # print("pvalue = ", pvalue)
        # It looks like it gives a sample by sample result for each pixel
        # individually... not really what I want... I want one number for the
        # tvalue, and one number for the pvalue...

    def testTtest2OnSimpleNumber(self):
        tvalue, pvalue = ttest2([1,2,3,4,5,6,7,8,9,10], [1,2,3,4,5,6,7,8,9,10])
        # print("tvalue = ", tvalue) # 0.0
        # print("pvalue = ", pvalue) # 1.0
        # Same as ttest1 so far.

    def testTtest2OnRGBImages(self):
        tvalue, pvalue = ttest(self.image1, self.image1)
        # print("tvalue = ", tvalue)
        # print("pvalue = ", pvalue)
        # Same as Ttest1...



if __name__ == "__main__":
    envtest.main()
