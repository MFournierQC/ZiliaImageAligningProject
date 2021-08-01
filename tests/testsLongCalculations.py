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
from multiprocessing import Pool, Queue, Process, SimpleQueue
import multiprocessing
from analyzeEyeImages import *
from skimage.io import imread
import time


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

    # def test01GetGrayscaleEyeImagesFromDatabase(self):
    #     images = self.db.getGrayscaleEyeImages(monkey='Bresil' , rlp=6, timeline='baseline 3', region='onh', limit=10)
    #     self.assertTrue(len(images) == 10)
    #     for image in images:
    #         self.assertEqual(image.shape, (1024, 1216))

    # def test02GetImagePathsFiltered(self):
    #     images = self.db.getImagePaths(rlp=34, timeline='baseline 3', region='onh', content='eye', limit=10)
    #     self.assertTrue(len(images) == 10)

    # def test03GetGrayscaleEyeImagesWithPaths(self):
    #     images = self.db.getGrayscaleEyeImagesWithPaths(region='onh', limit=3)
    #     for path, imageData in images.items():
    #         try:
    #             results = computeONHParams(imageData)
    #         except:
    #             pass

    # def test04GetGrayscaleEyeImagesWithPathsMultiProcessing(self):
    #     paths = self.db.getImagePaths(region='onh', limit=3)
    #     #allResults = map(self.print, list(paths))
    #     with Pool(multiprocessing.cpu_count()) as p:
    #         allResults = p.map(computeMeanForPath, list(paths))
    #     print(allResults)

    # def test05GetGrayscaleEyeImagesWithPathsSimpleMapMultiProcessing(self):
    #     paths = self.db.getImagePaths(region='onh', limit=3)
    #     with Pool(multiprocessing.cpu_count()) as p:
    #         allResults = p.map(computeForPath, list(paths))
    #     print(allResults)

    # def test06GetGrayscaleEyeImagesWithPathsMultiProcessing(self):
    #     paths = self.db.getImagePaths(region='onh', limit=10)
    #     pathQueue = SimpleQueue()
    #     resultsQueue = SimpleQueue()

    #     for path in paths:
    #         pathQueue.put(path)

    #     runningProcesses = []
    #     while not pathQueue.empty():
    #         while len(runningProcesses) <= multiprocessing.cpu_count():
    #             p=Process(target=computeMeanForPathWithQueue, args=(pathQueue, resultsQueue))
    #             runningProcesses.append(p)
    #             p.start()

    #         while not resultsQueue.empty():
    #             results = resultsQueue.get()
    #             print(results)

    #         runningProcesses = [ process for process in runningProcesses if process.is_alive()]
    #         time.sleep(1)

    #     while len(runningProcesses) > 0:
    #         p = runningProcesses.pop(0)
    #         p.join()

    #     while not resultsQueue.empty():
    #         results = resultsQueue.get()
    #         print(results)

    def test07GetGrayscaleEyeImagesWithPathsFullONCalculations(self):
        print("Getting paths")
        paths = self.db.getImagePaths(region='onh', limit=32000)
        print("Obtained {0} paths".format(len(paths)))
        pathQueue = Queue()
        resultsQueue = Queue()

        print("Getting paths into queue")
        for path in paths:
            # print("Inserting {0}".format(path))
            pathQueue.put(path)

        runningProcesses = []
        duration = {}
        print("Starting computations")
        while not pathQueue.empty():
            while len(runningProcesses) < multiprocessing.cpu_count():
                print("Starting new processes")
                p=Process(target=computeForPathWithQueues, args=(pathQueue, resultsQueue))
                runningProcesses.append((p, time.time()))
                p.start()

            while not resultsQueue.empty():
                print("Printing results")
                results = resultsQueue.get()
                print(results)

            # Kill very long processes (10 minutes)
            for (p, startTime) in runningProcesses:
                if time.time() > startTime+3*60:
                    print("Killing {0}".format(p))
                    p.terminate()

            runningProcesses = [ (p,startTime) for p,startTime in runningProcesses if p.is_alive()]
            time.sleep(1)
            print("Looping {0} processes running.".format(len(runningProcesses)))

        print("out waiting")
        while len(runningProcesses) >0:
            while not resultsQueue.empty():
                print("Printing results")
                results = resultsQueue.get()
                print(results)
            runningProcesses = [ process for process in runningProcesses if process.is_alive()]
            time.sleep(1)
            print("Waiting and looping {0} processes running.".format(len(runningProcesses)))


def getLen(self, path):
    return len(path)

def computeForPath(path):
    try:
        results = {}
        imageData = imread(path)
        results = computeONHParams(imageData)
        results["path"] = path
        return results
    except Exception as err:
        return None

def computeForPathWithQueues(pathQueue, resultsQueue):
    try:
        if pathQueue.empty():
            return
        path = pathQueue.get()
        results = {}
        imageData = imread(path)
        results = computeONHParams(imageData)
        results["path"] = path
        resultsQueue.put(results)
    except Exception as err:
        print(err)
        return 0.0
        
def computeMeanForPathWithQueue(pathQueue, resultsQueue):
    try:
        if pathQueue.empty():
            return
        path = pathQueue.get()
        results = {}
        imageData = imread(path)
        results["mean"] = np.mean(imageData)
        results["path"] = path
        resultsQueue.put(results)
    except Exception as err:
        print(err)
        return 0.0

if __name__ == '__main__':
    unittest.main()
