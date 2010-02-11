import csv
import codecs
import logging
#import traceback
import cStringIO

from pypes.component import Component

log = logging.getLogger(__name__)

class CSVWriter(Component):
    __metatype__ = 'PUBLISHER'

    def __init__(self):
        # initialize parent class
        Component.__init__(self)
        
        # this is a publisher so there is no output
        self.remove_output('out')
        
        self.set_parameter('outfile', 'pypescsvoutput.csv')
        self.set_parameter('fields', '_originals_')

        # used to join multivaled fields
        self.set_parameter('multi_separator', ';')

        # log successful initialization message
        log.info('Component Initialized: %s' % self.__class__.__name__)

    def _join(self, data, sep=None):
        result = u''    
        if sep is None:
            if isinstance(data, (str, unicode)):
                result = data.decode('utf-8', 'ignore')
            else:
                # if we don't have a string object, see if it has a str method
                try:
                    result = data.__str__().decode('utf-8', 'ignore')
                except:
                    pass
        else:
            # we have a sequence type, try to convert each peice to a string
            parts = []
            for part in data:
                if isinstance(part, (str, unicode)):
                    parts.append(part.decode('utf-8', 'ignore'))
                else:
                    # not a string object, see if it has a str method
                    try:
                        parts.append(part.__str__().decode('utf-8', 'ignore'))
                    except:
                        parts.append(u'')

            # join the parts, we don't need to worry about the sep being
            # a unicode string since python will take care of that for us
            result = sep.join(parts)

        return result            

    def run(self):
        # define our components entry point
        while True:

            # get parameters outside doc loop for better performace
            csvout = None
            try:
                outfile = self.get_parameter('outfile')
                if outfile is None:
                    raise ValueError, 'Outfile is not set'
                
                fields = self.get_parameter('fields')
                if fields is None:
                    raise ValueError, 'Fields is not set'

                sep = self.get_parameter('multi_separator')
                if sep is None:
                    raise ValueError, 'Multivalue separator not set'

                # convert to a list of field names
                if fields not in ('_all_', '_originals_'):
                    fields = [f.strip() for f in fields.split(',')]

                # open the file for writing
                csvout = open(outfile, 'w')
                csvwriter = UnicodeCSVWriter(csvout, dialect='excel')

            except Exception as e:
                log.error('Component Failed: %s' % self.__class__.__name__)
                log.error('Reason: %s' % str(e))

            else:     
                # for each document waiting on our input port
                for doc in self.receive_all('in'):
                    try:
                        row = []

                        # if we are using a macro to define the fields
                        # loop though all the fields and save the ones
                        # related to each macro.
                        if fields in ('_all_', '_originals_'):
                            newfields = []
                            for key in doc.get_attribute_names():
                                # original csv fields start with column
                                # if this is the original macro and the
                                # current fields doesn't start with that
                                # then we can move on to the next field
                                if fields == '_originals_' and not \
                                                    key.startswith('column'):
                                    continue
                
                                newfields.append(key)
                            
                            # update fields variable to use the matched fields
                            fields = newfields
                    
                        # loop though each field and write it to the csv
                        for key in fields:
                            value = doc.get(key)
                            if value is not None:
                                if doc.is_multivalued(key):
                                    # if we have a multivalued field we
                                    # want to make sure we use the multivalue
                                    # separator
                                    colval = self._join(value, sep=sep)
                                else:
                                    colval = self._join(value)

                                row.append(colval)
                            else:
                                # add empty unicode string
                                row.append(u'')

                        # if our row has a value, write it to the csv
                        if row:       
                            csvwriter.write_row(row)

                    except Exception as e:
                        log.error('Component Failed: %s' % self.__class__.__name__)
                        log.error('Reason: %s' % str(e))                    
                        #log.error(traceback.print_exc())

            finally:
                # close the csvfile if it is open
                if csvout is not None:
                    csvout.close()
 
                # yield the CPU, allowing another component to run
                self.yield_ctrl()

class UnicodeCSVWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding='utf-8', **kwds):
        # redirect output to a queue
        self._queue = cStringIO.StringIO()
        self._writer = csv.writer(self._queue, dialect=dialect, **kwds)
        self._stream = f
        self._encoder = codecs.getincrementalencoder(encoding)()

    def write_row(self, row):
        # write the row to the queue
        self._writer.writerow([s.encode('utf-8') for s in row])

        # fetch utf-8 output from the queue
        data = self._queue.getvalue()
        data = data.decode('utf-8')

        # re-encode it to the target encoding
        data = self._encoder.encode(data)

        # write to the target stream and empty the queue
        self._stream.write(data)
        self._queue.truncate(0)

    def write_rows(self, rows):
        for row in rows:
            self.write_row(row)
