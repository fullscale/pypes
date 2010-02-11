import logging
#import traceback

from pypes.component import Component

log = logging.getLogger(__name__)

class DeleteField(Component):
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        
        #Setup any user parameters required by this component 
        self.set_parameter('fields', '')

        # log successful initialization message
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # get parameters outside doc loop for better performace
            try:
                fields = self.get_parameter('fields')
                if fields is None:
                    raise ValueError, 'No input fields set'

                # convert to a list of field names
                fields = [f.strip() for f in fields.split(',')]

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
                    # loop though the list of fields and try to delete them
                    for field in fields:
                        if not doc.delete(field):
                            log.debug('Failed to delete field %s' % field)

                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

                # send the document to the next component
                self.send('out', doc)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

