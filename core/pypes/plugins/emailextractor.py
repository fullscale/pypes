import re
import logging
#import traceback

from pypes.component import Component

log = logging.getLogger(__name__)

class Email(Component):
    __metatype__ = 'EXTRACTOR'

    def __init__(self):
        Component.__init__(self)

        # define email regular expression string
        emailre = r'((?:[a-zA-Z0-9_\-\.]+)@(?:(?:\[[0-9]{1,3}\.[0-9]{1,3}\.' \
                  r'[0-9]{1,3}\.)|(?:(?:[a-zA-Z0-9\-]+\.)+))(?:[a-zA-Z]{2,4}' \
                  r'|[0-9]{1,3})(?:\]?))'

        # compile the regular expression
        self._reobj = re.compile(emailre)

        # set component parameters
        self.set_parameter('fields', '')
        self.set_parameter('destination', 'emails')

        log.info('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        while True:

            # get parameters outside doc loop for better performace
            try:
                fields = self.get_parameter('fields')
                if fields is None:
                    raise ValueError, 'Fields not set'

                destination = self.get_parameter('destination')                    
                if destination is None:
                    raise ValueError, 'Destination not set'

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
                    # use sets to avoid duplicates
                    emails = set()
                    for field in fields:
                        data = doc.get(field, '')
                    
                        # search all string objects in a multivalued field
                        if doc.is_multivalued(field):
                            for val in data:
                                if isinstance(val, (str, unicode)):
                                    emails.update(self._reobj.findall(val))
                        else:
                            if isinstance(data, (str, unicode)):
                                emails.update(self._reobj.findall(data))
                
                    # add all emails to destination field
                    if emails:
                        doc.set(destination, list(emails), multi=True)
             
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))
                    #log.error(traceback.print_exc())

                self.send('out', doc)

            self.yield_ctrl()

