import logging
#import traceback

from pypes.component import Component

log = logging.getLogger(__name__)

class Null(Component):
    __metatype__ = 'PUBLISHER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        self.remove_output('out')
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # for each document waiting on our input port
            for doc in self.receive_all('in'):
                try:
                    log.info('Null output: %s' % doc.get('id', \
                                doc.get_meta('url', default='no id')))
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

