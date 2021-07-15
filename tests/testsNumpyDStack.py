import envtest
import numpy as np
import matplotlib.pyplot as plt

class TestNumpyDStack(envtest.ZiliaTestCase):

	def testInit(self):
		self.assertTrue(True)

	@envtest.skip("skip plots")
	def testMake2DImage(self):
		image = np.array([[135, 140],[240, 0]])
		self.assertIsNotNone(image)
		plt.imshow(image)
		plt.show()

	@envtest.expectedFailure
	def testMatplotlibDoesntAcceptImagesWith2ColorChannels(self):
		image = np.array([[135, 140],[240, 0]])
		image2 = np.array([[0, 0],[0, 255]])
		self.assertIsNotNone(image2)
		finalImage = np.dstack((image, image2), axis=2)
		plt.imshow(finalImage)

	@envtest.skip("skip plots")
	def testDStackInstead(self):
		image = np.array([[135, 140],[240, 0]])
		image2 = np.array([[0, 0],[0, 255]])
		self.assertIsNotNone(image2)
		finalImage = np.dstack((image, image, image2))
		print(finalImage.shape)
		plt.imshow(finalImage)
		plt.show()

	def testIndexPickElements(self):
		# just to make elements are arranged how I think they are
		image = np.array([[135, 140],[240, 0]])
		image2 = np.array([[0, 0],[0, 255]])
		finalImage = np.dstack((image, image, image2))
		self.assertTrue(finalImage[1,1,2] == 255)
		self.assertTrue(finalImage[0,0,2] == finalImage[0,1,2] == finalImage[1,0,2] == 0)
		self.assertTrue(finalImage[0,1,0] == 140)
		# Ok, just how I thought, indexes are [vertical, horizontal, thinckness].

if __name__ == "__main__":
	envtest.main()
