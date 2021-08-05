from multiprocessing import Pool, Queue, Process, SimpleQueue, cpu_count
from queue import Empty
from threading import Thread
from analyzeEyeImages import *
from skimage.io import imread
import time
import json
import signal

"""
A class to run many tasks in parallel when they are mostly independent.  This engine is perfectly
appropriate for long, repetitive calculations (for example: computing f(x) on a large
dataset).

They will make use of all processors and cores and will use either threads or child processes.
You decide which one you use when you create the ComputeEngine:

engine = ComputeEngine(maxTaskCount=None, useThreads=True):

Differences between threads and processes:

* Threads start quickly (ms) and share the memory with the calling thread.  Processes require
  a copy of all the memory used, and will therefore take some time to actually start (~1s)
  Typically, threads will be used when you perform many small calculations.  If a calculation
  is really long, then a process can be more appropriate as 1) it does not suffer much 
  from the startup time and 2) any misbehaving code cannot crash your main code.
* If you use Processes, it is possible to set a timeout and terminate the task when it is taking
  too long. You can return an exit code and check it. It is not possible to terminate a thread.
* A badly behaving Thread can corrupt and crash your program (by modifying memory that it 
  should not for instance).  A Process cannot crash the calling program because it is running
  in a separate space.

To use this engine:

1. create an engine = ComputeEngine()
2. put the input data onto the "input queue" with engine.inputQueue.put(someData)
3. write a function someFunction(inputQueue, outputQueue) that takes two arguments: 
   inputQueue and outputQueue
4. that function will take its input data with inputQueue.get() and store the result
   on outputQueue.put(result)
5. you can put whatever you want on queues (numbers, dictionaries, tuples, other objects, etc...)
6. call engine.compute(), which will start many tasks (either processes or threads)
7. As the calculation progresses, the compute() function will call processTaskResult() with
   your function or the default function (which prints the results to the screen).
8. If using processes, it is possible to terminate a long running task with a timeout
9. You can change the processTaskResults() function to your own function (to save to disk for instance)

"""

class ComputeEngine:
    def __init__(self, maxTaskCount=None, useThreads=True):
        self.inputQueue = Queue()
        self.outputQueue = Queue()
        self.runningTasks = []
        self.useThreads = useThreads

        if maxTaskCount is None:
            self.maxTaskCount = cpu_count()
        else:
            self.maxTaskCount = maxTaskCount
        self.signalNames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items())) if v.startswith('SIG') and not v.startswith('SIG_'))

    def __del__(self):
        self.terminateTimedOutTasks(timeoutInSeconds=0)
        self.inputQueue.close()
        self.outputQueue.close()

    def compute(self, target, 
                      processTaskResults=None, 
                      processCompletedTask=None, 
                      timeoutInSeconds=None):
        if processTaskResults is None:
            processTaskResults = self.processTaskResults

        if timeoutInSeconds is not None and self.useThreads:
            raise ValueError('To use a timeout, you must use processes with useThreads=False')
        
        self.waitForInputQueue()

        while self.hasTasksStillRunning() or self.hasTasksLeftToLaunch():
            while len(self.runningTasks) < self.maxTaskCount and self.hasTasksLeftToLaunch():
                self.launchTask(target=target)

            processTaskResults(self.outputQueue)

            self.terminateTimedOutTasks(timeoutInSeconds=timeoutInSeconds)
            self.pruneCompletedTasks()
            time.sleep(0.1)

        processTaskResults(self.outputQueue)


    def waitForInputQueue(self, timeout=0.5):
        timeoutTime = time.time() + timeout
        while self.inputQueue.empty() and time.time() < timeoutTime:
            time.sleep(0.1)

    def hasTasksLeftToLaunch(self):
        return not self.inputQueue.empty()

    def hasTasksStillRunning(self):
        return len(self.runningTasks) > 0

    def launchTask(self, target):
        if self.useThreads:
            task=Thread(target=target, args=(self.inputQueue, self.outputQueue))
        else:
            task=Process(target=target, args=(self.inputQueue, self.outputQueue))

        startTime = time.time()
        self.runningTasks.append((task, startTime))
        task.start()
        return task, startTime

    def processTaskResults(self, queue):
        while not queue.empty():
            try:
                results = queue.get(block=False)
                print(json.dumps(results))
            except Empty as err:
                print(err)

    def terminateTimedOutTasks(self, timeoutInSeconds):
        if timeoutInSeconds is None or self.useThreads:
            return

        for (task, startTime) in self.runningTasks:
            if time.time() > startTime+timeoutInSeconds:
                task.terminate()
                # task.join()

    def processCompletedTasks(self, completedTasks):
        for task, startTime in completedTasks:
            if isinstance(task, Process):
                if task.exitcode > 0:
                    print("The process {0} failed with error {1}".format(task.pid, task.exitcode))
                elif task.exitcode == -signal.SIGTERM:
                    print("The process {0} timed out".format(task.pid))
                elif task.exitcode < 0:
                    print("The process {0} was terminated with signal {1}".format(task.pid, self.signalNames[-task.exitcode]))
            else:
                # Threads do not have "an exit code". There is nothing to check.
                pass

    def pruneCompletedTasks(self):
        completedTasks = [ (task,startTime) for task,startTime in self.runningTasks if not task.is_alive()]
        self.runningTasks = [ (task,startTime) for task,startTime in self.runningTasks if task.is_alive()]

        self.processCompletedTasks(completedTasks)



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
    try:
        value = inputQueue.get_nowait()
        product = 1
        for i in range(value):
            product *= (i+1)
        outputQueue.put( (value,  product) )
    except Empty as err:
        pass # not an error


def slowCalculation(inputQueue, outputQueue):
    try:
        value = inputQueue.get_nowait()
        time.sleep(10)
        outputQueue.put( value )
    except Empty as err:
        pass # not an error

def processSimple(queue):
    while not queue.empty():
        try:
            (n, nfactorial) = queue.get_nowait()
            print('Just finished calculating {0}!'.format(n))
        except Empty as err:
            break # we are done

def buggy(inputQueue, outputQueue):
    value = inputQueue.get()
    ouch = "Some text" / value
    outputQueue.put(ouch)

if __name__ == "__main__":
    N = 11
    print("Calculating n! for numbers 0 to {0} (every calculation is independent)".format(N-1))
    print("======================================================================")    

    print("Using threads: fast startup time appropriate for quick calculations")
    engine = ComputeEngine(useThreads=True)
    for i in range(N):
        engine.inputQueue.put(i)
    engine.compute(target=calculateFactorial)

    print("Using processes: long startup time appropriate for longer calculations")
    engine = ComputeEngine(useThreads=False)
    for i in range(N):
        engine.inputQueue.put(i)
    engine.compute(target=calculateFactorial)

    print("Using threads and replacing the processTaskResult function")
    engine = ComputeEngine(useThreads=True)
    for i in range(N):
        engine.inputQueue.put(i)
    engine.compute(target=calculateFactorial, processTaskResults=processSimple)

    print("Using threads with very long calculations and timeout")
    engine = ComputeEngine(useThreads=False)
    for i in range(N):
        engine.inputQueue.put(i)
    engine.compute(target=slowCalculation, timeoutInSeconds=2)

    # print("Using threads with buggy code")
    # engine = ComputeEngine(useThreads=True)
    # for i in range(N):
    #     engine.inputQueue.put(i)
    # engine.compute(target=buggy)

    # print("Using processes with buggy code")
    # engine = ComputeEngine(useThreads=False)
    # for i in range(N):
    #     engine.inputQueue.put(i)
    # engine.compute(target=buggy)
