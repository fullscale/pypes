import re
import logging
#import traceback

from pypes.component import Component

log = logging.getLogger(__name__)

class Address(Component):
    __metatype__ = 'EXTRACTOR'

    def __init__(self):
        Component.__init__(self)

        # break up regular expression parts so it is easier to read
        cityre = r'(\b(?:[A-Z]+[a-z]+\s*)+\s*\b)+'
        statere = r'(A[LKSZR]|C[AOT]|D[EC]|F[ML]|G[AU]|HI|I[DLNA]|K[SY]|LA|' \
                  r'M[EHDAINSOTP]|N[EVHJMYCD]|O[HKR]|P[WAR]|RI|S[CD]|T[NX]|' \
                  r'UT|V[TIA]|W[AVIY])'
        zipre = r'([0-9]{5}(?:[- /]?[0-9]{4})?)'
        
        # build regular expression to match address using parts above
        # city + optional space(s) + comma + one or more spaces + 
        # state + optional (one or more spaces + zip)
        self._reobj = re.compile(r'%s\s*[,]\s+%s(?:\s+%s)?' % \
                                    (cityre, statere, zipre))

        # set component parameters
        self.set_parameter('fields', '')
        self.set_parameter('destination', 'addresses')

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
                    addrs, cities, states, zips = set(), set(), set(), set()
                    for field in fields:
                        data = doc.get(field, '')
                    
                        # search all string object in a multivalued field
                        matches = []
                        if doc.is_multivalued(field):
                            for val in data:
                                if isinstance(val, (str, unicode)):
                                    matches.extend(self._reobj.findall(val))
                        else:
                            if isinstance(data, (str, unicode)):
                                matches.extend(self._reobj.findall(data))

                        # loop though each match and save it
                        for match in matches:
                            city, state, zipcode = match
                            cities.add(city)
                            states.add(state)

                            # check if zipcode is empty or not                                                                
                            if not zipcode:                                
                                address = '%s, %s' % (city, state)
                            else:
                                address = '%s, %s %s' % (city, state, zipcode)
                                zips.add(zipcode)
                                
                            addrs.add(address)    
                            log.debug('Match Found: %s' % address)
                
                    # add all addresses to destination field
                    if addrs:
                        doc.set(destination, list(addrs), multi=True)
                        doc.set_meta('cities', list(cities), destination)
                        doc.set_meta('states', list(states), destination)
                        doc.set_meta('zipcodes', list(zips), destination)
             
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))
                    #log.error(traceback.print_exc())

                self.send('out', doc)

            self.yield_ctrl()

