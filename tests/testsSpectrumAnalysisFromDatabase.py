import envtest
from spectrumAnalysisFromDatabase import *
from zilia import *

class TestSpectrumAnalysisFromDatabase(envtest.ZiliaTestCase):

    def testImportDatabase(self):
        db = ZiliaDB()
        self.assertIsNotNone(db)

    def setUp(self):
        self.db = ZiliaDB()
        self.assertIsNotNone(self.db)

    def testGetWavelengths(self):
        pass

    def testGetSpectraFor10(self):
        pass

    def testGetSpectraPathsFor10(self):
        pass

    def testGetDarkRefFor10(self):
        pass


if __name__ == '__main__':
    envtest.main()
