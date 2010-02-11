import json
import urllib2
import logging
#import traceback

from pypes.component import Component

log = logging.getLogger(__name__)

class GeoCode(Component):
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        
        # the field that contains the address information
        # most likely from the AddressExtractor
        self.set_parameter('address_field', 'addresses')

        # log successful initialization message
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:

            # get parameters outside doc loop for better performace
            try:
                addrfield = self.get_parameter('address_field')
                if addrfield is None:
                    raise ValueError, 'Address field not defined'

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
                    # check that the address field actually exists
                    if not doc.has(addrfield):
                        log.debug('Address field does not exist')
      
                    # check that the address contains zip codes
                    elif not doc.has_meta('zipcodes', attr=addrfield):
                        log.debug('No zipcodes found in address')
    
                    else:
                        # gather the geo information for each zipcode
                        zipcodes = doc.get_meta('zipcodes', addrfield, [])
                        cities, states, coordinates = set(), set(), set()
                        for zipcode in zipcodes:
                            response = None
                            try:
                                response = urllib2.urlopen( \
                                    'http://ws.geonames.org/postalCodeLookup' \
                                    'JSON?postalcode=%s&country=US&maxRows=1' \
                                                        % zipcode, timeout=2)

                                # the above service returns JSON
                                result = response.read()
                            except:
                                log.debug('Error getting GeoCode info for %s' \
                                                                    % zipcode)
                            else:
                                # payload is mapped to 'postalcodes' and we're 
                                # only asking for the first result
                                try:
                                    data = json.loads(result)['postalcodes'][0]
                                except (KeyError, IndexError):
                                    log.debug('No GeoCode information for %s' \
                                                                    % zipcode)
                                else:
                                    # try and grab some data from the response
                                    city = data.get('placeName', None)
                                    if city is not None:
                                        cities.add(city)

                                    state = data.get('adminCode1', None)
                                    if state is not None:
                                        states.add(state)

                                    # only save coords if we have lat and lon
                                    lat = data.get('lat', None)
                                    lon = data.get('lng', None)
                                    if (lat or lon) is not None:
                                        coordinates.add((lat, lon))

                                finally:
                                    response.close()

                        # save the GeoCode information to the document
                        if cities:
                            doc.set('cities', [c for c in cities], multi=True)
                    
                        if states:
                            doc.set('states', [s for s in states], multi=True)

                        if coordinates:
                            doc.set('coordinates', [c for c in coordinates], 
                                                                    multi=True)
                    
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

                # send the document to the next component
                self.send('out', doc)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

