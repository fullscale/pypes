import logging
import traceback
import json
from pypesvds.lib.packet import Packet
from pypes.component import Component

log = logging.getLogger(__name__)

class SimpleJSON(Component):
    __metatype__ = 'ADAPTER'

    def __init__(self):
        Component.__init__(self)
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        while True:
            for doc in self.receive_all('in'):
                try:
                    data = doc.get('data')
                    mime = doc.get_meta('mimetype')

                    if data is not None:
                        # this adapter only handles JSON
                        if not mime.startswith('application/json'):
                            log.warn('Bad Content-Type, expecting application/json')
                            log.warn('Ignorning doc: %s' % doc.get('id'))
                            continue
                        else:
                            try:
                                doc.merge(Packet(json.loads(data)), metas=True)
                            except:
                                log.error('Unable to convert data')
                                log.error(traceback.print_exc())

                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))
                    log.error(traceback.print_exc())

                self.send('out', doc)

            self.yield_ctrl()

