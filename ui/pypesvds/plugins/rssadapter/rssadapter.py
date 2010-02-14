import logging
#import traceback

from pypes.component import Component
from pypesvds.lib.extras import feedparser

log = logging.getLogger(__name__)

class RSS(Component):
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

                    # adapters should delete the data
                    doc.delete('data')

                    parsedfeed = feedparser.parse(data)
                    feeditems = ['author', 'language', 'link', 'publisher',
                                 'title', 'subtitle', 'updated', 'description']
                    itemitems = ['author', 'summary', 'link', 'id', 'title',
                                 'updated', 'published']

                    # set feed attributes as metadata
                    for fitem in feeditems:
                        try:
                            fval = parsedfeed.feed[fitem]
                            if isinstance(fval, (str, unicode)):
                                doc.set_meta('feed_%s' % fitem, fval)
                            else:
                                log.debug('Feed attribute %s is not a string' \
                                                            ', skipping' % fval)
                        except:
                            log.debug('Feed attribute %s does not exist' % \
                                                                        fitem)

                    # loop though each item (story) in the rss and send it
                    # as a separate packet.  Set any attributes as
                    # attributes on the packet.
                    for item in parsedfeed.entries:
                        cloned = doc.clone(metas=True)
                        for iitem in itemitems:
                            try:
                                ival = item[iitem]
                                if isinstance(ival, (str, unicode)):
                                    cloned.set(iitem, ival)
                                else:
                                    log.info('Item attribute %s is not a ' \
                                                    'string, skipping' % iitem)
                            except:
                                log.debug('Item attribute %s does not exist' \
                                                                        % iitem)

                        self.send('out', cloned)                                              

                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

