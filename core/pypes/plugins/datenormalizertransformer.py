import logging
#import traceback
from datetime import datetime

from pypes.component import Component

log = logging.getLogger(__name__)

class DateNormalizer(Component):
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        
        self.set_parameter('fields', '')
        
        # we can specify multiple input formats that if matched
        # will be normalized to the output format
        self.set_parameter('in_formats', '%m/%d/%Y|%m/%Y|%Y')
        self.set_parameter('out_format', '%Y-%m-%dT%H:%M:%SZ')

        log.info('Component Initialized: %s' % self.__class__.__name__)

    def _parse_date(self, instr, formats):
        result = None
        for format in formats:
            try:
                result = datetime.strptime(instr, format)
            except ValueError:
                # error parsing the string, try the next format
                continue
            except Exception:
                # this is a non-string like object
                # stop trying the other formats
                break
            else:
                # we have a match, stop trying other formats and return
                break

        return result

    def run(self):
        # Define our components entry point
        while True:

            # get parameters outside doc loop for better performace
            try:
                fields = self.get_parameter('fields')
                if fields is None:
                    raise ValueError, 'Input fields not defined'

                formats = self.get_parameter('in_formats')
                if formats is None:
                    raise ValueError, 'Input formats not defined'

                outfmt = self.get_parameter('out_format')
                if outfmt is None:
                    raise ValueError, 'Output format not set'

                # split the fields and formats into a list
                fields = [f.strip() for f in fields.split(',')]
                formats = [f for f in formats.split('|')]

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
                    # loop though each date fields
                    for field in fields:
                        data = doc.get(field)
                        if data is None:
                            log.info('Field %s does not exist' % field)
                            continue

                        if doc.is_multivalued(field):
                            for idx, val in enumerate(data):
                                dt = self._parse_date(val, formats)
                                if dt is None:
                                    log.warn('Unable find date in field %s' \
                                             ' at index %s' % (field, idx))
                                else:
                                    # use replace because we know the index 
                                    doc.replace(field, dt.strftime(outfmt), idx)
                        else:
                            dt = self._parse_date(data, formats)
                            if dt is None:
                                log.warn('Unable to find date in field %s' % \
                                                                field)
                            else: 
                                doc.set(field, dt.strftime(outfmt))
    
                except Exception as e:
                    log.error('Component Failed: %s' % self.__class__.__name__)
                    log.error('Reason: %s' % str(e))                    
                    #log.error(traceback.print_exc())

                # send the document to the next component
                self.send('out', doc)

            # yield the CPU, allowing another component to run
            self.yield_ctrl()

