import logging
#import traceback

from pypes.component import Component

log = logging.getLogger(__name__)

class RenameField(Component):
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)

        self.set_parameter('original_names', '')
        self.set_parameter('new_names', '')
        self.set_parameter('mode', 'Abort', ['Abort', 'Append', 'Overwrite'])

        # log successful initialization message
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def _rename(self, doc, orig, new, mode):
        ismulti = doc.is_multivalued(orig)
        docmeta, attrmeta = doc.get_metas()

        if not doc.has(new) or mode == 'Overwrite':
            doc.set(new, doc.get(orig), multi=ismulti, keep_meta=False)
            if orig in attrmeta:
                for meta in attrmeta[orig]:
                    doc.set_meta(meta, attrmeta[orig][meta], attr=new)

            doc.delete(orig)
        else:
            if mode == 'Append':
                doc.append(new, doc.get(orig), extend=ismulti)
                if orig in attrmeta:
                    for meta in attrmeta[orig]:
                        try:
                            old = attrmeta[new][meta]
                            doc.set_meta(meta, [old, attrmeta[orig][meta]], 
                                                                    attr=new)
                        except:
                            doc.set_meta(meta, attrmeta[orig][meta], attr=new)

                doc.delete(orig)

            elif mode == 'Abort':
                log.debug('Aborting rename, %s already exists' % new)
                
    def run(self):
        # Define our components entry point
        while True:

            # get parameters outside doc loop for better performace
            try:
                originals = self.get_parameter('original_names')
                if originals is None:
                    raise ValueError, 'No source fields set'

                newnames = self.get_parameter('new_names')
                if newnames is None:
                    raise ValueError, 'No new field names set'

                mode = self.get_parameter('mode')
                if mode is None:
                    raise ValueError, 'No comflict mode defined'

                # split into a list of  field names
                originals = [o.strip() for o in originals.split(',')]
                newnames = [n.strip() for n in newnames.split(',')]

                # make sure the list sizes are the same
                if len(originals) != len(newnames):
                    raise ValueError, 'There must be the same number of ' \
                                    'original fields as there are new fields'
                
            except Exception as e:
                log.error('Component Failed: %s' % self.__class__.__name__)
                log.error('Reason: %s' % str(e))
            
                # optionally send all docs without processing
                for d in self.receive_all('in'):
                    self.send('out', d)
            
                self.yield_ctrl()
                continue # so next time we are called we continue at the top               

            # for each document waiting on our input port
            for doc in self.receive_all('in'):
                try:
                    for orig, new in zip(originals, newnames):
                        if not doc.has(orig):
                            log.debug('%s does not exist, skipping' % orig)
                        elif orig == new:
                            log.debug('%s == %s, skipping' % (orig, new))
                        else:
                            self._rename(doc, orig, new, mode)

                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

                # send the document to the next component
                self.send('out', doc)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

