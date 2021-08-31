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
import time
import json
import cv2
from analyzeRosaImages import analyzeRosa

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



class TestZiliaCalculationEngine(env.DCCLabTestCase):

    def setUp(self):
        self.db = ZiliaDB()
        self.assertIsNotNone(self.db)

    def tearDown(self):
        # del self.db
        self.db = None

    def test101EngineInit(self):
        engine = ZiliaComputeEngine(self.db)
        self.assertIsNotNone(engine)
        self.assertTrue(engine.recordsQueue.empty())
        self.assertTrue(engine.resultsQueue.empty())
        self.assertTrue(len(engine.runningTasks) == 0)
    
    def test102LaunchTask(self):
        engine = ZiliaComputeEngine(self.db)
        p,startTime = engine.launchTask(target=getLen)
        self.assertIsNotNone(p)
        p.join()
        self.assertFalse(p.is_alive())

    @unittest.skip("temporary skip")
    def test103EnqueueRecords(self):
        engine = ZiliaComputeEngine(self.db)
        self.assertIsNotNone(engine)
        engine.enqueueRecordsWithStatement(selectStatement="select path from imagefiles limit 10")
        self.assertTrue(engine.hasTasksLeftToLaunch())
        for i in range(10):
            engine.recordsQueue.get()
        self.assertFalse(engine.hasTasksLeftToLaunch())

    @unittest.skip("temporary skip")
    def test105ComputeAll(self):
        engine = ZiliaComputeEngine(self.db)
        engine.enqueueRecordsWithStatement(selectStatement="select path from imagefiles limit 10")
        engine.compute(target=getLen)
        self.assertFalse(engine.hasTasksStillRunning())

    @unittest.skip("temporary skip")
    def test106ComputeAllWithCustomProcess(self):
        engine = ZiliaComputeEngine(self.db)
        engine.enqueueRecordsWithStatement(selectStatement="select path from imagefiles limit 10")
        engine.compute(target=getLen, processTaskResults=printRecord)
        self.assertFalse(engine.hasTasksStillRunning())

    @unittest.skip("temporary skip")
    def test107Compute10WithCustomProcess(self):
        engine = ZiliaComputeEngine(self.db)
        statement = engine.db.buildImageSelectStatement(region='onh', limit=10)
        engine.enqueueRecordsWithStatement(selectStatement=statement)
        engine.compute(target=computeMeanForPathWithQueues, processTaskResults=printRecord)
        self.assertFalse(engine.hasTasksStillRunning())

    @unittest.skip("temporary skip")
    def test107ComputeONHFor10(self):
        engine = ZiliaComputeEngine(self.db)
        engine.enqueueRecords(region='onh', limit=10)
        engine.compute(target=computeForPathWithQueues,timeoutInSeconds=120)
        self.assertFalse(engine.hasTasksStillRunning())

    @unittest.skip("temporary skip")
    def test108ComputeMaxIntensityFor10(self):
        engine = ZiliaComputeEngine(self.db)
        engine.enqueueRecords(region='onh', content='eye', limit=10)
        engine.compute(target=computeMaxValForPathWithQueues,timeoutInSeconds=120)
        self.assertFalse(engine.hasTasksStillRunning())

    def test109ComputeRosaPositionFor10(self):
        engine = ZiliaComputeEngine(self.db)
        engine.enqueueRecords(region='onh', content='eye', limit=10)
        engine.compute(target=computeRosaParamsForPathWithQueues,timeoutInSeconds=120)
        self.assertFalse(engine.hasTasksStillRunning())

    def test200OutputResultDicts(self):
        data = {"onhCenterX":1, "onhCenterY":2}
        for key, value in data.items():
            print("insert into calculations (property, value, date, algorithm) values('{0}', {1}, '{2}', 'hough');".format(key, value, '2021-08-01'))

    def test201ReadDictsFromString(self):
        text = '{"onhCenterX":1, "onhCenterY":2}'
        aDictionary = json.loads(text)
        self.assertEqual(aDictionary["onhCenterX"], 1)
        self.assertEqual(aDictionary["onhCenterY"], 2)

    def test202ReadDictsFromFileAndOutputCSVForCalculations(self):
        with open('calc-durations.txt') as f:
            lines = f.readlines()

        for line in lines:
            line = line.replace("'", '"')
            data = json.loads(line)
            self.assertIsNotNone(data["onhCenterX"])
            self.assertIsNotNone(data["onhCenterY"])
            for key, value in data.items():
                if key != 'path' and key != 'duration':
                    print("{3}|{0}|{1}||||hough|{2}".format(key, value, '2021-08-01', data['path']))
                    #print("insert into calculations (path, property, value, date, algorithm) values('{3}', '{0}', {1}, '{2}', 'hough');".format(key, value, '2021-08-01', data['path']))

    def test01GetGrayscaleEyeImagesFromDatabase(self):
        images = self.db.getGrayscaleEyeImages(monkey='Bresil' , rlp=6, timeline='baseline 3', region='onh', limit=10)
        self.assertTrue(len(images) == 10)
        for image in images:
            self.assertEqual(image.shape, (1024, 1216))

    def test02GetImagePathsFiltered(self):
        images = self.db.getImagePaths(rlp=34, timeline='baseline 3', region='onh', content='eye', limit=10)
        self.assertTrue(len(images) == 10)

    @unittest.skip("long")
    def test03GetGrayscaleEyeImagesWithPaths(self):
        images = self.db.getGrayscaleEyeImagesWithPaths(region='onh', limit=3)
        for path, imageData in images.items():
            try:
                results = computeONHParams(imageData)
            except:
                pass

    @unittest.skip("long")
    def test04GetGrayscaleEyeImagesWithPathsMultiProcessing(self):
        paths = self.db.getImagePaths(region='onh', limit=3)
        #allResults = map(self.print, list(paths))
        with Pool(multiprocessing.cpu_count()) as p:
            allResults = p.map(computeMeanForPath, list(paths))
        print(allResults)

    @unittest.skip("long")
    def test05GetGrayscaleEyeImagesWithPathsSimpleMapMultiProcessing(self):
        paths = self.db.getImagePaths(region='onh', limit=3)
        with Pool(multiprocessing.cpu_count()) as p:
            allResults = p.map(computeForPath, list(paths))
        print(allResults)

    @unittest.skip("long")
    def test06GetGrayscaleEyeImagesWithPathsMultiProcessing(self):
        paths = self.db.getImagePaths(region='onh', limit=10)
        pathQueue = SimpleQueue()
        resultsQueue = SimpleQueue()

        for path in paths:
            pathQueue.put(path)

        runningProcesses = []
        while not pathQueue.empty():
            while len(runningProcesses) <= multiprocessing.cpu_count():
                p=Process(target=computeMeanForPathWithQueue, args=(pathQueue, resultsQueue))
                runningProcesses.append(p)
                p.start()

            while not resultsQueue.empty():
                results = resultsQueue.get()
                print(results)

            runningProcesses = [ process for process in runningProcesses if process.is_alive()]
            time.sleep(1)

        while len(runningProcesses) > 0:
            p = runningProcesses.pop(0)
            p.join()

        while not resultsQueue.empty():
            results = resultsQueue.get()
            print(results)

    @unittest.skip("long and nasty")
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


