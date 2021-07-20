import envtest
from processImages import doHoughTransform
from skimage.io import imread
from skimage.draw import ellipse

class TestDoHoughTransform(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertTrue(True)

    def testOnRawImage(self):
        image = imread(self.testCannyDirectory+"/bresilMedium.jpg", as_gray=True)
        xCenter, yCenter, minorAxis, majorAxis = doHoughTransform(image)
        imageWithEllipse = np.zeros(image.shape)
        cy, cx = ellipse(yCenter, xCenter, minorAxis, majorAxis, rotation=orientation)
        imageWithEllipse[cy,cx] = 1
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(image)
        plt.subplot(1,2,2)
        plt.imshow(imageWithEllipse, cmap="gray")
        plt.show()

if __name__=="__main__":
    envtest.main()
