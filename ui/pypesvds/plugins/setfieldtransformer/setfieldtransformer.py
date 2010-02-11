import logging
#import traceback

from pypes.component import Component

log = logging.getLogger(__name__)

class SetField(Component):
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        
        self.set_parameter('field', '')
        self.set_parameter('values', '')

        # log successful initialization message
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # get parameters outside doc loop for better performace
            try:
                field = self.get_parameter('field')
                if field is None:
                    raise ValueError, 'Field not defined'

                values = self.get_parameter('values')
                if values is None:
                    raise ValueError, 'Values not set'

                # create a list of values
                values = [v for v in values.split(';') if v]

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
                    doc.set(field, values, multi=True)
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

                # send the document to the next component
                self.send('out', doc)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

