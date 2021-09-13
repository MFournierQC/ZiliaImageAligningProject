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

    def setUp(self):
        self.db = ZiliaDB()
        self.assertIsNotNone(self.db)

    def testZiliaDBInit(self):
        self.assertIsNotNone(self.db)

    def testSpectralFiles(self):
        self.assertTrue(self.db.getCountSpectralFiles() == 1037)

    def assertEmptySelect(self, statement):
        self.db.execute(statement)
        rows = self.db.fetchAll()
        self.assertTrue(len(rows) == 0,msg="{0} returned something.".format(statement))

    def testSpectralFilesValidPaths(self):
        self.assertEmptySelect(r"select * from spectralfiles where path not like './%'")
        self.assertEmptySelect(r"select * from spectralfiles where path not like '%.csv' and path not like '%log' and path not like '%yaml'")
        self.assertEmptySelect(r"select * from spectralfiles where path not like '%March%'")

    def fixEmptyDates(self):
        dbWrite=ZiliaDB(writePermission=True)
        dbWrite.execute("update spectralfiles set date = '2021-02-23 12:25:40' where date is null")        
        dbWrite.commit()

    def testSpectralFilesValidDates(self):
        self.assertEmptySelect(r"select * from spectralfiles where date is null")        
        # self.fixEmptyDates()

        self.assertEmptySelect(r"select * from spectralfiles where strftime('%Y', date) != '2021'")
        self.assertEmptySelect(r"select * from spectralfiles where cast(strftime('%m', date) as integer) < 2 or cast(strftime('%m', date) as integer) > 4")
        self.assertEmptySelect(r"select * from spectralfiles where cast(strftime('%d', date) as integer) < 1 or cast(strftime('%d', date) as integer) > 31")

    def fixMonkeys(self):
        dbWrite=ZiliaDB(writePermission=True)
        dbWrite.execute("update spectralfiles set timeline='reference' where monkeyId is null and path like '%referen%'")        
        dbWrite.commit()

    def testSpectralFilesValidMonkeys(self):
        self.assertEmptySelect(r"select * from spectralfiles where monkeyId is null and timeline like 'baseline%'")
        # fixed with 
        self.assertEmptySelect(r"select * from spectralfiles where monkeyId is not null and timeline not like 'baseline%' and timeline not like 'background'")

    def testGetMonkeyNames(self):
        names = self.db.getMonkeyNames()
        self.assertEqual(names, ['Bresil', 'Kenya', 'Rwanda', 'Somalie'])

    def fixImageFilesAcquisition(self):
        dbWrite=ZiliaDB(writePermission=True)
        dbWrite.execute("select path from imagefiles")
        rows = dbWrite.fetchAll()
        for row in rows:
            path = row['path']
            match = re.search(r"(.+)/(\d+)-[eye|rosa].*jpg", path)
            if match is not None:
                acquisition = match.group(1)
                idx = int(match.group(2))
                statement = "update imagefiles set acquisition='{0}' where path='{1}'".format(acquisition, path)
                dbWrite.execute(statement)
                dbWrite.commit()      

        # update spectra set acquisition = (select acquisition from imagefiles where spectra.path = imagefiles.path );

    def fixSpectralFilesAcquisition(self):
        dbWrite=ZiliaDB(writePermission=True)
        dbWrite.execute("select path from spectralfiles")
        rows = dbWrite.fetchAll()
        for row in rows:
            path = row['path']
            match = re.search(r"(.+)/spectro_data.csv", path)
            if match is not None:
                acquisition = match.group(1)
                statement = "update spectralfiles set acquisition='{0}' where path='{1}'".format(acquisition, path)
                dbWrite.execute(statement)
                dbWrite.commit()      

    def fixImageIndexes(self):
        dbWrite=ZiliaDB(writePermission=True)
        dbWrite.execute("select path from imagefiles")
        rows = dbWrite.fetchAll()
        for row in rows:
            path = row['path']
            match = re.search(r"/(\d+)-[eye|rosa].*jpg", path)
            if match is not None:
                idx = int(match.group(1))
                statement = "update imagefiles set idx={0} where path='{1}'".format(idx, path)
                dbWrite.execute(statement)        

    def fixSpectraIndexes(self):
        dbWrite=ZiliaDB(writePermission=True)
        dbWrite.execute("update spectra set idx = cast(substr(column,5) as int)+1")


    # def testValidatePaths(self):
    #     imgPaths = self.db.getImagePaths(timeline="baseline")
    #     spectraPaths = self.db.getSpectraPaths(timeline="baseline")
    #     self.assertEqual(len(imgPaths), len(spectraPaths))


    # def testGetWavelengths(self):
    #     wavelengths = self.db.getWavelengths()
    #     self.assertTrue(wavelengths.shape == (512,))

    # def testGetBackgroundWavelengths(self):
    #     wavelengths = self.db.getBackgroundWavelengths()
    #     self.assertTrue(wavelengths.shape == (512,))

    # def testGetTimelines(self):
    #     types = self.db.getTimelines()
    #     self.assertEqual(types, ['background','baseline',"reference"])

    # def testGetColumns(self):
    #     cols = self.db.getColumns()
    #     self.assertEqual(cols, ['raw'])

    # def testGetRegions(self):
    #     regions = self.db.getRegions()
    #     self.assertEqual(regions, ['mac','onh'])

    # def testGetSpectra(self):
    #     spectra = self.db.getRawIntensities(limit=10)
    #     self.assertIsNotNone(spectra)
    #     self.assertTrue(len(spectra) > 0)
    #     wavelengths = self.db.getWavelengths() 
    #     nPoints = len(wavelengths)
    #     self.assertEqual(spectra.shape[0], nPoints)
    #     self.assertEqual(spectra.shape[1], 10)

    # def testGetSpectraFromRegion(self):
    #     spectra = self.db.getRawIntensities(limit=10, region='onh')
    #     self.assertIsNotNone(spectra)
    #     self.assertTrue(len(spectra) > 0)
    #     wavelengths = self.db.getWavelengths() 
    #     nPoints = len(wavelengths)
    #     self.assertEqual(spectra.shape[0], nPoints)
    #     self.assertEqual(spectra.shape[1], 10)

    # def testGetSpectraFromTimeline(self):
    #     spectra = self.db.getRawIntensities(limit=10, timeline='baseline')
    #     self.assertIsNotNone(spectra)
    #     self.assertTrue(len(spectra) > 0)
    #     wavelengths = self.db.getWavelengths() 
    #     nPoints = len(wavelengths)
    #     self.assertEqual(spectra.shape[0], nPoints)
    #     self.assertEqual(spectra.shape[1], 10)

    # def testGetSpectraFromEye(self):
    #     spectra = self.db.getRawIntensities(limit=10, eye='os')
    #     self.assertIsNotNone(spectra)
    #     self.assertTrue(len(spectra) > 0)
    #     wavelengths = self.db.getWavelengths() 
    #     nPoints = len(wavelengths)
    #     self.assertEqual(spectra.shape[0], nPoints)
    #     self.assertEqual(spectra.shape[1], 10)

    # def testGetSpectraFromMlonkey(self):
    #     spectra = self.db.getRawIntensities(monkey='Bresil')
    #     self.assertIsNotNone(spectra)

    # def testGetNoSpectraMustReturnNone(self):
    #     spectra = self.db.getRawIntensities(monkey='Daniel')
    #     self.assertIsNone(spectra)

    # def testGetNoSpectraMustReturnNoneIsSlow(self):
    #     startTime = time.time()
    #     spectra = self.db.getRawIntensities(monkey='Daniel')
    #     endTime = time.time()
    #     self.assertIsNone(spectra)
        
    #     if endTime-startTime < 5:
    #         print("Warning: Simple spectrum request was more than 5s. Consider copying database to local folder")

    # def testGetBackgroundSpectra(self):
    #     wavelengths, spectra = self.db.getBackgroundIntensities(rlp=4)
    #     self.assertIsNotNone(spectra)
    #     self.assertTrue(spectra.shape[0] > 2)
    #     self.assertIsNotNone(wavelengths)
    #     self.assertEqual(wavelengths.shape[0], spectra.shape[0])

    # @unittest.skip("Was used for initial development")
    # def testGetEyeImages(self):
    #     self.db.execute("select path from imagefiles where content='eye' and rlp = 34 and timeline='baseline 3' limit 10 ")
    #     rows = self.db.fetchAll()
    #     for row in rows:
    #         relativePath = row['path']
    #         absolutePath = "{0}/{1}".format(dbRoot, relativePath)
    #         image = imread(absolutePath)
    #         self.assertIsNotNone(image)
    #         self.assertEqual(image.shape, (1024, 1216, 3))

    # def testGetEyeImagesFromDatabase(self):
    #     images = self.db.getRGBImages(rlp=34, timeline='baseline 3', region='onh', content='eye', limit=10)
    #     self.assertTrue(len(images) == 10)


    # def testGetGrayscaleEyeImagesFromDatabase(self):
    #     images = self.db.getGrayscaleEyeImages(monkey='Bresil' , rlp=6, timeline='baseline 3', region='onh', limit=10)
    #     self.assertTrue(len(images) == 10)
    #     for image in images:
    #         self.assertEqual(image.shape, (1024, 1216))

    # def testGetGrayscaleEyeImagesFromDatabaseLarge(self):
    #     images = self.db.getRGBImages(timeline='baseline 3', limit=100)
    #     self.assertEqual(len(images), 100)
    #     for image in images:
    #         self.assertEqual(image.shape, (1024, 1216, 3))

    # def testGetImagePaths(self):
    #     paths = self.db.getImagePaths()
    #     self.assertTrue(len(paths) > 1000)

    # def testGetImagePathsFiltered(self):
    #     images = self.db.getImagePaths(rlp=34, timeline='baseline 3', region='onh', content='eye', limit=10)
    #     self.assertTrue(len(images) == 10)

    # def testGetSpectraPaths(self):
    #     paths = self.db.getSpectraPaths()
    #     self.assertTrue(len(paths) > 1000)

    # def testGetCalculatedProperties(self):
    #     records = self.db.getCalculatedImageProperties(rlp=34, timeline='baseline 3', region='onh', content='eye')
    #     self.assertTrue(len(records) > 0)
    #     for record in records:
    #         self.assertTrue('path' in record)    
    #         self.assertTrue('timeline' in record)    

    # def testGetAcquisitionIdList(self):
    #     acqIds = self.db.getAcquisitionIdList()
    #     self.assertTrue(len(acqIds) == 205)

    # def computeSomething(self, data):
    #     return {"mean":np.mean(data)}

    # def testComputeManyThings(self):
    #     a = [1,2,3]
    #     result = self.computeSomething(a)
    #     self.assertAlmostEqual(result["mean"], 2)

    # def testComputeThingsOnManyImageData(self):
    #     images = self.db.getGrayscaleEyeImagesWithPaths(limit=10)
    #     self.assertIsNotNone(images)

    #     for path, imageData in images.items():
    #         result = self.computeSomething(imageData)

if __name__ == '__main__':
    unittest.main()
