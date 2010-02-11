import logging
#import traceback

from pypes.component import Component

log = logging.getLogger(__name__)

class CaseNormalizer(Component):
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        Component.__init__(self)
        self.set_parameter('fields', '')
        self.set_parameter('operation', 'lowercase', 
                                ['lowercase', 'UPPERCASE', 'TitleCase'])
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def _normalize(self, val, op):
        result = val
        try:        
            if op == 'lowercase':
                result = val.lower()
            elif op == 'UPPERCASE':
                result = val.upper()
            elif op == 'TitleCase':
                result = val.title()
            else:
                # should never get here
                log.warn('Undefined operation: %s' % op)
        except AttributeError:
            #log.info('Non-string object found, skipping')
            pass

        return result

    def run(self):
        while True:

            # get parameters outside doc loop for better performace
            try:
                # get defined operation
                op = self.get_parameter('operation')
                if op is None:
                    raise ValueError, 'Operation not set'

                # get the fields to perform normalization on
                fields = self.get_parameter('fields')
                if fields is None:
                    raise ValueError, 'Fields not set'

                # convert to a list of field names
                fields = [f.strip() for f in fields.split(',')]

            except Exception as e:
                log.error('Component Failed: %s' % self.__class__.__name__)
                log.error('Reason: %s' % str(e))

                # send all docs without processing
                for d in self.receive_all('in'):
                    self.send('out', d)

                self.yield_ctrl()
                continue # so next time we are called we continue at the top

            # loop though each document on input port
            for doc in self.receive_all('in'):
                try:
                    # perform normalization on each field
                    for field in fields:
                        fieldval = doc.get(field)
                        if fieldval is not None:
                            # if it is multivalued, then perform
                            # normalization on each value                        
                            if doc.is_multivalued(field):
                                doc.set(field, [self._normalize(x, op) \
                                                for x in fieldval], multi=True)
                            else:
                                doc.set(field, self._normalize(fieldval, op))
                        else:
                            log.info('Field %s not set, skipping' % field)

                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))
                    #log.error(traceback.print_exc())

                self.send('out', doc)
            
            self.yield_ctrl()

