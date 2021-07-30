import env
from dcclab.database import *
from datetime import date
from zilia import *
import unittest
import os
import numpy as np
from skimage.io import imread
import subprocess
import re
from analyzeEyeImages import *


def computeONHParams(grayImage):
    detector = ZiliaONHDetector(grayImage)
    detector.getParamsCorrections()
    detector.preProcessImage()
    bestEllipse = detector.findOpticNerveHead()
    (xCenter, yCenter), minorAxis, majorAxis, orientation = bestEllipse
    ellipseDict = { "onhCenterX": xCenter,
                    "onhCenterY": yCenter,
                    "onhHeight": majorAxis,
                    "onhWidth": minorAxis}
    return ellipseDict


class TestZilia(env.DCCLabTestCase):

    def setUp(self):
        self.db = ZiliaDB()
        self.assertIsNotNone(self.db)

    def testGetGrayscaleEyeImagesFromDatabase(self):
        images = self.db.getGrayscaleEyeImages(monkey='Bresil' , rlp=6, timeline='baseline 3', region='onh', limit=10)
        self.assertTrue(len(images) == 10)
        for image in images:
            self.assertEqual(image.shape, (1024, 1216))


    def testGetGrayscaleEyeImagesWithPaths(self):
        images = self.db.getGrayscaleEyeImagesWithPaths(region='onh')
        self.assertTrue(len(images.keys()) == 10)
        for path, imageData in images.items():
            # self.assertEqual(imageData.shape, (1024, 1216))
            try:
                results = computeONHParams(imageData)
                results["path"] = path
                print(results)
            except:
                pass

if __name__ == '__main__':
    unittest.main()
