from multiprocessing import Pool, Queue, Process, SimpleQueue
import multiprocessing
from analyzeEyeImages import *
from skimage.io import imread
import time
import json

class ComputeEngine:
    def __init__(self, maxTaskCount=None):
        self.inputQueue = Queue()
        self.outputQueue = Queue()
        self.runningTasks = []

        if maxTaskCount is None:
            self.maxTaskCount = multiprocessing.cpu_count()
        else:
            self.maxTaskCount = maxTaskCount

    def __del__(self):
        self.terminateTimedOutTasks(timeoutInSeconds=0)
        self.inputQueue.close()
        self.outputQueue.close()

    def compute(self, target, processTaskResults=None, timeoutInSeconds=3*60, taskCount=None):
        if taskCount is None:
            taskCount = self.maxTaskCount
        if processTaskResults is None:
            processTaskResults = self.processTaskResults

        while self.hasTasksStillRunning() or self.hasTasksLeftToLaunch():
            while len(self.runningTasks) < taskCount and self.hasTasksLeftToLaunch():
                self.launchTask(target=target)

            processTaskResults(self.outputQueue)

            self.terminateTimedOutTasks(timeoutInSeconds=timeoutInSeconds)
            self.pruneTerminatedTasks()
            time.sleep(0.1)

        processTaskResults(self.outputQueue)


    def hasTasksLeftToLaunch(self):
        return not self.inputQueue.empty()

    def hasTasksStillRunning(self):
        return len(self.runningTasks) > 0

    def launchTask(self, target):
        p=Process(target=target, args=(self.inputQueue, self.outputQueue))
        startTime = time.time()
        self.runningTasks.append((p, startTime))
        p.start()
        return p, startTime

    def processTaskResults(self, queue):
        while not queue.empty():
            results = queue.get()
            try:
                print(json.dumps(results))
            except:
                print(results)

    def terminateTimedOutTasks(self, timeoutInSeconds):
        for (p, startTime) in self.runningTasks:
            if time.time() > startTime+timeoutInSeconds:
                p.terminate()
                p.join()

    def pruneTerminatedTasks(self):
        self.runningTasks = [ (p,startTime) for p,startTime in self.runningTasks if p.is_alive()]

class DBComputeEngine(ComputeEngine):
    def __init__(self, database, maxTaskCount=None):
        super().__init__(maxTaskCount=maxTaskCount)
        self.db = database

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
            self.inputQueue.put(record)

        # it takes a fraction of a second for the queue to appear non-empty.  We make sure it is ok before returning
        while self.inputQueue.empty():
            pass

def calculateFactorial(inputQueue, outputQueue):
    if inputQueue.empty():
        return

    value = inputQueue.get()
    product = 1
    for i in range(value):
        product *= (i+1)

    outputQueue.put( (value,  product) )

if __name__ == "__main__":

    engine = ComputeEngine()

    for i in range(100):
        engine.inputQueue.put(i)

    engine.compute(target=calculateFactorial)


        
