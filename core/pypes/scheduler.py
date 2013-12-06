"""Provides scheduling routines for stackless tasklets.

The scheduler itself runs as a tasklet. It blocks waiting
for input on the channel passed in. When new data is sent
on this channel, the scheduler wakes and begins processing
of the data.

"""

import stackless  # pylint: disable=F0401
from pypes.pype import Pype
from pypes.graph import get_pairlist, topsort
import traceback


class ComponentPortError(Exception):
    """Exception raised if input or output port for the
    pypes.component.Component is not found.

    """
    pass


def connect_graph_components(graph):
    """Sort the components and connect the output of a component to the
    input of the next.

    @param graph: The graph representing the work flow
    @type graph: Python dict organized as a graph struct
    @return nodes: The sorted nodes in the graph

    """
    edgeList = get_pairlist(graph)
    nodes = topsort(edgeList)
    pipes = []

    for n in nodes:
        try:
            # get this nodes outputs
            edges = graph[n]
        except:
            pass
        else:
            # for each output
            for e in edges:
                pipe = Pype()
                pipes.append(pipe)
                # does the output port exist?
                if not n.has_port(edges[e][0]):
                    raise ComponentPortError(
                        '''Trying to connect undefined
                           output port {0} {1}'''.format(n, edges[e][0]))
                else:
                    n.connect_output(edges[e][0], pipe)

                # does the input port exist?
                if not e.has_port(edges[e][1]):
                    raise ComponentPortError(
                        '''Trying to connect undefined
                           input port {0} {1}'''.format(e, edges[e][1]))

                e.connect_input(edges[e][1], pipe)
    return nodes, pipes


def sched(ch, graph):
    """Sits in an infinite loop waiting on the channel to receive data.

    The procedure prolog takes care of sorting the
    input graph into a dependency list and initializing
    the filter tasklets used to construct the graph.

    @param graph: The graph representing the work flow
    @type graph: Python dict organized as a graph struct
    @param ch: The stackless channel to listen on
    @type ch: stackless.channel
    @return: nothing
    """
    # Added so that incoming data is fed to every input adapter
    # should check if in exists and create it if it doesn't
    # because a user could remove the input port by accident
    nodes, _ = connect_graph_components(graph)
    tasks = []
    inputEdges = []
    for n in nodes:
        # start this microthread
        tasks.append(stackless.tasklet(n.run)())
        if n.get_type() == 'ADAPTER':
            ie = Pype()
            n.connect_input('in', ie)
            inputEdges.append(ie)

    while True:
        data = ch.receive()
        for ie in inputEdges:
            ie.send(data)
        try:
            tasks[0].run()
        except:
            traceback.print_exc()
