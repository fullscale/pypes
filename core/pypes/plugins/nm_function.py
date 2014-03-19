"""Any function from n inputs to m outputs"""

import logging
from itertools import zip_longest

import pypes.component

log = logging.getLogger(__name__)


def default_function(*args):
    "pass"
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
        self._in_ports = ["in"]
        self._out_ports = ["out"]
        if n > 1:
            self._in_ports += ["in{0}".format(i)
                               for i in range(1, n)]
            for port in self._in_ports:
                self.add_input(port, 'input')
        if m > 1:
            self._out_ports += ["out{0}".format(i)
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
            name = function.__name__

            packets = [self.receive(port)
                       for port in self._in_ports]
            log.debug("function %s received %s", name, packets)
            # for each packet waiting on our input port
            try:
                args = [packet.get("data")
                        for packet in packets]
                results = function(*args)
                log.debug("%s: results %s",
                          name,
                          results)
                if self._m == 1:
                    packet = packets[0]
                    packet.set("data", results[0])
                    self.send("out", packet)
                elif self._m > 1 and len(results) <= self._m:
                    for result, port in zip_longest(results,
                                                    self._out_ports,
                                                    fillvalue=results[-1]):
                        packet = pypes.packet.Packet()
                        for key, value in packets[0]:
                            log.debug("%s %s %s", name,
                                      key, value)
                            packet.set(key, value)
                        packet.set("data", result)
                        log.debug("%s: sending %s to %s",
                                  name,
                                  packet.get("data"),
                                  port)
                        self.send(port, packet)
                else:
                    raise ValueError("too many results!")
            except:
                log.error('Component Failed: %s',
                          name, exc_info=True)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