def computeRosaParamsForPathWithQueues(recordsQueue, resultsQueue):
    try:
        if recordsQueue.empty():
            return
        record = recordsQueue.get()
        path = record["abspath"]
        result = {}
        result['path'] = record['path']
        startTime = time.time()
        blob = analyzeRosa(path)
        result['duration'] = time.time() - startTime
        result['rosaAbsX'] = blob["center"]['rx']
        result['rosaAbsY'] = blob["center"]['ry']
    except Exception as err:
        print(f"An error has occured: {err}.")

def computeMaxValForPathWithQueues(recordsQueue, resultsQueue):
    try:
        if recordsQueue.empty():
            return
        record = recordsQueue.get()
        path = record["abspath"]
        result = {}
        result['path'] = record['path']
        startTime = time.time()
        image = imread(path, as_gray=True)
        result["maxValue"] = np.amax(image)
        result['duration'] = time.time() - startTime
        resultsQueue.put(result)
    except Exception as err:
        print(f"An error has occured: {err}.")

def getLen(recordsQueue, resultsQueue):
    if recordsQueue.empty():
        return
    record = recordsQueue.get()
    length = len(record["path"])
    time.sleep(0.2)
    resultsQueue.put(length)

def printRecord(queue):
    while not queue.empty():
        results = queue.get()
        print(results)

def computeForPath(path):
    try:
        results = {}
        imageData = imread(path)
        results = computeONHParams(imageData)
        return results
    except Exception as err:
        return None

def computeForPathWithQueues(recordsQueue, resultsQueue):
    try:
        if recordsQueue.empty():
            return
        record = recordsQueue.get()
        path = record["abspath"]
        results = {}
        startTime = time.time()
        imageData = imread(path)
        results = computeONHParams(imageData)
        results["path"] = record["path"]
        results["duration"] = time.time()-startTime
        resultsQueue.put(results)
    except Exception as err:
        print(err)

def computeMeanForPathWithQueues(recordsQueue, resultsQueue):
    try:
        if recordsQueue.empty():
            return
        record = recordsQueue.get()
        path = record["abspath"]
        results = {}
        startTime = time.time()
        imageData = imread(path)
        results["mean"] = np.mean(imageData)
        # results["abspath"] = record["abspath"]
        results["path"] = record["path"]
        results["duration"] = time.time()-startTime
        resultsQueue.put(results)
    except Exception as err:
        print(err)

if __name__ == '__main__':
    unittest.main()
