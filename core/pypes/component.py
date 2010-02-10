"""Provides a common component interface.

Filters should subclass this module and impliment 
the run() method.

"""

import stackless

class Component(object):
    """Provides methods common to all filters.

    Anyone building a custom filter object should
    subclass this module and implement their own
    run() method.

    Keep in mind that filters are stackless.tasklets
    and the run method should yield rather return.
    """
    __metatype__ = None

    def __init__(self):
        """Class constructor

        Provides default input of 'in' and output of 'out'.
        """
        self._inputs  = {'in' : [None, 'Default input port'] }
        self._outputs = {'out': [None, 'Default output port']}
        self._parameters = {}

    def run(self):
        """Starts this component as a stackless tasklet

        This method is meant to be overridden in derived subclass.
        The subclass should implement its own logic.
        """
        raise NotImplementedError

    def yield_ctrl(self):
        """Causes this tasklet to relinquish control of the 
        CPU to allow another tasklet to run. This tasklet is
        re-scheduled to run again.

        @return: Nothing
        """
        stackless.schedule()

    def add_input(self, name, desc=None):
        """Adds a new input port to this component.

        This is most typically called from the object
        subclassing this component. Adding a new port means 
        you are adding some filter logic that utilizes 
        the new port in some way.

        @param name: The string used to represent this port
        @type name: String
        
        @keyword desc: An optional description of what this port is used for.
        @note: Although desc is optional, it is considered good practice 
               to provide a brief description.

        @return: Nothing
        """
        status = False
        if not self._inputs.has_key(name):
            self._inputs[name] = [None, desc]
            status = True
        return status
    
    def remove_input(self, name):
        """Removes the given port from this components list of available input ports.

        @param name: The string used to represent this port
        @type name: String

        @return: Nothing
        """
        status = False
        if self._inputs.has_key(name):
            self._inputs.pop(name)
            status = True
        return status

    def add_output(self, name, desc=None):
        """Adds a new output port to this component.

        This is most typically called from the object
        subclassing this component. Adding a new port means 
        you are adding some filter logic that utilizes 
        the new port in some way.

        @param name: The string used to represent this port
        @type name: String
        
        @keyword desc: An optional description of what this port is used for.
        @note: Although desc is optional, it is considered good practice 
               to provide a brief description.

        @return: Nothing
        """
        status = False
        if not self._outputs.has_key(name):
            self._outputs[name] = [None, desc]
            status = True
        return status
    
    def remove_output(self, name):
        """Removes the given port from this components list of available output ports.

        @param name: The string used to represent this port
        @type name: String

        @return: Nothing
        """
        status = False
        if self._outputs.has_key(name):
            self._outputs.pop(name)
            status = True
        return status

    def connect_input(self, name, edge):
        """Connects a edge (pype) to the specified input port of this component.

        This only represents half of an actual connection between two nodes.
        Typically, one side of the edge is connected to the output of one
        node while the other side is connected to the input of another node.

        @see: L{connect_output}

        @param name: The string used to represent this port
        @type name: String
        
        @param edge: The edge you would like to connect
        @type edge: L{Pype}

        @return: Nothing
        @todo: Need to raise custom excpetion when trying to connect
               a non-existant port.
        """
        try:
            item = self._inputs[name]
        except:
            print 'Input does not exist'
        else:
            item[0] = edge
            self._inputs[name] = item

    def connect_output(self, name, edge):
        """Connects a edge (pype) to the specified output port of this component.

        This only represents half of an actual connection between two nodes.
        Typically, one side of the edge is connected to the output of one
        node while the other side is connected to the input of another node.

        @see: L{connect_input}

        @param name: The string used to represent this port
        @type name: String
        
        @param edge: The edge you would like to connect
        @type edge: L{Pype}

        @return: Nothing
        @todo: Need to raise custom exception when trying to connect
               a non-existant port.
        """
        try:
            item = self._outputs[name]
        except:
            print 'Output does not exist'
        else:
            item[0] = edge
            self._outputs[name] = item

    def is_connected(self, name):
        """Returns True is the specified port is connected to an edge.

        @param name: The port being referenced
        @type name: String
        @return: Boolean
        """
        status = False
        in_connected = False
        out_connected = False

        if self._inputs.has_key(name):
            in_connected = self._inputs[name][0]

        if self._outputs.has_key(name):
            out_connected = self._outputs[name][0]

        connected = in_connected or out_connected

        if connected:
            status = True

        return status

    def get_port_description(self, port):
        """Returns the ports description.

        @param port: The port being referenced
        @type port: String
        @return: String
        @todo: Need to raise custom exception when trying to query
               a non-existant port.
        """
        desc = None

        if self.has_port(port):
            try:
                desc = self._inputs[port][1]
            except:
                desc = self._outputs[port][1]

        return desc

    def set_port_description(self, port, desc):
        """Sets the ports description.

        @param port: The port being referenced
        @type port: String
        @return: Nothing
        @todo: Need to raise custom exception when trying to query
               a non-existant port.
        """
        if self.has_port(port):
            try:
                item = self._inputs[port]
                item[1] = desc
                self._inputs[port] = item
            except:
                item = self._outputs[port]
                item[1] = desc
                self._outputs[port] = item
            

    def has_port(self, port):
        """Returns True if the component contains this port, False otherwise.

        @param port: The port being referenced
        @type port: String
        @return: Boolean
        """
        return self._inputs.has_key(port) or self._outputs.has_key(port)

    def receive(self, port):
        """Tries recieving data on the specified port.

        @param port: The port being referenced
        @type port: String
        @return: Incoming data or None if no data is available
        @todo: Nothing
        """
        try:
            data = self._inputs[port][0].recv()
        except:
            data = None
        return data

    def receive_all(self, port):
        """Tries recieving all data waiting on the specified port.

        @param port: The port being referenced
        @type port: String
        @return: An iterator over this ports available data
        """
        for item in range(self._inputs[port][0].size):
            yield self._inputs[port][0].recv()
    
    def send(self, port, data):
        """Sends data on specified port.

        @param port: The port being referenced
        @type port: String

        @param data: Data to be sent
        @type data: Application specific

        @return: Boolean (depending on the success)
        """
        status = True
        try:
            self._outputs[port][0].send(data)
        except:
            status = False
        return status

    def get_in_ports(self):
        """Returns a list of current inputs ports for this component.
        """
        return self._inputs.keys()

    def get_out_ports(self):
        """Returns a list of current output ports for this component.
        """
        return self._outputs.keys()

    def get_parameters(self):
        """Returns a dict of parameters used by this component.
        """
        return self._parameters

    def set_parameters(self, parameters):
        """Sets parameters for this component.

        @param parameters: The parameters being set on this component
        @type parameters: dict
        """
        self._paramaters = parameters

    def get_parameter(self, name):
        """Returns a specific parameter for this component.

        @param name: The name of the parameter you want
        @type name: String
        @return: String
        """
        try:
            p = self._parameters[name][0]
        except:
            p = None
        return p

    def set_parameter(self, name, parameter, options=None):
        """Sets a specific parameter for this component.

        @param name: The name of teh parameter being set
        @type name: String
        @param parameter: The value being set for this parameter
        @type parameter: String
        """
        if options is None and self._parameters.has_key(name):
            pset = self._parameters[name][0] = parameter
        else:
            if options is None or not isinstance(options, list):
                options = []
            try:
                self._parameters[name] = [parameter, options]
            except:
                pass

    def get_type(self):
        return self.__metatype__
