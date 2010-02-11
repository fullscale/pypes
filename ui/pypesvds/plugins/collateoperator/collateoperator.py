import logging

from pypes.component import Component

log = logging.getLogger(__name__)

class Collate(Component):
    __metatype__ = 'OPERATOR'

    def __init__(self):
        Component.__init__(self)
        self.add_input('in2', 'Second Input Port')
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        while True:
            doc1 = self.receive('in')
            doc2 = self.receive('in2')

            if doc1 is not None:
                self.send('out', doc1)
            if doc2 is not None:
                self.send('out', doc2)

            if doc1 is None and doc2 is None:
                self.yield_ctrl()

