"""Provides various basic filters that mimic Unix filters
such as grep, cut, sort, uniq, etc...

Most of these basic filters operate on strings or lines
of strings just as you would expect from the Unix versions.
"""

import stackless

from component import Component

class Null(Component):
    """A Null filter used to silently swallow data similar to /dev/null
    """
    __metatype__ = 'PUBLISHER'

    def __init__(self):
        """Class constructor 
        """
        Component.__init__(self)

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            for data in self.receive_all('in'):
                pass
            self.yield_ctrl()

class TextFileInputReader(Component):
    """Filter used to consume ASCII text files
    """
    __metatype__ = 'ADAPTER'

    def __init__(self):
        """Class constructor 
        """
        Component.__init__(self)

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            for data in self.receive_all('in'):
                fp = open(data, 'rb')
                lines = fp.readlines()
                fp.close()
                for line in lines:
                    self.send('out', line.strip())

            self.yield_ctrl()

class StringInputReader(Component):
    """Filter used to consume strings
    """
    __metatype__ = 'ADAPTER'

    def __init__(self):
        """Class constructor 
        """
        Component.__init__(self)

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            for data in self.receive_all('in'):
                self.send('out', data)
            self.yield_ctrl()

class ConsoleOutputWriter(Component):
    """Filter that emulates Unix stdout
    """
    __metatype__ = 'PUBLISHER'

    def __init__(self):
        """Class constructor 
        """
        Component.__init__(self)
        self.remove_output('out')

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            for data in self.receive_all('in'):
                print data
            
            self.yield_ctrl()

class Grep(Component):
    """Filter that emulates the Unix grep command
    """
    __metatype__ = 'TRANSFORMER'

    def __init__(self, expression):
        """Class constructor 

        @param expression: the expression we want to grep
        @type expression: String
        @todo: Should handle regular expressions
        """
        Component.__init__(self)
        self.expression = expression

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            for data in self.receive_all('in'):
                if self.expression in data:
                    self.send('out', data)
            self.yield_ctrl()

class Sort(Component):
    """Filter that emulates the Unix sort command
    """
    __metatype__ = 'TRANSFORMER'

    def __init__(self, direction='ascending'):
        """Class constructor

        @keyword direction: ascending|descending sort order
        @type direction: String
        """
        Component.__init__(self)

        if direction not in ['ascending', 'descending']:
            direction = 'ascending'

        if direction == 'ascending':
            self.direction = False
        else:
            self.direction = True

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        items = []
        while True:
            for data in self.receive_all('in'):
                items.append(data)

            items.sort(reverse=self.direction)
            for item in items:
                self.send('out', item)
            items = []
            self.yield_ctrl()

class BinarySplit(Component):
    """Filter that forks data into two output paths

    @todo: Rename to fork?
    """
    __metatype__ = 'OPERATOR'

    def __init__(self):
        """Class constructor 
        """
        Component.__init__(self)
        self.add_output('out2', 'duplicates output on this port')

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            for data in self.receive_all('in'):
                self.send('out', data)
                self.send('out2', data)
            
            self.yield_ctrl()

class Uniq(Component):
    """Filter that emulates the Unix uniq command
    """
    __metatype__ = 'TRANSFORMER'

    def __init__(self):
        """Class constructor 
        """
        Component.__init__(self)

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        items = []
        while True:
            for data in self.receive_all('in'):
                items.append(data)
            
            uniq = {}
            count = 0

            for line in items:
                uniq[count] = line
                count += 1

            keys = [uniq[i] for i in range(len(uniq))]

            for item in items:
                self.send('out', item)
            items = []
            self.yield_ctrl()

class Cut(Component):
    """Filter that emulates the Unix cut command
    """
    __metatype__ = 'TRANSFORMER'

    def __init__(self, *fields, **kwargs):
        """Class constructor

        @param fields: the field numbers to be cut
        @param fields: int
        @keyword sep: default separator to use (defaults to 0x20)
        @type sep: String
        """
        Component.__init__(self)
        self.indicies = fields
        try:
            self.sep = kwargs['sep']
        except:
            self.sep = ' '

    def run(self):
        """Entry point for this component. Overrides L{Component.run}
        """
        while True:
            for data in self.receive_all('in'):
                tokens = []
                parts = data.split(self.sep)

                for i in self.indicies:
                    try:
                        tokens.append(parts[i-1])
                    except:
                        pass
                this_string = ' '.join(tokens)

                self.send('out', this_string)
            
            self.yield_ctrl()

