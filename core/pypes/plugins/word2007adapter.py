import zipfile
import logging
#import traceback
import cStringIO
from xml.dom.minidom import parseString

from pypes.component import Component

log = logging.getLogger(__name__)

class Word2007(Component):
    __metatype__ = 'ADAPTER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def _unzip(self, zipdata):
        buf = cStringIO.StringIO()
        buf.write(zipdata)
        unzipped = zipfile.ZipFile(buf)
        try:
            xml = unzipped.read('word/document.xml')
            props = unzipped.read('docProps/core.xml')
        except:
            log.debug('Error reading document contents')
            xml = props = None
        finally:
            unzipped.close()
            buf.close()
        
        return (xml, props)

    def _extract_body(self, xml):
        data = []
        try:
            dom = parseString(xml)
            elements = dom.getElementsByTagName('w:t')
            for element in elements:
                for node in element.childNodes:
                    data.append(node.data)

        except Exception as e:
            log.debug('Error parsing body')
            log.debug('Reason: %s' % str(e))

        return ' '.join(data)

    def _extract_props(self, props):
        p = {}
        try:
            dom = parseString(props)
            pairs = [('title', 'dc:title'), ('author', 'dc:creator'),
                 ('keywords', 'cp:keywords'), ('comments', 'dc:description')]

            for prop, tag in pairs:
                # grab the property (if it exists)
                try: 
                    elem = dom.getElementsByTagName(tag)
                    p[prop] = elem[0].childNodes[0].data
                except: 
                    pass
        except Exception as e:
            log.debug('Error parsing properties')
            log.debug('Reason: %s' % str(e))

        return p

    def run(self):
        # Define our components entry point
        while True:

            # for each document waiting on our input port
            for doc in self.receive_all('in'):
                try:
                    data = doc.get('data')
                    mime = doc.get_meta('mimetype')
                    fname = doc.get_meta('url', default='unknown')

                    # if there is no data, move on to the next doc
                    if data is None:
                        continue
                    
                    # if this is not a MS Word doc, move on to the next doc
                    if mime != 'application/msword':
                        continue

                    # Word2007 docs should end in docx
                    if fname[fname.rfind('.'):].lower() != '.docx':
                        log.debug('Document does not end in .docx')
                        continue

                    # word documents are zipped xml files
                    # get the main and properties xml files 
                    xml, props = self._unzip(data)
                    if (xml or props) is None:
                        # TODO should we continue to let another adapter
                        # try or should we raise an error and pass the 
                        # document along?  
                        continue

                    # parse the body of the word document
                    body = self._extract_body(xml)
                    if not body:
                        log.debug('Document body is empty')
                    else:
                        doc.set('body', body)

                    # try to extract some properties
                    for key, val in self._extract_props(props).items():
                        doc.set(key, val)

                    # delete data since we are an adapter
                    doc.delete('data')

                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

                # send the document to the next component
                self.send('out', doc)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

