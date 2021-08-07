from multiprocessing import Pool, Queue, Process, SimpleQueue, cpu_count
from threading import Thread
from queue import Empty
import time
import json
import signal

"""
A class to run many tasks in parallel when they are mostly independent.  This engine is perfectly
appropriate for long, repetitive calculations (for example: computing f(x) on a large
dataset).

They will make use of all processors and cores and will use either threads or
child processes. Either way, both are referred to as "Tasks" in the code. You
decide which one you use when you create the ComputeEngine:

engine = ComputeEngine(maxTaskCount=None, useThreads=True):

Differences between threads and processes:

* Threads start quickly (ms) and share the memory with the calling thread.
  Processes require a copy of all the memory used, and will therefore take
  some time to actually start (~1s) Typically, threads will be used when you
  perform many small calculations.  If a calculation is really long, then a
  process can be more appropriate as 1) it does not suffer much from the
  startup time and 2) any misbehaving code cannot crash your main code.
* If you use Processes, it is possible to set a timeout and terminate the task
  when it is taking too long. You can return an exit code and check it. It is
  not possible to terminate a thread.
* A badly behaving Thread can corrupt and crash your program (by modifying
  memory that it should not for instance).  A Process cannot crash the
  calling program because it is running in a separate space.

To use this engine:

1. create an engine = ComputeEngine()
2. put the input data onto the "input queue" with engine.inputQueue.put(someData)
3. write a function someFunction(someData) that takes an argument.
   it is possible to reuse a function that takes many arguments, in which 
   case you put all arguments as a tuple, in the order they will be needed for 
   the call to someFunction.
4. that function will take the argument(s), and return a result.  The inputArgs and the results
   are put into the outputQueue as a tuple.
5. you can put whatever you want in results (numbers, dictionaries, tuples, other objects, etc...)
6. call engine.compute(), which will start many tasks (either processes or threads).  The function
   will return when all the tasks have run.
7. As the calculation progresses, the compute() function will call 
   a user-provided function that takes inputArgs and results as argument
   or the default function (which prints the results to the screen).
8. If using processes, it is possible to terminate a long running task with a timeout
9. You can change the processTaskResults() function to your own function (to save to disk for instance)

"""

