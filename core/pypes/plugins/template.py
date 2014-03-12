"""Template for a new pipeline component."""

from __future__ import division, print_function

import logging

import pypes.component

log = logging.getLogger(__name__)


class TemplateComponent(pypes.component.Component):
    """
    mandatory input packet attributes:
    - att1:

    optional input packet attributes:
    - opt:

    parameters:
    - par1: [default: blah]

    output packet attributes:
    - output attribute:

    """

    # defines the type of component we're creating.
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)

        # Optionally add/remove component ports
        # self.remove_output('out')
        # self.add_input('in2', 'A description of what this port is used for')

        # Setup any user parameters required by this component
        # 2nd arg is the default value, 3rd arg is optional list of choices
        #self.set_parameter('MyParam', 'opt1', ['opt1', 'opt2', 'opt3'])

        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # myparam = self.get_parameter('MyParam')

            # for each packet waiting on our input port
            for packet in self.receive_all('in'):
                try:
                    # perform your custom logic here
                    pass
                except:
                    log.error('Component Failed: %s',
                              self.__class__.__name__, exc_info=True)

                # send the packet to the next component
                self.send('out', packet)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
