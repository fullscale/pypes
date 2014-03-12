import logging
#import traceback

from pypes.component import Component
from pypesvds.lib.extras.BeautifulSoup import BeautifulSoup

log = logging.getLogger(__name__)

class HTML(Component):
    __metatype__ = 'ADAPTER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        
        # if true, the raw html will be placed in the html field
        self.set_parameter('keep_html', 'False', ['True', 'False'])

        # log successful initialization message
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # get parameters outside doc loop for better performace
            try:
                keephtml = self.get_parameter('keep_html')
                if keephtml is None:
                    raise ValueError, 'Keep HTML not set'

                if keephtml == 'True':
                    keephtml = True
                else:
                    keephtml = False

            except Exception as e:
                log.error('Component Failed: %s' % self.__class__.__name__)
                log.error('Reason: %s' % str(e))
                self.yield_ctrl()
                continue  # so next time we are called we continue at top  

            # for each document waiting on our input port
            for doc in self.receive_all('in'):
                try:
                    data = doc.get('data')
                    mime = doc.get_meta('mimetype')

                    # if there is no data, move on to the next doc
                    if data is None:
                        continue
                    
                    # if this is not a html file, move on to the next doc
                    if mime != 'text/html':
                        continue

                    # use BeautifulSoup to parse the html
                    html = BeautifulSoup(data)
                    doc.set('title', u''.join(html.title.contents))
                    doc.set('body', u''.join(html.body.findAll(text=True)))

                    # copy raw html to html field if we need to keep it
                    if keephtml:
                        doc.set('html', data)

                    # delete the data field like all adapters should
                    doc.delete('data')

                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

                # send the document to the next component
                self.send('out', doc)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

