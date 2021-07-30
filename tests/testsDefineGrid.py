import envtest
from processImages import defineGrid
from zilia import *
import numpy as np

class TestDefineGrid(envtest.ZiliaTestCase):

    def testImport(self):
        self.assertIsNotNone(defineGrid)

    def testImportDatabase(self):
        db = ZiliaDB()
        self.assertIsNotNone(db)

    def testImport10GrayRetinaImages(self):
        db = ZiliaDB()
        eyeImages = db.getGrayscaleEyeImages(limit=10)
        for image in eyeImages:
            self.assertIsInstance(image, np.ndarray)
            self.assertEqual(len(image.shape), 2)

    def testImport1RetinaImage(self):
        db = ZiliaDB()
        eyeImage = db.getGrayscaleEyeImages(limit=1)
        self.assertEqual(len(eyeImage), 1)
        print(eyeImage[0].shape)

    def testImport2RetinaImages(self):
        db = ZiliaDB()
        eyeImage = db.getGrayscaleEyeImages(limit=2)
        self.assertEqual(len(eyeImage), 2)
        print(eyeImage[0].shape)



if __name__=="__main__":
    envtest.main()
