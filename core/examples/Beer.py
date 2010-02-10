# load the pypes framework
from pkg_resources import require
require('pypes')

import re
import time

from pypes.pipeline import Dataflow
from pypes.component import Component

class Tail(Component):
    __metatype__ = 'ADAPTER'

    def __init__(self, fp):
        Component.__init__(self)
        self.fp = fp

    def run(self):
        self.fp.seek(0,2)
        while True:    
            self.receive('in')
            line = self.fp.readline()
            if line:
                self.send('out', line.strip())
            else:
                self.yield_ctrl()

class Grep(Component):
    __metatype__ = 'TRANSFORMER'

    def __init__(self, pattern):
        Component.__init__(self)
        self.regex = re.compile(pattern)

    def run(self):
        while True:
            for line in self.receive_all('in'):
                if self.regex.match(line):
                    self.send('out', line)
            self.yield_ctrl()

class Printer(Component):
    __metatype__ = 'PUBLISHER'

    def __init__(self):
        Component.__init__(self)

    def run(self):
        while True:
            for data in self.receive_all('in'):
                print data
            self.yield_ctrl()

tail    = Tail(open('/var/log/syslog', 'r'))
grep    = Grep('.*pants.*')
printer = Printer()

pipe = Dataflow({
    tail: {grep:('out','in')}, 
    grep: {printer:('out', 'in')}
})

while True:
    pipe.send(None)
    time.sleep(0.1)
