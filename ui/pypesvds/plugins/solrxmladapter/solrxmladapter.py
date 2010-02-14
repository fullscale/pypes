import logging
#import traceback
import xml.etree.cElementTree as ET

from pypes.component import Component
from pypesvds.lib.packet import Packet

log = logging.getLogger(__name__)

class SolrXML(Component):
    __metatype__ = 'ADAPTER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
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
                    
                    # if this is not a xml file, move on to the next doc
                    if mime != 'application/xml':
                        continue

                    # solr xml starts with an add tag, if this does not start
                    # with an add tag, move to the next doc
                    xml = ET.XML(data)
                    if xml.tag != 'add':
                        log.debug('Not a Solr XML document')
                        continue

                    # create a new packet for each document in the xml
                    for sdoc in xml.getchildren():
                        if sdoc.tag != 'doc':
                            log.warn('Unexpected tag %s, expecting doc' % \
                                                                    sdoc.tag)
                            continue
                
                        packet = Packet()
                        # each field in the xml becomes a field in the packet
                        for sfield in sdoc.getchildren():
                            if sfield.tag != 'field':
                                log.warn('Unexpected tag %s, expecting field' \
                                                                % sfield.tag)
                                continue

                            fieldname = sfield.get('name', None)
                            fieldval = sfield.text

                            if fieldname is not None:
                                if not isinstance(fieldname, unicode):
                                    fieldname = fieldname.decode('utf-8')

                                if not isinstance(fieldval, unicode):
                                    fieldval = fieldval.decode('utf-8')

                                packet.append(fieldname, fieldval)

                        # send out packet along
                        self.send('out', packet)

                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

