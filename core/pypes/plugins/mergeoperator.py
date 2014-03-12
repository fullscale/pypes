import logging
#import traceback

from pypes.component import Component

log = logging.getLogger(__name__)

class Merge(Component):
    __metatype__ = 'OPERATOR'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        self.add_input('in2', 'Second Input Port')
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:
            # get a document from each input port
            doc1 = self.receive('in')
            doc2 = self.receive('in2')

            # if we have 2 documents, try to merge them
            if doc1 is not None and doc2 is not None:
                try:
                    newdoc = doc1.clone()
                    newdoc.merge(doc2, metas=True)
                except Exception as e:
                    log.info('Merge failed, sending unmerged documents')
                    self.send('out', doc1)
                    self.send('out', doc2)
                else:
                    self.send('out', newdoc)

            # there was no document on input port 1
            elif doc1 is not None:
                self.send('out', doc1)

            # there was no document on input port 2
            elif doc2 is not None:
                self.send('out', doc2)

            # there was no documents on any input ports
            else:
                self.yield_ctrl()

