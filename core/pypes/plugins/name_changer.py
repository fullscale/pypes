"""Change the keys in the packet through a dictionary"""

import logging

import pypes.component

log = logging.getLogger(__name__)


class NameChanger(pypes.component.Component):
    """
    The run method will get the keys from the input packet and set them back
    in the packet with the new key specified by the value in the init
    dictionary.

    """

    # defines the type of component we're creating.
    __metatype__ = 'TRANSFORMER'

    def __init__(self, dictionary):
        # initialize parent class
        pypes.component.Component.__init__(self)

        # Optionally add/remove component ports
        # self.remove_output('out')
        self._dictionary = dictionary

        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:
            packet = self.receive("in")
            if packet is None:
                self.yield_ctrl()
                continue
            try:
                for key, value in self._dictionary.items():
                    data = packet.get(key)
                    packet.delete(key)
                    packet.set(value, data)
            except:
                log.error('Component Failed: %s',
                          name, exc_info=True)
            self.send("out", packet)
            # yield the CPU, allowing another component to run
            self.yield_ctrl()
