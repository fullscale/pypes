import httplib
import logging
#import traceback
from xml.etree.ElementTree import _escape_cdata

from pypes.component import Component

log = logging.getLogger(__name__)

class Solr(Component):
    __metatype__ = 'PUBLISHER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        
        # remove the output port since this is a publisher
        self.remove_output('out')

        # solr host, port, and path (core)
        self.set_parameter('host', 'localhost')
        self.set_parameter('port', 8983)
        self.set_parameter('path', '/solr')

        # if we should commit after each batch
        # set to OFF if using the auto commit feature
        self.set_parameter('commit', 'True', ['True', 'False'])

        # wait_flush and wait_searcher
        self.set_parameter('wait_flush', 'True', ['True', 'False'])
        self.set_parameter('wait_searcher', 'True', ['True', 'False'])

        # overwrite previously commited docs with same id
        self.set_parameter('overwrite', 'True', ['True', 'False'])

        # commit within time in milliseconds (0 = disabled)
        self.set_parameter('commit_within', '0')

        # log successful initialization message
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def _escape(self, val):
        result = None
        if isinstance(val, (str, unicode)):
            result = _escape_cdata(val)
        else:
            try:
                strval = val.__str__()
            except:
                pass
            else:
                result = _escape_cdata(strval)

        return result

    def run(self):
        # Define our components entry point
        while True:

            # get parameters outside doc loop for better performace
            try:
                host = self.get_parameter('host')
                if host is None:
                    raise ValueError, 'Host not set'

                port = self.get_parameter('port')
                if port is None:
                    raise ValueError, 'Port not set'

                path = self.get_parameter('path')
                if path is None:
                    raise ValueError, 'Path not set'

                commit = self.get_parameter('commit')
                if commit is None:
                    raise ValueError, 'Commit not set'

                commit_within = self.get_parameter('commit_within')
                if commit_within is None:
                    raise ValueError, 'Commit Within not set'

                wait_flush = self.get_parameter('wait_flush')
                if wait_flush is None:
                    raise ValueError, 'Wait Flush not set'

                wait_searcher = self.get_parameter('wait_searcher')
                if wait_searcher is None:
                    raise ValueError, 'Wait Searcher not set'

                overwrite = self.get_parameter('overwrite')
                if overwrite is None:
                    raise ValueError, 'Overwrite not set'

                # convert to booleans
                if commit == 'True':
                    commit = True
                else:
                    commit = False

                if wait_flush == 'True':
                    wait_flush = True
                else:
                    wait_flush = False

                if wait_searcher == 'True':
                    wait_searcher = True
                else:
                    wait_searcher = False

                if overwrite == 'True':
                    overwrite = True
                else:
                    overwrite = False

                # validate commit within value
                try:
                    commit_within = int(commit_within)
                    if commit_within < 0:
                        raise ValueError
                except:
                    log.warn('Commit Within invalid, using default')
                    commit_within = 0

                # strip trailing slash from path
                if path.endswith('/'):
                    path = path[:-1]

            except Exception as e:
                log.error('Component Failed: %s' % self.__class__.__name__)
                log.error('Reason: %s' % str(e))
                self.yield_ctrl()
                continue # so next time we are called we continue at the top               

            # for each document waiting on our input port
            cnt = 0
            writebuf = []
            for doc in self.receive_all('in'):
                cnt = cnt + 1
                try:
                    # check for a document boost
                    try:
                        boost = float(doc.get_meta('boost'))
                    except:
                        boost = 1

                    writebuf.append('<doc%s>' % ( \
                                ' boost="%s">' % boost if boost > 1 else ''))
                    for key, vals in doc:
                        # see if we need to do a field boost
                        try:
                            fboost = float(doc.get_meta('boost', attr=key))
                        except:
                            fboost = 1
                        
                        for val in vals:
                            escaped = self._escape(val)
                            if val is None:
                                log.warn('Invalid value in field %s' % key)
                                continue
                
                            writebuf.append('\t<field name="%s"%s>' \
                                '<![CDATA[%s]]></field>' % (key, 
                                ' boost="%s"' % fboost if fboost > 1 else '', 
                                escaped))

                    writebuf.append('</doc>')
                                         
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())
                    # decrement the failed document
                    cnt = cnt - 1

            # check if we have a batch of documents to submit to solr
            if cnt > 0:
                batch = '<add%s%s>\n%s\n</add>\n' % ( \
                    ' overwrite="false"' if not overwrite else '',
                    ' commitWithin="%s"' % commit_within if commit_within > 0 \
                    else '', '\n'.join(writebuf))

                conn = None
                try:
                    headers = {'Content-Type': 'text/xml; charset=utf-8'}
                    updatepth = '%s/update' % path
                    conn = httplib.HTTPConnection(host, port)
                    conn.request('POST', updatepth, 
                                                batch.encode('utf-8'), headers)
                    res = conn.getresponse()
                    if res.status != 200:
                        raise ValueError, res.reason
                    
                    commitstr = '<commit%s%s />' % ( \
                        ' waitFlush="false"' if not wait_flush else '',
                        ' waitSearcher="false"' if not wait_searcher else '')

                    if commit:
                        conn.request('POST', updatepth, commitstr, headers)
                        # the following causes a ResponseNotReady exception
                        #res = conn.getresponse()
                        #if res.status != 200:
                        #    raise ValueError, res.reason

                except Exception as e:
                    log.error('Solr batch submission failed')
                    log.error('Reason: %s' % str(e))
                    #log.error(traceback.print_exc())
                finally:
                    if conn is not None:
                        conn.close()

            else:
                log.info('No documents to submit to Solr')                                    
            
            # yield the CPU, allowing another component to run
            self.yield_ctrl()

