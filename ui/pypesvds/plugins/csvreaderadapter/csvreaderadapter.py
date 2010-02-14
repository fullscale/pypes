import io
import csv
import logging
#import traceback

from pypes.component import Component
from pypesvds.lib.packet import Packet

log = logging.getLogger(__name__)

class CSVReader(Component):
    __metatype__ = 'ADAPTER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def _utf8_encoder(self, data):
        # encodes unicode strings to utf-8
        # needed because the csv module does not support unicode strings
        for line in data:
            yield line.encode('utf-8')

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
                    
                    # if this is not a csv file, move on to the next doc
                    if mime != 'text/csv':
                        continue

                    # adapters should delete the data once it is read
                    doc.delete('data')

                    # convert the data to a file-like object required by 
                    # the csv reader
                    content = io.StringIO(unicode(data, 'utf-8'), 
                                                            newline=None)

                    # create the csv reader object
                    # TODO support for all dialects
                    rows = csv.reader(self._utf8_encoder(content), 
                                                            dialect='excel')
                    for row in rows:
                        document = doc.clone(metas=False)
                        for idx, column in enumerate(row):
                            # column nums start at 1
                            # convert back to unicode string since all
                            # adapters should provide unicode objects
                            document.set('column%d' % (idx + 1), 
                                                    unicode(column, 'utf-8'))

                        self.send('out', document)
                
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

            # yield the CPU, allowing another component to run
            self.yield_ctrl()
