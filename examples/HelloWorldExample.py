# load the pypes framework
from pkg_resources import require
require('pypes')

# import the Dataflow module
from pypes.pipeline import Dataflow
# import the Component Interface
from pypes.component import Component
# import the built-in ConsoleOutputWriter
from pypes.filters import ConsoleOutputWriter

class HelloWorld(Component):
    __metatype__ = 'ADAPTER'

    def __init__(self):
        Component.__init__(self)

    def run(self):
        while True:
            for data in self.receive_all('in'):
                message = 'Hello %s' % data
                self.send('out', message)
            self.yield_ctrl()

hello   = HelloWorld()          # our custom component 
printer = ConsoleOutputWriter() # writes to console (STDOUT)

Network = {
       hello: {printer:('out','in')}
}

if __name__ == '__main__':
    # create a new data flow
    p = Dataflow(Network)
    # send some data through the data flow
    for name in ['Tom', 'Dick', 'Harry']:
        p.send(name)
    # shut down the data flow
    p.close() 
