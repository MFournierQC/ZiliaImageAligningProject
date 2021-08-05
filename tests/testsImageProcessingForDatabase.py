import envtest
from processImagesFromDatabase import *
from zilia import *
db = ZiliaDB()

# skipPlots = True

class TestImageProcessingForDatabase(envtest.ZiliaTestCase):

    def testInit(self):
        self.assertTrue(True)

    def testImportRosaImages(self):
        rosaImages = db.getRGBImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                     ,content='rosa',eye='os', limit=10)
        self.assertIsNotNone(rosaImages)
        
    def testGetRosaProperties(self):
        rosaImages = db.getRGBImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                     , content='rosa', eye='os', limit=10)
        rosaProperties = getRosaProperties(rosaImages)
        self.assertIsNotNone(len(rosaProperties))
        self.assertTrue(len(rosaProperties) == len(rosaImages))

    def testImportRetinaImages(self):
        retinaImages = db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                                , eye='os', limit=10)
        self.assertIsNotNone(retinaImages)

    def testFindBlurryImages(self):
        retinaImages = db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                                , eye='os', limit=10)
        isBluryFlag =  findBlurryImages(retinaImages)
        self.assertIsNotNone(isBluryFlag)
        self.assertTrue(len(isBluryFlag) == len(retinaImages))

    def testCropImageMargins(self):
        retinaImages = db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                                , eye='os', limit=3)
        margin = 100
        croppedImage = cropImageMargins(retinaImages[0], margin=margin)
        self.assertTrue(croppedImage.shape[0] == retinaImages[0].shape[0] - margin * 2)
        self.assertTrue(croppedImage.shape[1] == retinaImages[0].shape[1] - margin * 2)



if __name__=="__main__":
    envtest.main()