class ComputeEngine:
    lastMarker = "ComputeEngine.LastInput"
    doneMarker = "ComputeEngine.Done"
    def __init__(self, maxTaskCount=None, useThreads=True):
        """
        ComputeEngine that will launch parallel tasks to compute a function on a list of arguments
        (stored in a Queue).

        The engine will start at most maxTaskCount (number of cpu/cores is the default).
        useThreads=True will use threads and False will use processes.

        When using processes, it is possible to terminate a task that is taking too long.
        When using threads, it is possible to access shared memory (with you own locks).

        """
        self.inputQueue = Queue()
        self.outputQueue = Queue()
        self.runningTasks = []
        self.completedTasks = []
        self.useThreads = useThreads
        self.isComputationDone = False
        if maxTaskCount is None:
            self.maxTaskCount = cpu_count()
        else:
            self.maxTaskCount = maxTaskCount
        self.signalNames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items())) if v.startswith('SIG') and not v.startswith('SIG_'))

    def __del__(self):
        """
        Upon deleting this object, we terminate all tasks if we can.
        """
        if not self.useThreads:
            [ task.terminate() for task,startTime in self.runningTasks]

        self.inputQueue.close()
        self.inputQueue.join_thread()
        self.outputQueue.close()
        self.outputQueue.join_thread()
        
    def emptyQueues(self):
        try:
            while True:
                self.inputQueue.get_nowait()
        except:
            pass

        try:    
            while True:
                self.outputQueue.get_nowait()
        except:
            pass

    def compute(self, target, 
                      unwrapArguments = False,
                      processTaskResults=None, 
                      processCompletedTask=None, 
                      timeoutInSeconds=None):
        """
        Call the target function from a separate task (thread or process) with
        whatever was put onto the inputQueue as parameters. Typically, the
        target function will get its arguments from the inputQueue and will
        put the result on the outputQueue.

        The target function must:
            1. accept a single argument, i.e. whatever is put onto the inputQueue
            2. or accept many arguments and you set the unwrapArguments=True

        As the calculation progresses, the outputQueue is processed.  The
        default processing prints everything to screen and empties the queue.
        You can provide your own function processTaskResults
        (inputArgs, results) that must accept the inputArg and results as
        arguments. Results is pushed to the outputQueue as a tuple if
        multiple values are returned.

        When using processes, it is possible to kill a task that is taking too long. It is not
        possible with threads.

        When tasks are completed, you get a last chance to do something with them with 
        processCompletedTask(listOfTasks).
        """
        if timeoutInSeconds is not None and self.useThreads:
            raise ValueError('To use a timeout, you must use processes with useThreads=False')

        self.waitForInputQueue()
        self.inputQueue.put(self.lastMarker)

        isComputationDone = False
        while not isComputationDone:
            if self.hasTasksLeftToLaunch():
                while len(self.runningTasks) < self.maxTaskCount:
                    self.launchTask(target=target, unwrapArguments=unwrapArguments)

            isComputationDone = self.processOutputQueue(userProcessFunction=processTaskResults)

            self.terminateTimedOutTasks(timeoutInSeconds=timeoutInSeconds)
            self.pruneCompletedTasks()

            time.sleep(0.1)

        self.pruneCompletedTasks()
        assert(self.inputQueue.empty())

    def waitForInputQueue(self, timeout=0.3):
        """
        A queue may appear empty immediately after putting an element into it
        because it actually puts everything into a buffer and an internal
        thread will put it onto the queue. We really want to have a non-empty
        inputQueue for calculations so we check here with a short timeout in
        case it is really empty.
        """
        timeoutTime = time.time() + timeout
        while self.inputQueue.empty() and time.time() < timeoutTime:
            time.sleep(0.1)

    def hasTasksLeftToLaunch(self) -> bool:
        """
        If the inputQueue is not empty, then we still have tasks to launch.
        """
        return not self.inputQueue.empty()

    def hasTasksStillRunning(self) -> bool:
        """
        When tasks that are running are alive, then we obviously still have tasks running
        """
        return len([ task for task,startTime in self.runningTasks if task.is_alive()]) != 0

    def launchTask(self, target, unwrapArguments=False)  -> (object, float):
        """
        Launch either a Thread or a Process with the target processing the inputQueue and outputQueue.

        We keep an internal timer with the start time of the task to determine if it has
        timed out in the future.
        """
        if self.useThreads:
            task=Thread(target=ComputeEngine.targetWrapper, args=(target, unwrapArguments, self.inputQueue, self.outputQueue))
        else:
            task=Process(target=ComputeEngine.targetWrapper, args=(target, unwrapArguments, self.inputQueue, self.outputQueue))

        startTime = time.time()
        self.runningTasks.append((task, startTime))
        task.start()

        return task, startTime

    def processOutputQueue(self, userProcessFunction=None) -> bool:
        """
        We get (and remove) elements from the outputQueue. The default action is to print everything
        to screen,but this function can be replaced by your own when calling compute().
        It returns True when everything has been processed (that is, when the element corresponds to 
        the lastMarker and the result is doneMarker)
        """
        while not self.outputQueue.empty():
            try:
                inputArgs, results = self.outputQueue.get(block=False)
                if inputArgs == ComputeEngine.lastMarker and results == ComputeEngine.doneMarker:
                    return True
                else:
                    if userProcessFunction is not None:
                        userProcessFunction(inputArgs, results)
                    else:
                        self.defaultProcessFunction(inputArgs, results)
                    return False

            except Empty as err:
                return False

    def defaultProcessFunction(self, inputArgs, results):
        print(results)

    def terminateTimedOutTasks(self, timeoutInSeconds):
        """
        If tasks are taking too long, we terminate (kill) them. This is only possible with processes.
        """
        if timeoutInSeconds is None:
            return

        for (task, startTime) in self.runningTasks:
            if time.time() > startTime+timeoutInSeconds:
                if not self.useThreads:
                    task.terminate()
                else:
                    print("Task has timed out but threads cannot be terminated")
                task.join()

    def processCompletedTasks(self, completedTasks):
        """
        The last chance to manipulate a completed task before it is deleted. Here
        we simply warn the user if the task timedout.
        """
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
            task.join()

    def pruneCompletedTasks(self):
        """
        Internal function to keep a list of tasks that are alive (i.e. still running).
        Completed tasks (normal or terminated) get processed by processCompletedTasks() before being 
        deleted.
        """
        newlyCompletedTasks = [ (task,startTime) for task,startTime in self.runningTasks if not task.is_alive()]
        self.runningTasks = [ (task,startTime) for task,startTime in self.runningTasks if task.is_alive()]

        self.processCompletedTasks(newlyCompletedTasks)
        self.completedTasks.extend(newlyCompletedTasks)

    @classmethod
    def targetWrapper(cls, target, unwrapArguments, inputQueue, outputQueue):
        """
        This function does a bit a management and then calls the user-provided function
        for the computation. It manages the input and output queues to flag the last
        element and when the computation is done.  This is essential, as we cannot rely 
        on watching the queues (they change from different threads and could be temporarily empty).

        It must be a @classmethod, because everything with it (including self) is sent to the
        process and must be "picklable".  ComputeEngine is not picklable.
        """
        try:
            inputArgs = inputQueue.get_nowait()
            if inputArgs != ComputeEngine.lastMarker:
                if not unwrapArguments:
                    result = target(inputArgs)
                else:
                    result = target(*inputArgs)
            else:
                result = ComputeEngine.doneMarker
            outputQueue.put( (inputArgs, result) )
        except Empty as err:
            return

class DBComputeEngine(ComputeEngine):
    def __init__(self, database, maxTaskCount=None, useThreads=True):
        super().__init__(maxTaskCount=maxTaskCount, useThreads=useThreads)
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
        self.waitForInputQueue()

def calculateFactorial(value) -> float:
    product = 1
    for i in range(value):
        product *= (i+1)
    return (value,  product)

def calculationWith3Arguments(value1, value2,value3) -> float:
    product = 1
    for i in range(value1):
        product *= (i+1)
    return (value1, value2, value3, product)


def slowCalculation(value):
    time.sleep(10)
    return value

def processResults(args, results)->bool:
    print('Just finished calculating {0}!'.format(args))

if __name__ == "__main__":
    N = 10
    print("Calculating n! for numbers 0 to {0} (every calculation is independent)".format(N-1))
    print("======================================================================")    

    print("Simple calculation, no parallelism")
    for i in range(N):
        print(calculateFactorial(i))


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
    engine.compute(target=calculateFactorial, processTaskResults=processResults)

    print("Using threads with a function that takes 3 arguments")
    engine = ComputeEngine(useThreads=True)
    for i in range(N):
        engine.inputQueue.put( (i,i+1,i+2))
    engine.compute(target=calculationWith3Arguments, unwrapArguments=True)
