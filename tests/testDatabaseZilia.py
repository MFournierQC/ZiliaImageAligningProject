import env
from dcclab.database import *
from datetime import date
from zilia import *
import unittest
import os
import numpy as np

dbPath = 'test.db'
ziliaDb = '../zilia.db'

class TestZilia(env.DCCLabTestCase):
    def testZiliaDBCreation(self):
        self.assertIsNotNone(ZiliaDB(ziliaDb))

    def testZiliaGetMonkeyNames(self):
        db=ZiliaDB(ziliaDb)
        self.assertIsNotNone(db)
        db.execute("select name from monkeys order by name")
        rows = db.fetchAll()
        self.assertTrue(len(rows) == 4)
        self.assertEqual([ r['name'] for r in rows], ['Bresil', 'Kenya', 'Rwanda', 'Somalie'])

    def testGetMonkeyNames(self):
        db=ZiliaDB(ziliaDb)
        self.assertIsNotNone(db)
        names = db.getMonkeyNames()
        self.assertEqual(names, ['Bresil', 'Kenya', 'Rwanda', 'Somalie'])

    def testGetWavelengths(self):
        db=ZiliaDB(ziliaDb)
        self.assertIsNotNone(db)
        wavelengths = db.getWavelengths()
        self.assertTrue(wavelengths.shape == (512,))

    def testGetTimelines(self):
        db=ZiliaDB(ziliaDb)
        self.assertIsNotNone(db)
        types = db.getTimelines()
        self.assertEqual(types, ['background','baseline'])

    def testGetColumns(self):
        db=ZiliaDB(ziliaDb)
        self.assertIsNotNone(db)
        cols = db.getColumns()
        # self.assertEqual(cols, ['bg','raw','ref'])
        self.assertEqual(cols, ['raw'])

    def testGetRegions(self):
        db=ZiliaDB(ziliaDb)
        self.assertIsNotNone(db)
        regions = db.getRegions()
        self.assertEqual(regions, ['mac','onh'])

    def testGetSpectra(self):
        db=ZiliaDB(ziliaDb)
        self.assertIsNotNone(db)
        spectra = db.getRawIntensities(monkey='Rwanda', region='onh', timeline='baseline', column='raw')
        self.assertIsNotNone(spectra)
        print(spectra.shape)

    def testGetSaturatedSpectralRAnge(self):
        db=ZiliaDB(ziliaDb)
        self.assertIsNotNone(db)
        db.execute('select min(wavelength), max(wavelength), f.path from bloodspectra as s, bloodfiles as f where s.intensity == 65535 and s.wavelength > 530  and f.md5 = s.md5 group by s.md5;')
        rows = db.fetchAll()
        print(rows)

    def testGetBloodSpectra(self):
        db=ZiliaDB(ziliaDb)
        self.assertIsNotNone(db)
        wavelengths, spectra, saturation = db.getBloodIntensities()
        print(spectra, saturation)

if __name__ == '__main__':
    unittest.main()
