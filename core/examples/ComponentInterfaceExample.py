# load the pypes framework
from pkg_resources import require
require('pypes')

import stackless

from pypes.pype import Pype
from pypes.component import Component
from pypes.filters import ConsoleOutputWriter

# sample component
class HelloWorld(Component):
    def __init__(self):
        Component.__init__(self)

    def run(self):
        while True:
            for data in self.receive_all('in'):
                message = 'Hello %s' % data
                self.send('out', message)
            
            self.yield_ctrl()

# run our example
if __name__ == '__main__':
    """ The following example is meant to demonstrate how the component
        interface looks and work. The following example can be written
        in a simpler fashion by leveraging some of the abstraction
        that the pypes framework offers:

            pipeline = { hello: {printer:('out','in')} }
            df = Dataflow(pipeline)

            for name in ['Tom', 'Dick', 'Harry']:
                df.send(name)

            df.close()

        The above code segment is equivilent to the following example
        that produces the same work flow by hand.
    """
    # create an instance of the Print() component
    printer = ConsoleOutputWriter()

    # create an instance of our custom HelloWorld() component
    print 'Creating HelloWorld() component'
    hello = HelloWorld()

    print 'This component has these default input ports:', hello.get_in_ports()
    print 'This component has these default output ports:', hello.get_out_ports()

    # we can add an input/output but this is typically used
    # inside the actual custom component code. A custom component
    # can define additional ports which it handles.
    print 'Adding new output port "test1" to HelloWorld component...'
    hello.add_output('test1', 'this is where the port description would go')

    print 'This component now has these output ports:', hello.get_out_ports()

    print 'Description for port "in" -->', hello.get_port_description('in')

    if hello.has_port('test1'):
        print 'Description for port "test1" -->', \
                                hello.get_port_description('test1')

    print 'Description for port "out" -->', hello.get_port_description('out')

    if hello.has_port('test2'):
        print 'HelloWorld contains a port called "test2"'
    else:
        print 'HelloWorld does not contain a port called "test2"' 

    print 'Connection status for HelloWorld port "out":', \
                                                    hello.is_connected('out')

    # we need two pypes (2 edges)
    p1 = Pype()
    p2 = Pype()

    # A component is written as a stackless tasklet
    # We need to let stackless know. We only need a reference
    # to the first tasklet which is where we will send data 
    t = stackless.tasklet(hello.run)()
    stackless.tasklet(printer.run)()

    print 'Connecting ports now...'
    # now we connect the nodes using the pypes we created
    hello.connect_input('in', p1)
    hello.connect_output('out', p2)
    printer.connect_input('in', p2)
    
    # Now the connection status on "out" should be True since we've just connected it
    print 'Connection status now for HelloWorld port "out":', \
                                                    hello.is_connected('out')

    # send some data through this pipeline
    print 'Sending some test data...\n'
    for name in ['Tom', 'Dick', 'Harry']:
        p1.send(name)
        # we need to "trigger" the first stackless tasklet
        t.run()

