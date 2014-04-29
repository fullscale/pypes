"""Plugins that send messages through zmq"""

import zmq
import h5py
import numpy as np
import logging

from pypes.component import Component

log = logging.getLogger(__name__)


def send_array(socket, A, flags=0, copy=True, track=False):
    """send a numpy array with metadata"""
    md = dict(
        dtype=str(A.dtype),
        shape=A.shape,
    )
    socket.send_json(md, flags | zmq.SNDMORE)
    return socket.send(A, flags, copy=copy, track=track)


def recv_array(socket, flags=0, copy=True, track=False):
    """recv a numpy array"""
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    A = np.frombuffer(msg, dtype=md['dtype'])
    return A.reshape(md['shape'])


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
        while True:
            port = self.get_parameter("port")
            context = zmq.Context()
            socket = context.socket(zmq.PUSH)
            socket.bind("tcp://*:{0}".format(port))
            for packet in self.receive_all('in'):
                # if requested through the socket, I will send the data
                data = packet.get("data")
                if isinstance(data, h5py.Dataset):
                    log.debug("%s sending h5py object %s",
                              self.__class__.__name__, data.shape)
                    send_array(socket, data[...])
                elif isinstance(data, np.ndarray):
                    log.debug("%s sending np.ndarray %s",
                              self.__class__.__name__, data.shape)
                    send_array(socket, data)
                else:
                    log.debug("%s sending json %s",
                              self.__class__.__name__,
                              type(data))
                    socket.send_json(data)
            socket.close()
            self.yield_ctrl()
