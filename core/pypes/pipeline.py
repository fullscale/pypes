"""Provides high level routines and objects that convert user
input such as graphs into actual functioning data flow objects.

This module takes care of setting up the scheduler and providing
an input channel from which the calling application can submit
data.

It also provides the pooling logic which ensures that each instance
of the data flow model is run on a different CPU/core. At the same
time, it provides an abstraction making the pool appear as a single
unified entity. 

Data fed is actually load balanced in a round-robin fashion across
all instances in the workflow pool.

Uses the L{multiprocessing} module and requires Python >= 2.6
"""
import stackless
import traceback
from multiprocessing import Process, Pipe, Queue

from scheduler import sched

def pipeline(graph):
    """Initializes the main scheduling tasklet.

    @param graph: The work flow graph 
    @type graph: Python dict organized as a graph
    @return: L{stackless.channel}
    """
    ch = stackless.channel()
    stackless.tasklet(sched)(ch, graph).run()
    return ch

class Instance:
    """Represents a single instance of a data flow model.
    """
    def __init__(self, channel):
        """Class constructor

        @param channel: the L{stackless.channel} this instance will listen on
        @type channel: L{stackless.channel}
        """
        self.sender, self.recipient = Pipe()
        self.channel = channel

    def execute(self, graph):
        """This is the entry point for the process.

        This method will be forked into a separate process
        from the caller using the L{multiprocessing.Process}
        method.

        The actual pipeline must be created here so that it
        lives inside a separate process than teh caller. This
        is vital to how the scheduling works in stackless Python.

        @see: L{Dataflow.add_process}

        @param graph: The data flow graph
        @type graph: dict
        
        @return: Nothing
        """
        pipe = pipeline(graph)
        self._run(pipe)

    def _run(self, pipe):
        """The main loop that runs inside the new process.

        This runs in an event loop waiting on data using
        a L{multiprocessing.Pipe} which allows two processes
        to communicate using shared memory.

        If no data is available then it blocks and waits.

        @param pipe: The communcation channel used to wake this method
        @type pipe: L{multiprocessing.Pipe}
        @return: Nothing
        """
        while True:
            data = self.recipient.recv()
            if data == -1:
                break
            try:
                pipe.send(data)
            except:
                print 'OOPS! - Component Failure'
                traceback.print_exc()

    def send(self):
        """Sends data into the new process 

        This runs in an event loop waiting on data using
        a L{multiprocessing.Queue}. When data arrives, it is
        sent immediately into the new process using a
        L{multiprocessing.Pipe}.

        If no data is available then it blocks and waits.

        This method serves as a proxy that can shuttle
        data from the main calling process to the newly
        created process that was created using L{execute}

        @return: Nothing
        """
        while True:
            data = self.channel.get()
            if data == -1:
                self.sender.send(-1)
                break
            else: 
                self.sender.send(data)

class Dataflow:
    """Provides an abstraction of a group of L{Instance}s.

    A Dataflow represents a pool of data flow L{Instance}s.
    The caller simply sends data to the Dataflow and the 
    Dataflow takes care of load balancing across all available
    L{Instance}s.

    It uses L{multiprocessing.Queue} to send data to the
    instance pool.
    """
    def __init__(self, graph, n=1):
        """Class constructor

        @param graph: the data model in graph notation
        @type graph: dict
        @param n: The number of instances to start (pool size)
                  This number should the number of CPUs and/or cores
                  available on the architecture running the code.
                  Defaults to 1
        @type n: int
        """
        self.queue = Queue()
        self.pipeline = graph
        self.size = n
        self.processes = []

        for i in range(self.size):
            self.add_process()

    def send(self, data):
        """Sends data to the next available L{Instance}
        
        Uses a stackless channel to communicate with the
        L{Instance} tasklet.

        @see: L{add_process}
        @param data: The data being sent
        @type data: Application Specific
        """
        self.queue.put(data)

    def close(self):
        """ Shuts down this workflow and all associated L{Instance}s

        Sends a terminate signal to all the tasklets causing them to
        return which in turn causes the process running that L{Instance}
        to return/exit as well.

        This should lead to a clean shutdown based on the shear nature
        of stackless tasklets. Any data will be flushed (completed) before
        exiting.
        """
        for p in self.processes:
            self.queue.put(-1)

    def add_process(self):
        """Adds a new process (L{Instance} to the Dataflow pool.

        Creates a new L{Instance} and runs it inside a L{multiprocessing.Process}
        """
        process = Instance(self.queue)
        self.processes.append(process)
        Process(target=process.send).start()
        Process(target=process.execute, args=(self.pipeline,)).start()

    def remove_process(self):
        """Removes an instance from the Dataflow pool.

        Shuts down one instance in the pool.
        @todo: Which Instance do we stop? Right now it's the last that was added
               which may be good enough. What if it's the only instance?
        """
        process = self.processes.pop()
        self.queue.put(-1)

