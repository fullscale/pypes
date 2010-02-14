import logging
#import traceback

from pypes.component import Component

log = logging.getLogger(__name__)

class TextReader(Component):
    __metatype__ = 'ADAPTER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        # define our components entry point
        while True:

            # for each document waiting on our input port
            for doc in self.receive_all('in'):
                try:
                    data = doc.get('data')
                    mime = doc.get_meta('mimetype')

                    # if there is no data, move on to the next doc
                    if data is None:
                        continue
                    
                    # if this is not a plain text file, move on to the next doc
                    if mime != 'text/plain':
                        continue

                    # move data to text field and delete data
                    doc.set('text', data.decode('utf-8'))
                    doc.delete('data')

                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

                # send the document to the next component
                self.send('out', doc)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

