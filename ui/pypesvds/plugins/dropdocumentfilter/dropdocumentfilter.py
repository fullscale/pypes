import logging
#import traceback

from pypes.component import Component

log = logging.getLogger(__name__)

class DropDocument(Component):
    __metatype__ = 'FILTER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        
        self.set_parameter('fields', '')
        self.set_parameter('dropvalues', '_any_') 

        # log successful initialization message
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def _check(self, val, dropvals):
        drop = False    
        if isinstance(val, (str, unicode)):
            if val.strip() in dropvals:
                drop = True
        else:
            try:
                # this is a non string object, try to convert to string
                val = val.__str__()
                if val in dropvals:
                    drop = True
            except:
                pass

        return drop

    def run(self):
        # Define our components entry point
        while True:

            # get parameters outside doc loop for better performace
            try:
                fields = self.get_parameter('fields')
                if fields is None:
                    raise ValueError, 'No input fields set'

                dropvals = self.get_parameter('dropvalues')
                if dropvals is None:
                    raise ValueError, 'No drop values defined'

                # split into a list of fields
                fields = [f.strip() for f in fields.split(',')]

                # split into a list of drop values
                if dropvals != '_any_':
                    dropvals = [v.strip() for v in dropvals.split(';')]

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
                drop = False                
                try:
                    for field in fields:
                        if dropvals == '_any_' and doc.has(field):
                            drop = True
                            break
                        else:
                            data = doc.get(field)
                            if data is not None:
                                if doc.is_multivalued(field):
                                    # if this is multivalued check each value
                                    for val in data:
                                        if self._check(val, dropvals):
                                            drop = True
                                            break    

                                    # break out of loop early drop is True
                                    if drop:
                                        break
                                else:
                                    if self._check(data, dropvals):
                                        drop = True
                                        break
                
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

                # send the document to the next component
                if not drop:
                    self.send('out', doc)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

