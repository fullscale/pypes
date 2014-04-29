"""Test the composition of components.

"""



import pypes.component


class Doubler(pypes.component.Component):

    """Doubles any input"""
    __metatype__ = "TRANSFORMER"

    def __init__(self):
        pypes.component.Component.__init__(self)

    def run(self):
        while True:
            packet = self.receive("in")
            print("called doubler with packet", packet)
            self.send("out", 2 * packet)
            self.yield_ctrl()


class Printer(pypes.component.Component):
    """Print with the print function."""
    __metatype__ = 'PUBLISHER'

    def __init__(self):
        pypes.component.Component.__init__(self)

    def run(self):
        while True:
            for data in self.receive_all('in'):
                print(data)
            self.yield_ctrl()


def quadrupler_network_factory():
    """make a network that doubles twice
    :returns: a dictionary with the graph of two connected doublers

    """
    doubler1 = Doubler()
    doubler2 = Doubler()
    graph = {
        doubler1: {
            doubler2: ("out", "in")
        },
    }
    return graph


if __name__ == '__main__':
    quadrupler = pypes.component.HigherOrderComponent(
        quadrupler_network_factory())
    quadrupler.__metatype__ = "ADAPTER"
    printer = Printer()
    doubler = Doubler()
    doubler.__metatype__ = "ADAPTER"

    network = {
        quadrupler: {
            printer: ("out", "in"),
        },
    }
    #network = {
        #doubler: {
            #printer: ("out", "in"),
        #},
    #}

    from pypes.pipeline import Dataflow
    pipeline = Dataflow(network)
    for number in range(1, 5):
        pipeline.send(number)
    pipeline.close()
