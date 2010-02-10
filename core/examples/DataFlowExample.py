# load the pypes framework
from pkg_resources import require
require('pypes')

# import the Dataflow module
from pypes.pipeline import Dataflow
# import some built-in filters provided by the framework (for testing)
from pypes.filters import TextFileInputReader, BinarySplit, Sort, \
                                        Grep, ConsoleOutputWriter, Cut, Uniq

reader   = TextFileInputReader() # reads ASCII text files line by line
splitter = BinarySplit()         # splits the data into 2 branches
sorter   = Sort('descending')    # sorts in descending order 
grepper1 = Grep('POST')          # grep any lines containing 'POST'
grepper2 = Grep('GET')           # grep any lines containing 'GET'
cutter   = Cut(4,5,6, sep=' ')   # cut fields 4, 5, and 6 using space as separator
uniq     = Uniq()                # outputs only unique lines
printer1 = ConsoleOutputWriter() # writes to console (STDOUT)
printer2 = ConsoleOutputWriter() # writes to console (STDOUT)

"""
The "network" depicted graphically.
                                  __________       __________
                                 |          |     |          |
                                /| grepper1 |-----| printer1 |
                               / |__________|     |__________|
 __________       __________  /
|          |     |          |/
|  reader  |-----| splitter |
|__________|     |__________|\
                              \   __________       __________       __________       __________       __________
                               \ |          |     |          |     |          |     |          |     |          |
                                \| grepper2 |-----|  sorter  |-----|  cutter  |-----|   uniq   |-----| printer2 |
                                 |__________|     |__________|     |__________|     |__________|     |__________|


"""

# The "network" defined formally as a dataflow graph
Network = {
      reader: {splitter:('out','in')},
    splitter: {grepper1:('out','in'), grepper2:('out2','in')},
    grepper1: {printer1:('out','in')},
    grepper2: {  sorter:('out','in')},
      sorter: {  cutter:('out','in')}, 
      cutter: {    uniq:('out','in')},
        uniq: {printer2:('out','in')}
}

# run our example
if __name__ == '__main__':
    # create a new data flow
    p = Dataflow(Network)
    # send a document through the data flow
    p.send('cups.log')
    # shut down the data flow
    p.close()   
 
