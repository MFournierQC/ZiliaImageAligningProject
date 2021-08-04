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
        
    def test01RosaProperties(self):
        rosaImages = db.getRGBImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                     , content='rosa', eye='os', limit=10)
        rosaProperties = getRosaProperties(rosaImages)
        self.assertIsNotNone(len(rosaProperties))
        self.assertTrue(len(rosaProperties) == len(rosaImages))

 
if __name__=="__main__":
    envtest.main()
