import envtest
from spectrumAnalysisFromDatabase import *

class TestSpectrumAnalysisFromDatabase(envtest.ZiliaTestCase):

    def testExecuteFile(self):
        self.assertTrue(True)



if __name__ == '__main__':
    envtest.main()