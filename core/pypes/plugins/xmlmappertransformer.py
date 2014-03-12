import os
import zlib
import logging
import unittest
#import traceback
import xml.etree.cElementTree as ET

from pypes.component import Component
from pypesvds.lib.packet import Packet
from pypesvds.lib.extras.elementfilter import findall

log = logging.getLogger(__name__)

class XMLMapper(Component):
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        self.set_parameter('mapfile', 'etc/sample-xmlmap.xml')
        self.set_parameter('input', 'xml')
        self._docroot = './'
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def Text(self, nodes):
        # gets the next for a given node
        def getText(node):
            try:
                # get the nodes text payload
                data = unicode(node.text.strip()) if node.text else None
            except:
                # if node is an attribute then node itself will be a string
                text.append(unicode(node))
                return ' '.join(text)
            else:
                # append data to text buffer
                if data:
                    text.append(data)

                # recurse down to child nodes. This is necessary for "mixed"
                # content (i.e., <body>Some <b>bold</b> text</body>)
                for child in node.getchildren():
                    # grab the tail of the current node
                    tail = unicode(child.tail.strip()) if child.tail else None
                    # look for children
                    getText(child)
                    if tail:
                        text.append(tail)
            return ' '.join(text)

        content = []
        for node in nodes:
            text = []
            content.append(getText(node))

        return content

    def _parse_config(self, config):
        # TODO validate the config file
        mappings = []
        for c in config.getchildren():
            attrs = {}
            attrs['path'] = c.get('path')
            attrs['name'] = c.get('name')
            attrs['mode'] = c.get('mode')
            attrs['comp'] = c.get('comp')

            mappings.append(attrs)
            self._parse_config(c)

        self._mappings = mappings

    def _do_mapping(self, doc):
        data = doc.get(self._infield, '')
        if doc.is_multivalued(self._infield):
            log.debug('Multivalued fields not supported.  Using first value')
            data = data[0]

        xml = ET.XML(data.encode('utf-8'))

        roots = xml.findall(self._docroot)
        for root in roots:
            newdoc = doc.clone(metas=False)      
            for mapping in self._mappings:

                # determine path
                path = mapping['path']
                if self._docroot == './':
                    # TODO Explain this better
                    path = '/'.join(path.split('/')[3:])

                name = mapping['name']
                mode = mapping['mode']
                comp = mapping['comp']

                content = []
                try:
                    multi = False
                    if mode == 'multi':
                        multi = True
                    
                    nodes = findall(root, path)
                    content = self.Text(nodes)

                    if content:
                        if mode == 'append':
                            payload = ' '.join(content)
                        elif mode == 'multi':
                            payload = content
                        else:
                            payload = content[0]
                    else:
                        payload = u''

                    if comp == 'true':
                        payload = zlib.compress(payload, 1)

                    try:
                        payload = payload.strip()
                        if comp != "true":
                            if not isinstance(payload, unicode):
                                payload = payload.decode('utf-8')
                    except:
                        pass

                    newdoc.set(name, payload, multi=multi)

                except Exception as e:
                    log.error('Error parsing xml file: %s' % \
                                            doc.get_meta('url', default=''))
                    log.error('Reason: %s' % str(e))
                    #traceback.print_exc()
                    newdoc.set(name, u'')

            self.send('out', newdoc)     

    def run(self):
        # Define our components entry point
        last_mtime = 0
        config = None
        while True:

            # get parameters outside doc loop for better performace
            try:
                mapfile = self.get_parameter('mapfile')
                if mapfile is None:
                    raise ValueError, 'Map File not set'

                infield = self.get_parameter('input')
                if infield is None:
                    raise ValueError, 'Input is not set'

                # set the input field to be used later
                self._infield = infield

                # starting mtime
                mtime = 1
                try:
                    mtime = os.stat(mapfile)[8]
                    log.debug('(mtime: %s, last_mtime: %s)' % (mtime, 
                                                                last_mtime))
                except:
                    log.warn('Could not read modification time from map file')
                
                # try to load the file if the file has been modified
                # or not been loaded yet
                if mtime > last_mtime or config is None:
                    try:
                        text = open(mapfile).read()
                        config = ET.XML(text)
                    except:
                        log.warn('Error reading map file')
                    else:
                        docroot = config.get('docroot')
                        if docroot is None:
                            docroot = './'
                        else:
                            # TODO do some better validation on this
                            docroot = '/'.join(docroot.split('/')[3:])
        
                        self._docroot = docroot
                        self._parse_config(config)
                        last_mtime = mtime

                # if we don't have a map file raise an error to stop processing
                if config is None:
                    raise ValueError, 'Unable to load map file'                  

            except Exception as e:
                log.error('Component Failed: %s' % self.__class__.__name__)
                log.error('Reason: %s' % str(e))
                self.yield_ctrl()
                continue # so next time we are called we continue at the top               

            # for each document waiting on our input port
            for doc in self.receive_all('in'):
                try:
                    self._do_mapping(doc)
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

class XMLUnitTest(unittest.TestCase):

    def setUp(self):
        text = '<metamap><meta name="body" path="//html/body" mode="append"' \
                                                ' comp="false" /></metamap>'
        elem = ET.XML(text)
        self.m = XMLMapper()
        self.m._infield = 'data'
        self.m._parse_config(elem)

    def testmapper(self):

        # defines a fake packet object for testing purposes
        class FakePacket(dict):
            def delete(self, field):
                del self[field]

            def clone(self, metas):
                return self

            def set(self, name, val, multi=False):
                self[name] = val

            def is_multivalued(self, field):
                return False

        print 'Running simple parse test'
        doc = FakePacket({'data':'<html><body>Some bold text</body></html>'})
        self.m._do_mapping(doc)
        self.assertEqual(doc['body'], 'Some bold text', 
                                'Failed simple parse test: %s' % doc['body'])

        print 'Running multi node test'
        doc = FakePacket({'data':'<html><body>Some bold text</body><body>' \
                                            'Some more text</body></html>'})
        self.m._do_mapping(doc)
        self.assertEqual(doc['body'], 'Some bold text Some more text', 
                                    'Failed multi node test: %s' % doc['body'])

        print 'Running simple mixed content test'
        doc = FakePacket({'data':'<html><body>Some <b>bold</b> text</body>' \
                                                                    '</html>'})
        self.m._do_mapping(doc)
        self.assertEqual(doc['body'], 'Some bold text', 
                        'Failed simple mixed content test: %s' % doc['body'])

        print 'Running multi-child mixed content test'
        doc = FakePacket({'data':'<html><body>Some <b>bold and</b> <i>' \
                                'italicized</i> courier text</body></html>'})
        self.m._do_mapping(doc)
        self.assertEqual(doc['body'], 'Some bold and italicized courier text', 
                    'Failed multi-child mixed content test: %s' % doc['body'])

        print 'Running deeply nested mixed content test'
        doc = FakePacket({'data':'<html><body>Some <b>bold and <i>italicized' \
                                    '</i> courier</b> text</body></html>'})
        self.m._do_mapping(doc)
        self.assertEqual(doc['body'], 'Some bold and italicized courier text', 
                    'Failed deeply nested mixed content test: %s' % doc['body'])

        print 'Running stray tail element test'
        doc = FakePacket({'data':'<html><body>Some bold text</body>end</html>'})
        self.m._do_mapping(doc)
        self.assertEqual(doc['body'], 'Some bold text', 
                            'Failed stray tail element test: %s' % doc['body'])

if __name__ == '__main__':
    unittest.main()


