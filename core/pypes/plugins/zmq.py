"""Plugins that send messages through zmq"""

import zmq

from pypes.component import Component


class ZmqReply(Component):
    """Note: The call blocks, so a request must be send through zmq,
    otherwise the pipeline hangs!"""

    __metatype__ = 'PUBLISHER'

    def __init__(self, port=40000):
        Component.__init__(self)
        self.set_parameter("port", port)
        self.set_parameter("name", None)

    def run(self):
        port = self.get_parameter("port")
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:{0}".format(port))
        while True:
            for packet in self.receive_all('in'):
                # if requested through the socket, I will send the data
                message = socket.recv_string()
                socket.send_pyobj(packet)
            self.yield_ctrl()


class ZmqPush(Component):
    """Note: The call blocks, so a request must be send through zmq,
    otherwise the pipeline hangs!"""

    __metatype__ = 'PUBLISHER'

    def __init__(self, port=40000):
        Component.__init__(self)
        self.set_parameter("port", port)
        self.set_parameter("name", None)

    def run(self):
        port = self.get_parameter("port")
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        socket.bind("tcp://*:{0}".format(port))
        while True:
            for packet in self.receive_all('in'):
                # if requested through the socket, I will send the data
                socket.send_pyobj(packet)
            self.yield_ctrl()
