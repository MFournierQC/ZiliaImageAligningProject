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


class CalcEngine:
    def __init__(self, database, maxTaskCount=None):
        self.db = database
        self.recordsQueue = Queue()
        self.resultsQueue = Queue()
        self.runningTasks = []

        if maxTaskCount is None:
            self.maxTaskCount = multiprocessing.cpu_count()
        else:
            self.maxTaskCount = maxTaskCount

    def __del__(self):
        self.terminateTimedOutTasks(timeoutInSeconds=0)
        self.recordsQueue.close()
        self.resultsQueue.close()

    def compute(self, target, processTaskResults=None, timeoutInSeconds=3*60, taskCount=None):
        if taskCount is None:
            taskCount = self.maxTaskCount

        while self.hasTasksStillRunning() or self.hasTasksLeftToLaunch():
            while len(self.runningTasks) < taskCount and self.hasTasksLeftToLaunch():
                self.launchTask(target=target)

            if processTaskResults is None:
                self.processTaskResults(self.resultsQueue)
            else:
                processTaskResults(self.resultsQueue)

            self.terminateTimedOutTasks(timeoutInSeconds=timeoutInSeconds)
            self.pruneTerminatedTasks()
            time.sleep(0.1)

    def hasTasksLeftToLaunch(self):
        return not self.recordsQueue.empty()

    def hasTasksStillRunning(self):
        return len(self.runningTasks) > 0

    def enqueueRecords(self, monkey=None, timeline=None, rlp=None, region=None, content=None, eye=None, limit=None):
        selectStatement = self.db.buildImageSelectStatement(monkey=monkey, timeline=timeline, rlp=rlp, region=region, content=content, eye=eye, limit=limit)
        self.enqueueRecordsWithStatement(selectStatement)

    def enqueueRecordsWithStatement(self, selectStatement):
        self.db.execute(selectStatement)
        rows = self.db.fetchAll()
        if len(rows) >= 32767:
            print("Warning: queue may be limited to 32768 elements")
        elif len(rows) == 0:
            raise ValueError("Warning: no records returned from {0}".format(selectStatement))

        for row in rows:
            record = {}
            for key in row.keys():
                record[key] = row[key]
            self.recordsQueue.put(record)

        # it takes a fraction of a second for the queue to appear non-empty.  We make sure it is ok before returning
        while self.recordsQueue.empty():
            pass

    def launchTask(self, target):
        p=Process(target=target, args=(self.recordsQueue, self.resultsQueue))
        startTime = time.time()
        self.runningTasks.append((p, startTime))
        p.start()
        return p, startTime

    def processTaskResults(self, queue):
        while not queue.empty():
            results = queue.get()
            print(results)

    def terminateTimedOutTasks(self, timeoutInSeconds):
        for (p, startTime) in self.runningTasks:
            if time.time() > startTime+timeoutInSeconds:
                p.terminate()
                p.join()

    def pruneTerminatedTasks(self):
        self.runningTasks = [ (p,startTime) for p,startTime in self.runningTasks if p.is_alive()]



class TestZiliaCalculation(env.DCCLabTestCase):

    def setUp(self):
        self.db = ZiliaDB()
        self.assertIsNotNone(self.db)

    def tearDown(self):
        del self.db
        self.db = None

    def test101EngineInit(self):
        engine = CalcEngine(self.db)
        self.assertIsNotNone(engine)
        self.assertTrue(engine.recordsQueue.empty())
        self.assertTrue(engine.resultsQueue.empty())
        self.assertTrue(len(engine.runningTasks) == 0)
    
    def test102LaunchTask(self):
        engine = CalcEngine(self.db)
        p,startTime = engine.launchTask(target=getLen)
        self.assertIsNotNone(p)
        p.join()
        self.assertFalse(p.is_alive())
        
    def test103EnqueueRecords(self):
        engine = CalcEngine(self.db)
        self.assertIsNotNone(engine)
        engine.enqueueRecordsWithStatement(selectStatement="select path from imagefiles limit 10")
        self.assertTrue(engine.hasTasksLeftToLaunch())
        for i in range(10):
            engine.recordsQueue.get()
        self.assertFalse(engine.hasTasksLeftToLaunch())

    def test105ComputeAll(self):
        engine = CalcEngine(self.db)
        engine.enqueueRecordsWithStatement(selectStatement="select path from imagefiles limit 10")
        engine.compute(target=getLen)
        self.assertFalse(engine.hasTasksStillRunning())

    def test106ComputeAllWithCustomProcess(self):
        engine = CalcEngine(self.db)
        engine.enqueueRecordsWithStatement(selectStatement="select path from imagefiles limit 10")
        engine.compute(target=getLen, processTaskResults=printRecord)
        self.assertFalse(engine.hasTasksStillRunning())

    def test107Compute10WithCustomProcess(self):
        engine = CalcEngine(self.db)
        statement = engine.db.buildImageSelectStatement(region='onh', limit=10)
        engine.enqueueRecordsWithStatement(selectStatement=statement)
        engine.compute(target=computeMeanForPathWithQueues, processTaskResults=printRecord)
        self.assertFalse(engine.hasTasksStillRunning())

    def test107ComputeONHFor10(self):
        engine = CalcEngine(self.db)
        engine.enqueueRecords(region='onh', limit=32000)
        engine.compute(target=computeForPathWithQueues,timeoutInSeconds=120)
        self.assertFalse(engine.hasTasksStillRunning())

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

    # def test07GetGrayscaleEyeImagesWithPathsFullONCalculations(self):
    #     print("Getting paths")
    #     paths = self.db.getImagePaths(region='onh', limit=32000)
    #     print("Obtained {0} paths".format(len(paths)))
    #     pathQueue = Queue()
    #     resultsQueue = Queue()

    #     print("Getting paths into queue")
    #     for path in paths:
    #         # print("Inserting {0}".format(path))
    #         pathQueue.put(path)

    #     runningProcesses = []
    #     duration = {}
    #     print("Starting computations")
    #     while not pathQueue.empty():
    #         while len(runningProcesses) < multiprocessing.cpu_count():
    #             print("Starting new processes")
    #             p=Process(target=computeForPathWithQueues, args=(pathQueue, resultsQueue))
    #             runningProcesses.append((p, time.time()))
    #             p.start()

    #         while not resultsQueue.empty():
    #             print("Printing results")
    #             results = resultsQueue.get()
    #             print(results)

    #         # Kill very long processes (10 minutes)
    #         for (p, startTime) in runningProcesses:
    #             if time.time() > startTime+3*60:
    #                 print("Killing {0}".format(p))
    #                 p.terminate()

    #         runningProcesses = [ (p,startTime) for p,startTime in runningProcesses if p.is_alive()]
    #         time.sleep(1)
    #         print("Looping {0} processes running.".format(len(runningProcesses)))

    #     print("out waiting")
    #     while len(runningProcesses) >0:
    #         while not resultsQueue.empty():
    #             print("Printing results")
    #             results = resultsQueue.get()
    #             print(results)
    #         runningProcesses = [ process for process in runningProcesses if process.is_alive()]
    #         time.sleep(1)
    #         print("Waiting and looping {0} processes running.".format(len(runningProcesses)))




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
        return 0.0
        
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
        return 0.0

if __name__ == '__main__':
    unittest.main()
