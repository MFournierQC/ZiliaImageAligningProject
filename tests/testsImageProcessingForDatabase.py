import envtest
from processImagesFromDatabase import *
from zilia import *
import numpy as np
# skipPlots = True

class TestImageProcessingForDatabase(envtest.ZiliaTestCase):

    def setUp(self):
        super().setUp()
        self.db = ZiliaDB()
        self.assertIsNotNone(self.db)

    def testInit(self):
        self.assertTrue(True)

    def testImportRosaImages(self):
        rosaImages = self.db.getRGBImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                     ,content='rosa',eye='os', limit=10)
        self.assertIsNotNone(rosaImages)
        self.assertTrue(isinstance(rosaImages, list))
        self.assertEqual(len(rosaImages), 10)
        for image in rosaImages:
            self.assertTrue(isinstance(image, np.ndarray))
            self.assertTrue(len(image.squeeze().shape) == 3)
            self.assertTrue((image.squeeze().shape[0]) > 100)
            self.assertTrue((image.squeeze().shape[1]) > 100)
            self.assertTrue((image.squeeze().shape[2]) == 3)
        
    def testGetRosaProperties(self):
        rosaImages = self.db.getRGBImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                     , content='rosa', eye='os', limit=10)
        rosaProperties = getRosaProperties(rosaImages)

        self.assertIsNotNone(rosaProperties)
        self.assertEqual(len(rosaProperties), len(rosaImages))
        for rosa in rosaProperties:
            self.assertTrue(rosa["found"])
            self.assertIsNotNone(rosa["center"])
            for key, value in rosa["center"].items():
                self.assertTrue(value > 0)

    def testImportRetinaImages(self):
        retinaImages = self.db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                                , eye='os', limit=10)
        self.assertIsNotNone(retinaImages)
        self.assertTrue(isinstance(retinaImages, list))
        self.assertEqual(len(retinaImages), 10)
        for image in retinaImages:
            self.assertTrue(isinstance(image, np.ndarray))
            self.assertTrue(len(image.squeeze().shape) == 2)
            self.assertTrue((image.squeeze().shape[0]) > 100)
            self.assertTrue((image.squeeze().shape[1]) > 100)

    def testFindBlurryImages(self):
        retinaImages = self.db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                                , eye='os', limit=10)
        isBluryFlag =  findBlurryImages(retinaImages)
        self.assertIsNotNone(isBluryFlag)
        self.assertTrue(len(isBluryFlag) == len(retinaImages))

    def testCropImageMargins(self):
        retinaImages = self.db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                                , eye='os', limit=3)
        margin = 100
        for image in retinaImages:
            croppedImage = cropImageMargins(image, margin=margin)
            self.assertTrue(isinstance(croppedImage, np.ndarray))
            self.assertTrue(len(croppedImage.squeeze().shape) == 2)
            self.assertTrue(croppedImage.shape[0] == image.shape[0] - margin * 2)
            self.assertTrue(croppedImage.shape[1] == image.shape[1] - margin * 2)

    def testSpotDarkVessels(self):
        retinaImages = self.db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                                     , eye='os', limit=3)
        for image in retinaImages:
            vesselsImage = spotDarkVessels(image)
            self.assertTrue(isinstance(vesselsImage, np.ndarray))
            self.assertTrue(len(vesselsImage.squeeze().shape) == 2)
            self.assertTrue(vesselsImage.shape[0] == image.shape[0])
            self.assertTrue(vesselsImage.shape[1] == image.shape[1])

    


if __name__=="__main__":
    envtest.main()
