import logging
#import traceback

from pypes.component import Component
from pypesvds.lib.extras.pdfparser import PDFConverter

log = logging.getLogger(__name__)

class PDFReader(Component):
    __metatype__ = 'ADAPTER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        
        # create an instance of the pdf converter
        self._converter = PDFConverter()

        log.info('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # for each document waiting on our input port
            for doc in self.receive_all('in'):
                try:
                    data = doc.get('data')
                    mime = doc.get_meta('mimetype')

                    # if there is no data, move on to the next doc
                    if data is None:
                        continue
                    
                    # if this is not a  file, move on to the next doc
                    if mime != 'application/pdf':
                        continue

                    # do the conversion
                    # if it fails the converter will return an empty string
                    body = self._converter.convert(data)
                    if body:
                        # write out the body as unicode string
                        doc.set('body', body.decode('utf-8'))
                    else:
                        log.debug('PDF conversion failed')

                    # delete the binary data
                    doc.delete('data')
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

                # send the document to the next component
                self.send('out', doc)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

