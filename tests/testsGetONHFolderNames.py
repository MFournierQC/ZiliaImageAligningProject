import pandas as pd
import numpy as np
import csv
import unittest
import os
import sys

# Run tests in order they are written
unittest.TestLoader.sortTestMethodsUsing = None

skipAll = True
# skipAll = False

class TestGetONHFolderNames(unittest.TestCase):

    @unittest.skipIf(skipAll, "skip all file creations")
    def testTakePathsFromCsvAndSaveThemInNewCSV(self):
        filename = "manualEllipses.csv"

        df = pd.read_csv(filename, sep=",")
        paths = df["Path"].to_list()
        cleanpaths = []
        for path in paths:
            cleanpaths.append(path[:-12])

        with open("onhpaths.csv", "w", newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["path"])
            for path in cleanpaths:
                writer.writerow([path])

        print(cleanpaths)

    @unittest.skipIf(skipAll, "skip all file creations")
    def testImportThePathsCsvAndThrowThemInAList(self):
        df = pd.read_csv("onhpaths.csv")
        # print(df.head())
        paths = df["path"].to_list()
        print(paths)

    def testIfPathExists(self):
        dataPath = "Z:/labdata/dcclab/zilia"
        sys.path.insert(0, dataPath)
        exists = os.path.exists(dataPath)
        self.assertTrue(exists)

    @unittest.skipIf(skipAll, "skip all file creations")
    def testIfRelativePathFromCsvFileIsAccessible(self):
        dataPath = "Z:/labdata/dcclab/zilia"
        sys.path.insert(0, dataPath)

        df = pd.read_csv("onhpaths.csv")
        paths = df["path"].to_list()
        folderPath = paths[0]
        exists = os.path.exists(dataPath+folderPath[1:])
        self.assertTrue(exists)

if __name__ == '__main__':
    unittest.main()
