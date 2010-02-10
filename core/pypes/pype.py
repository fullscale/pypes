"""Provides the buffer that connects two filters.

This class serves as the edges of the graph. Nodes
attached to either end send and recieve data through
a pype instance.

Each pair of nodes is connected by their own unique
pype object.
"""

class Pype(object):
    """A bidirectional buffer used to allow two nodes to pass data back and forth.
    @todo: Should this be a L{multiprocessor.pipe}?
    """
    def __init__(self):
        """Class constructor
        """
        self.buffer = []

    def get_buffer_size(self):
        """Returns the current buffer size of this pype
        """
        return len(self.buffer)

    size = property(get_buffer_size)

    def send(self, data):
        """Writes data to this pype

        @return: Nothing
        """
        self.buffer.append(data)

    def recv(self):
        """Reads data from this pype

        @return: data or None if no data is available
        """
        try:
            data = self.buffer.pop(0)
        except:
            data = None
        return data

