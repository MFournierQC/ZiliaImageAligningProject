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
        self.assertEqual(len(rosaProperties), 10)

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
            self.assertIsNotNone(vesselsImage)
            self.assertTrue(isinstance(vesselsImage, np.ndarray))
            self.assertTrue(len(vesselsImage.squeeze().shape) == 2)
            self.assertTrue(vesselsImage.shape[0] == image.shape[0])
            self.assertTrue(vesselsImage.shape[1] == image.shape[1])

    def testCalculateSkeletonImage(self):
        retinaImages = self.db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                                     , eye='os', limit=3)
        for image in retinaImages:
            skeletonImage = calculateSkeletonImage(image)
            self.assertIsNotNone(skeletonImage)
            self.assertTrue(isinstance(skeletonImage, np.ndarray))
            self.assertTrue(len(skeletonImage.squeeze().shape) == 2)
            self.assertTrue(skeletonImage.shape[0] == image.shape[0])
            self.assertTrue(skeletonImage.shape[1] == image.shape[1])

    def testFindGoodImagesIndex(self):
        retinaImages = self.db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                                     , eye='os', limit=10)
        isBluryFlag = findBlurryImages(retinaImages)
        goodImages=findGoodImagesIndex(isBluryFlag)
        self.assertIsNotNone(goodImages)
        self.assertTrue(len(goodImages) <= len(isBluryFlag))
        for imageNumber in goodImages:
            self.assertTrue(isBluryFlag[imageNumber] == 'False')

    def testCalculateValidShiftInOneAcquisition(self):
        retinaImages = self.db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                                     , eye='os', limit=10)
        shiftValueFromReferenceImage, imageIsValid = calculateValidShiftsInOneAcquisition (retinaImages)
        self.assertTrue(len(shiftValueFromReferenceImage) == 10)
        self.assertTrue(len(imageIsValid) == 10)
        for i in range(len(imageIsValid)):
            if imageIsValid[i] is not None:
                self.assertIsNotNone(shiftValueFromReferenceImage[i][0])
                self.assertIsNotNone(shiftValueFromReferenceImage[i][1])

    def testApplyShiftOnRosaCenter(self):
        retinaImages = self.db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                                     , eye='os', limit=10)
        shiftValueFromReferenceImage, imageIsValid = calculateValidShiftsInOneAcquisition(retinaImages)

        rosaImages = self.db.getRGBImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                          , content='rosa', eye='os', limit=10)
        rosaProperties = getRosaProperties(rosaImages)
        rosaOnRefImage = applyShiftOnRosaCenter(rosaProperties, shiftValueFromReferenceImage)
        self.assertTrue(len(rosaOnRefImage) == 10)
        for i in range(len(imageIsValid)):
            if imageIsValid[i] is not None and rosaProperties[i]['found'] is True:
                self.assertIsNotNone(rosaOnRefImage[i][0])
                self.assertIsNotNone(rosaOnRefImage[i][1])

    def test01CrossImage(self):
        firstImage = np.zeros([10,20])
        firstImage[5,10] = 1
        secondImage = firstImage
        crossCorrelationResult = crossImage(firstImage, secondImage)
        self.assertTrue(crossCorrelationResult.shape[0] == firstImage.shape[0])
        self.assertTrue(crossCorrelationResult.shape[1] == firstImage.shape[1])
        self.assertTrue(np.max(crossCorrelationResult) >= 0.99)

    def test02CrossImage(self):
        firstImage = np.zeros([10,20])
        firstImage[5,10] = 1
        secondImage = np.zeros([10,20])
        crossCorrelationResult = crossImage(firstImage, secondImage)
        self.assertTrue(np.sum(crossCorrelationResult) == 0)







if __name__=="__main__":
    envtest.main()
