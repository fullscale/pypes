"""
Output from numpy to hdf5 datasets

"""

import logging
import os
import h5py
import numpy as np

import pypes.component
import pypes.packet

log = logging.getLogger(__name__)


class Hdf5Writer(pypes.component.Component):
    """Output an image to HDF5, with all of its metadata.

    mandatory input packet attributes:
    - file_name: path of the destination hdf5 file
    - [any]: if instances of np.ndarray will be saved to the file

    parameters:
    - overwrite: [default: False] overwrite the dataset if it already
    exists in the hdf5 file
    - group: [default: /] h5 Group used to store the datasets

    output:
    - None, writes to disk

    """

    __metatype__ = "PUBLISHER"

    def __init__(self):
        pypes.component.Component.__init__(self)
        # remove the output port since this is a publisher
        self.remove_output('out')
        self.set_parameter("overwrite", False)  # overwrite existing datasets
        self.set_parameter("group", "/")  # group inside the hdf file
        log.debug('Component Initialized: {0}'.format(
            self.__class__.__name__))

    def run(self):
        while True:
            overwrite = self.get_parameter("overwrite")
            packet = self.receive("in")
            try:
                log.debug("%s received %s",
                          self.__class__.__name__,
                          packet)
                file_name = packet.get("file_name")
                log.debug("with path %s", file_name)
                output_file = h5py.File(file_name)
                output_group_name = self.get_parameter("group")
                output_group = output_file.require_group(output_group_name)
                for key in packet.get_attribute_names():
                    value = packet.get(key)
                    log.debug("%s: read attribute %s=%s",
                              self.__class__.__name__,
                              key, value)
                    if not isinstance(value, np.ndarray):
                        log.debug("%s is not a ndarray, skipping",
                                  type(value))
                        continue
                    if key in output_group and overwrite:
                        del output_group[key]
                    elif key in output_group and not overwrite:
                        log.debug("dataset exists, not overwriting")
                        continue
                    output_group[key] = value
                    log.debug("""
                    %s: written dataset %s
                    with shape %s
                    to file %s group %s
                    """,
                              self.__class__.__name__,
                              key,
                              value.shape,
                              file_name,
                              output_group_name)
                output_file.close()
            except:
                log.error('Component Failed: %s',
                          self.__class__.__name__, exc_info=True)
            # yield the CPU, allowing another component to run
            self.yield_ctrl()


class Hdf5ReadGroup(pypes.component.Component):
    """
    Read all datasets in a group

    mandatory input packet attributes:
    - file_name: path of the hdf5 file
    - data: path inside the hdf5 file

    parameters:
    None

    output packet attributes:
    - file_name: the path of the input file
    - data: the list of h5py.Datasets read from the file(s)

    """

    __metatype__ = 'ADAPTER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)

        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:
            # for each file name string waiting on our input port
            for packet in self.receive_all("in"):
                if packet is not None:
                    input_file = False
                    try:
                        log.debug("%s received %s",
                                  self.__class__.__name__,
                                  packet)
                        log.debug("with file name %s and data %s",
                                  packet.get("file_name"),
                                  packet.get("data"))
                        file_name = packet.get("file_name")
                        object_name = packet.get("data")
                        input_file = h5py.File(file_name)
                        input_object = [
                            dataset[...]
                            for dataset in input_file[object_name].values()
                            if isinstance(dataset, h5py.Dataset)]
                        attrs = [
                            dataset.attrs
                            for dataset in input_file[object_name].values()
                            if isinstance(dataset, h5py.Dataset)][0]

                        #add info from first dataset
                        for key, value in attrs.items():
                            packet.set(key, value)
                        log.debug("%s found %d datasets",
                                  self.__class__.__name__,
                                  len(input_object))
                        packet.set("data", input_object)
                    except:
                        log.error('%s failed while reading %s',
                                  self.__class__.__name__,
                                  file_name, exc_info=True)
                    finally:
                        if input_file:
                            input_file.close()
                        # send the packet to the next component
                self.send('out', packet)
            # yield the CPU, allowing another component to run
            self.yield_ctrl()


class Hdf5ReadDataset(pypes.component.Component):
    """
    Read a dataset
    The files are stored in self.files so that they are not prematurely
    garbage collected.

    mandatory input packet attributes:
    - file_name: path of the hdf5 file
    - data: path inside the hdf5 file

    parameters:
    None

    output packet attributes:
    - file_names: the list of the paths of the input files
    - data: the list of h5py.Datasets read from the file(s)

    """

    __metatype__ = 'ADAPTER'

    def __init__(self):
        # initialize parent class
        pypes.component.Component.__init__(self)

        #store files so that they are not garbage collected
        self.files = []

        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:
            # for each file name string waiting on our input port
            for packet in self.receive_all("in"):
                log.debug("%s received %s %s",
                          self.__class__.__name__,
                          packet.get("file_name"),
                          packet.get("data"))
                try:
                    file_name = packet.get("file_name")
                    object_name = packet.get("data")
                    input_file = h5py.File(file_name)
                    input_object = input_file[object_name]
                    self.files.append(input_file)
                    packet.set("data", input_object)
                except:
                    log.error('%s failed while reading %s',
                              self.__class__.__name__,
                              file_name, exc_info=True)
                # send the packet to the next component
                self.send('out', packet)
            # yield the CPU, allowing another component to run
            self.yield_ctrl()

    def __del__(self):
        """close files when the reference count is 0."""
        for f in self.files:
            log.debug('{0} closing file {1}'.format(
                self.__class__.__name__, f.filename))
            if f:
                f.close()
            else:
                log.debug('{0} file {1} was already closed'.format(
                    self.__class__.__name__, f.filename))


def output_name(files):
    """
    Get the name of the output hdf5 file from a list of input files.

    """
    first_file_name, _ = os.path.splitext(os.path.basename(files[0]))
    last_file_name = os.path.splitext(os.path.basename(files[-1]))[0]
    dir_name = os.path.dirname(files[0])
    if len(files) > 1:
        file_name = os.path.join(
            dir_name, "{0}_{1}.hdf5".format(
                first_file_name, last_file_name))
    else:
        file_name = os.path.join(
            dir_name, "{0}.hdf5".format(first_file_name))
    return file_name
