"""Apply a function passed as parameter.
Defaults to passing."""

import logging

import pypes.component

log = logging.getLogger(__name__)


class SingleFunction(pypes.component.Component):
    """
    mandatory input packet attributes:
    - data: the input to the function

    optional input packet attributes:
    - None

    parameters:
    - function: [default: lambda x: x]

    output packet attributes:
    - data: function(data)

    """

    # defines the type of component we're creating.
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)

        # Setup any user parameters required by this component
        # 2nd arg is the default value, 3rd arg is optional list of choices
        self.set_parameter('function', lambda x: x)

        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            function = self.get_parameter('function')

            # for each packet waiting on our input port
            for packet in self.receive_all('in'):
                try:
                    data = packet.get("data")
                    packet.set("data", function(data))
                    log.debug("%s calculated %s",
                              self.__class__.__name__,
                              function.__name__,
                              exc_info=True)
                except:
                    log.error('Component Failed: %s',
                              self.__class__.__name__, exc_info=True)

                # send the packet to the next component
                self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
