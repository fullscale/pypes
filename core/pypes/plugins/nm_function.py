"""Any function from n inputs to m outputs"""

import logging

import pypes.component

log = logging.getLogger(__name__)


def default_function(*args):
    "pass"
    if len(args) == 1:
        return args[0]
    else:
        return args


class NMFunction(pypes.component.Component):
    """
    mandatory input packet attributes:
    - data: for each of the input ports

    parameters:
    - function: [default: merge the inputs into a list if more than one
      input, then replicate over all the outputs]

    output packet attributes:
    - data: each of the M outputs goes to an output port

    """

    # defines the type of component we're creating.
    __metatype__ = 'TRANSFORMER'

    def __init__(self, n=1, m=1):
        # initialize parent class
        pypes.component.Component.__init__(self)

        # Optionally add/remove component ports
        # self.remove_output('out')
        self._n = n
        self._m = m
        if n > 1:
            self._in_ports = ["in"] + ["in{0}".format(i)
                                       for i in range(1, n)]
            for port in self._in_ports:
                self.add_input(port, 'input')
        if m > 1:
            self._out_ports = ["out"] + ["out{0}".format(i)
                                         for i in range(1, m)]
            for port in self._out_ports:
                self.add_output(port, 'output')

        # Setup any user parameters required by this component
        # 2nd arg is the default value, 3rd arg is optional list of choices
        self.set_parameter('function', default_function)

        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            function = self.get_parameter('function')

            # for each packet waiting on our input port
            packets = [self.receive(port)
                       for port in self._in_ports]
            try:
                args = [packet.get("data")
                        for packet in packets]
                results = function(*args)
                if self._m == 1:
                    packet = pypes.packet.Packet()
                    packet.set("data", results)
                    self.send("out", packet)
                elif len(results) == self._m and self._m != 1:
                    for result, port in zip(results, self._out_ports):
                        packet = pypes.packet.Packet()
                        packet.set("data", result)
                        self.send(port, packet)
                else:
                    log.error('Component Failed: %s, %s outputs?',
                              self.__class__.__name__,
                              len(results), exc_info=True)
            except:
                log.error('Component Failed: %s',
                          self.__class__.__name__, exc_info=True)

            # send the packet to the next component
            self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
