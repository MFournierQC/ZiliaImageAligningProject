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
from multiprocessing import Pool

class TestZilia(env.DCCLabTestCase):

    def test01FindDatabase(self):
        path = ZiliaDB.findDatabasePath()
        self.assertIsNotNone(path)
        self.assertTrue(os.path.isabs(path))
        print("Using database at: {0}".format(path))

    def test02FindDataFilesRoot(self):
        path = ZiliaDB.findDataFilesRoot()
        self.assertIsNotNone(path)
        self.assertTrue(os.path.isabs(path))
        print("Using files from: {0}".format(path))

    def testSubprocess(self):
        try:
            result = subprocess.run(['duck', '-h'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                match = re.match(r'Third.+in\s+(.+duck).Profiles', line)
                if match is not None:
                    shortPath = match.group(1)
                    duckDir = os.path.expanduser(shortPath)
                    ziliaPath = ("{0}/Volumes/Zilia".format(duckDir))
                    self.assertTrue(os.path.exists( ziliaPath ) )
        except:
            print("No cyberduck command-line tool. Not an error.")

    def testCyberduckMounts(self):
        before = len(ZiliaDB.rootCandidates)
        if ZiliaDB.addCyberduckPathsIfPresent():
            self.assertTrue(before < len(ZiliaDB.rootCandidates))
        else:
            print("Cyberduck not present.")

    def setUp(self):
        self.db = ZiliaDB()
        self.assertIsNotNone(self.db)

    def testZiliaDBInit(self):
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
        spectra = self.db.getRawIntensities(monkey='Rwanda', region='onh', timeline='baseline')
        self.assertIsNotNone(spectra)

    def testGetBackgroundSpectra(self):
        spectra = self.db.getBackgroundIntensities(rlp=4)
        self.assertIsNotNone(spectra)
        print(spectra)
        # select s.path, s.wavelength, s.intensity, s.md5, s.column from spectra as s inner join spectralfiles as f on f.md5 = f.md5  where f.timeline like '%background%' and f.rlp = 4 order by s.wavelength
        self.assertTrue(len(spectra) > 4)


    @unittest.skip("Was used for initial development")
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
        images = self.db.getRGBImages(rlp=34, timeline='baseline 3', region='onh', content='eye', limit=10)
        self.assertTrue(len(images) == 10)


    def testGetGrayscaleEyeImagesFromDatabase(self):
        images = self.db.getGrayscaleEyeImages(monkey='Bresil' , rlp=6, timeline='baseline 3', region='onh', limit=10)
        self.assertTrue(len(images) == 10)
        for image in images:
            self.assertEqual(image.shape, (1024, 1216))

    def testGetGrayscaleEyeImagesFromDatabaseLarge(self):
        images = self.db.getRGBImages(timeline='baseline 3', limit=100)
        self.assertEqual(len(images), 100)
        for image in images:
            self.assertEqual(image.shape, (1024, 1216, 3))

    def testGetImagePaths(self):
        paths = self.db.getImagePaths()
        self.assertTrue(len(paths) > 1000)

    def testGetImagePathsFiltered(self):
        images = self.db.getImagePaths(rlp=34, timeline='baseline 3', region='onh', content='eye', limit=10)
        self.assertTrue(len(images) == 10)

    def testGetSpectraPaths(self):
        paths = self.db.getSpectraPaths()
        self.assertTrue(len(paths) > 1000)

    def testGetCalculatedProperties(self):
        records = self.db.getCalculatedImageProperties(rlp=34, timeline='baseline 3', region='onh', content='eye')
        self.assertTrue(len(records) > 0)
        for record in records:
            self.assertTrue('path' in record)    
            self.assertTrue('timeline' in record)    

    def testGetAcquisitionIdList(self):
        acqIds = self.db.getAcquisitionIdList()
        self.assertTrue(len(acqIds) == 205)

    def computeSomething(self, data):
        return {"mean":np.mean(data)}

    def testComputeManyThings(self):
        a = [1,2,3]
        result = self.computeSomething(a)
        self.assertAlmostEqual(result["mean"], 2)

    def testComputeThingsOnManyImageData(self):
        images = self.db.getGrayscaleEyeImagesWithPaths(limit=10)
        self.assertIsNotNone(images)

        for path, imageData in images.items():
            result = self.computeSomething(imageData)

if __name__ == '__main__':
    unittest.main()
