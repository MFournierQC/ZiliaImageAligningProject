import env
from dcclab.database import *
from datetime import date
from zilia import *
import unittest
import os
import numpy as np
from skimage.io import imread


dbPath = 'test.db'
ziliaDb = '/Volumes/Goliath/labdata/dcclab/zilia/zilia.db'
dbRoot = '/Volumes/Goliath/labdata/dcclab/zilia'

class TestZilia(env.DCCLabTestCase):
    def setUp(self):
        self.db = ZiliaDB(ziliaDb, dbRoot)
        self.assertIsNotNone(self.db)

    def testZiliaDBCreation(self):
        self.assertIsNotNone(self.db)

    def testZiliaGetMonkeyNames(self):
        self.db.execute("select name from monkeys order by name")
        rows = self.db.fetchAll()
        self.assertTrue(len(rows) == 4)
        self.assertEqual([ r['name'] for r in rows], ['Bresil', 'Kenya', 'Rwanda', 'Somalie'])

    def testGetMonkeyNames(self):
        names = self.db.getMonkeyNames()
        self.assertEqual(names, ['Bresil', 'Kenya', 'Rwanda', 'Somalie'])

    def testGetWavelengths(self):
        wavelengths = self.db.getWavelengths()
        self.assertTrue(wavelengths.shape == (512,))

    def testGetTimelines(self):
        types = self.db.getTimelines()
        self.assertEqual(types, ['background','baseline'])

    def testGetColumns(self):
        cols = self.db.getColumns()
        # self.assertEqual(cols, ['bg','raw','ref'])
        self.assertEqual(cols, ['raw'])

    def testGetRegions(self):
        regions = self.db.getRegions()
        self.assertEqual(regions, ['mac','onh'])

    def testGetSpectra(self):
        spectra = self.db.getRawIntensities(monkey='Rwanda', region='onh', timeline='baseline', column='raw')
        self.assertIsNotNone(spectra)
        print(spectra.shape)

    def testGetEyeImages(self):
        self.db.execute("select path from imagefiles where content='eye' and rlp = 34 and timeline='baseline 3' limit 10 ")
        rows = self.db.fetchAll()

        for row in rows:
            relativePath = row['path']
            absolutePath = "{0}/{1}".format(dbRoot, relativePath)
            image = imread(absolutePath)
            self.assertIsNotNone(image)
            self.assertEqual(image.shape, (1024, 1216, 3))

    def testGetEyeImagesFromDatabase(self):
        images = self.db.getRGBImages(rlp=34, timeline='baseline 3', region='onh', content='eye')
        self.assertTrue(len(images) > 0)

    def testGetGrayscaleEyeImagesFromDatabase(self):
        images = self.db.getGrayscaleEyeImages(monkey='Bresil' , rlp=6, timeline='baseline 3', region='onh')
        self.assertTrue(len(images) > 0)
        for image in images:
            self.assertEqual(image.shape, (1024, 1216))

    def testGetImagePaths(self):
        paths = self.db.getImagePaths()
        self.assertTrue(len(paths) > 1000)


    def testGetSpectraPaths(self):
        paths = self.db.getSpectraPaths()
        self.assertTrue(len(paths) > 1000)

if __name__ == '__main__':
    unittest.main()
