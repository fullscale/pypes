import os
import os.path
import logging
#import traceback
from xml.etree.ElementTree import _escape_cdata

from pypes.component import Component

log = logging.getLogger(__name__)

class FastXML(Component):
    __metatype__ = 'PUBLISHER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        
        # publishers don't have an output port
        self.remove_output('out')

        self.set_parameter('output_dir', 'fastxml')
        self.set_parameter('on_exist', 'Abort', ['Abort', 'Overwrite', 
                                                            'NextAvaiable'])

        # log successful initialization message
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def _escape(self, vals):
        results = []
        for val in vals:
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

            if result is not None:
                results.append(result)

        return results

    def run(self):
        # Define our components entry point
        batchnum = 0
        while True:

            # get parameters outside doc loop for better performace
            try:
                outdir = self.get_parameter('output_dir')
                if outdir is None:
                    raise ValueError, 'Output directory not set'

                onexist = self.get_parameter('on_exist')
                if onexist is None:
                    raise ValueError, 'On Exist not set'

                # check that the output directory exists and is a directory
                if not os.path.exists(outdir):
                    os.mkdir(outdir)
                else:
                    if not os.path.isdir(outdir):
                        raise ValueError, 'Output directory is not a directory'
       
            except Exception as e:
                log.error('Component Failed: %s' % self.__class__.__name__)
                log.error('Reason: %s' % str(e))
   
                self.yield_ctrl()
                continue # so next time we are called we continue at the top               

            # for each document waiting on our input port
            doccnt = 0
            writebuf = []
            for doc in self.receive_all('in'):
                doccnt = doccnt + 1
                try:
                    writebuf.append('\t<document>')
                    for key, vals in doc:
                        sep = ';'

                        # get a document level separator
                        if doc.has_meta('separator'):
                            sep = doc.get_meta('separator')

                        # get a field level separator that overwrite a
                        # document level separator
                        if doc.has_meta('separator', attr=key):
                            sep = doc.get_meta('separator', attr=key)

                        escaped = sep.join(self._escape(vals))
                        writebuf.append('\t\t<element name="%s">' % key)
                        writebuf.append('\t\t\t<value><![CDATA[%s]]></value>' \
                                                                    % escaped)
                        writebuf.append('\t\t</element>')

                    writebuf.append('\t</document>') 
                                             
                except Exception as e:
                    doccnt = doccnt - 1
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

            # if there are document write them to disk
            if doccnt > 0:
                batch = '<?xml version="1.0" encoding="utf-8"?>\n<documents>' \
                        '\n%s\n</documents>' % '\n'.join(writebuf)

                outfile = None
                try:
                    # try to find an output file
                    batchname = None
                    while True:
                        batchnum = batchnum + 1
                        batchname = os.path.join(outdir, 
                                            'fastxml-batch-%s.xml' % batchnum)

                        if os.path.exists(batchname):
                            if onexist == 'Abort':
                                raise ValueError, '%s exists, abort' % batchname
                            elif onexist == 'Overwrite':
                                log.info('Overwriting %s' % batchname)
                                break
                            else:
                                log.debug('%s exists, trying next' % batchname)
                                continue
                        else:
                            break                    

                    outfile = open(batchname, 'w')
                    outfile.write(batch)
                except Exception as e:
                    log.error('Error writing FastXML batch file')
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())
                finally:
                    if outfile is not None:
                        outfile.close()            
                
            # yield the CPU, allowing another component to run
            self.yield_ctrl()

