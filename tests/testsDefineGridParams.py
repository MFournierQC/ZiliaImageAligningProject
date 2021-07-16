import envtest
from processImages import defineGridParams
from skimage.io import imread
from skimage.color import rgb2gray
import matplotlib.pyplot as plt

skipPlots = True

class TestDefineGridParams(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertIsNotNone(defineGridParams)

    @envtest.skipIf(skipPlots, "skipPlots")
    def testShowGraphsOnBresilMedium(self):
        image = imread(self.testCannyDirectory+"/bresilMedium.jpg")
        image[:,:,2] = 0
        image = rgb2gray(image)
        params = defineGridParams(image)
        xCenterGrid, yCenterGrid, gridLength = params
        for i in params:
            self.assertIsNotNone(i)

    @envtest.skipIf(skipPlots, "skipPlots")
    def testShowGraphsOnBresilMedium2(self):
        image = imread(self.testCannyDirectory+"/bresilMedium.jpg")
        image[:,:,2] = 0
        image = rgb2gray(image)
        params = defineGridParams(image, xThreshConst=.95, yThreshConst=.95)
        xCenterGrid, yCenterGrid, gridLength = params
        print(params) # 366, 641, 4
        plt.imshow(image, cmap="gray")
        plt.plot([xCenterGrid], [yCenterGrid], "o")
        plt.show()

    @envtest.skipIf(skipPlots, "skipPlots")
    def testShowGraphsOnBresilHigh(self):
        image = imread(self.testCannyDirectory+"/bresilHigh.jpg")
        image[:,:,2] = 0
        image = rgb2gray(image)
        params = defineGridParams(image, xThreshConst=.3, yThreshConst=.3)
        xCenterGrid, yCenterGrid, gridLength = params
        print(params) # 422, 365, 4
        plt.imshow(image, cmap="gray")
        plt.plot([xCenterGrid], [yCenterGrid], "o")
        plt.show()

if __name__=="__main__":
    envtest.main()
