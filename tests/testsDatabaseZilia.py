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
        print(wavelengths.shape)
        self.assertTrue(wavelengths.shape == (512,))

    def testGetBackgroundWavelengths(self):
        wavelengths = self.db.getBackgroundWavelengths()
        self.assertTrue(wavelengths.shape == (512,))

    def testGetTimelines(self):
        types = self.db.getTimelines()
        self.assertEqual(types, ['background','baseline 1','baseline 2','baseline 3'])

    def testGetColumns(self):
        cols = self.db.getColumns()
        self.assertEqual(cols, ['raw'])

    def testGetRegions(self):
        regions = self.db.getRegions()
        self.assertEqual(regions, ['mac','onh'])

    def testGetSpectra(self):
        spectra = self.db.getRawIntensities(limit=10)
        self.assertIsNotNone(spectra)
        self.assertTrue(len(spectra) > 0)
        wavelengths = self.db.getWavelengths() 
        nPoints = len(wavelengths)
        self.assertEqual(spectra.shape[0], nPoints)
        self.assertEqual(spectra.shape[1], 10)

    def testGetSpectraFromRegion(self):
        spectra = self.db.getRawIntensities(limit=10, region='onh')
        self.assertIsNotNone(spectra)
        self.assertTrue(len(spectra) > 0)
        wavelengths = self.db.getWavelengths() 
        nPoints = len(wavelengths)
        self.assertEqual(spectra.shape[0], nPoints)
        self.assertEqual(spectra.shape[1], 10)

    def testGetSpectraFromTimeline(self):
        spectra = self.db.getRawIntensities(limit=10, timeline='baseline')
        self.assertIsNotNone(spectra)
        self.assertTrue(len(spectra) > 0)
        wavelengths = self.db.getWavelengths() 
        nPoints = len(wavelengths)
        self.assertEqual(spectra.shape[0], nPoints)
        self.assertEqual(spectra.shape[1], 10)

    def testGetSpectraFromEye(self):
        spectra = self.db.getRawIntensities(limit=10, eye='os')
        self.assertIsNotNone(spectra)
        self.assertTrue(len(spectra) > 0)
        wavelengths = self.db.getWavelengths() 
        nPoints = len(wavelengths)
        self.assertEqual(spectra.shape[0], nPoints)
        self.assertEqual(spectra.shape[1], 10)

    def testGetSpectraFromMlonkey(self):
        spectra = self.db.getRawIntensities(monkey='Bresil')
        self.assertIsNotNone(spectra)

    def testGetNoSpectraMustReturnNone(self):
        spectra = self.db.getRawIntensities(monkey='Daniel')
        self.assertIsNone(spectra)

    def testGetNoSpectraMustReturnNoneIsSlow(self):
        startTime = time.time()
        spectra = self.db.getRawIntensities(monkey='Daniel')
        endTime = time.time()
        self.assertIsNone(spectra)
        
        if endTime-startTime < 5:
            print("Warning: Simple spectrum request was more than 5s. Consider copying database to local folder")

    def testGetBackgroundSpectra(self):
        wavelengths, spectra = self.db.getBackgroundIntensities(rlp=4)
        self.assertIsNotNone(spectra)
        self.assertTrue(spectra.shape[0] > 2)
        self.assertIsNotNone(wavelengths)
        self.assertEqual(wavelengths.shape[0], spectra.shape[0])

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

    def testNumberOfRetinaImages(self):
        retinaImages = self.db.getGrayscaleEyeImages(monkey='Bresil', rlp=6, timeline='baseline 3', region='onh'
                                                     , eye='os', limit=10)
        self.assertEqual(len(retinaImages), 10)

if __name__ == '__main__':
    unittest.main()
