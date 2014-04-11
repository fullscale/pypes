"""
Output from numpy to hdf5 datasets

"""

import logging
import os
import h5py

import pypes.component
import pypes.packet

log = logging.getLogger(__name__)


class Hdf5Writer(pypes.component.Component):
    """Output an image to HDF5, with all of its metadata.

    mandatory input packet attributes:
    - full_path: path of the original raw file, used to calculate the
    hdf5 path and the name of the dataset
    - data: containing the image as a numpy array

    optional input packet attributes:
    - any: will be added as attributes for the hdf5 Dataset

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
                file_name = packet.get("full_path")
                log.debug("with path %s", file_name)
                folder_name, tail_name = os.path.split(file_name)
                output_file_name = folder_name + ".hdf5"
                output_file = h5py.File(output_file_name)
                output_group = output_file.require_group(
                    self.get_parameter("group"))
                dataset_name = os.path.splitext(tail_name)[0]
                if dataset_name in output_group and overwrite:
                    del output_group[dataset_name]
                elif dataset_name in output_group and not overwrite:
                    log.debug(
                        "{0}: dataset {1} exists, not overwriting".format(
                            self.__class__.__name__, dataset_name))
                    output_file.close()
                    self.yield_ctrl()
                    continue
                output_group[dataset_name] = packet.get("data")
                packet.delete("data")
                log.debug("%s: written dataset %s to file %s group %s",
                          self.__class__.__name__,
                          dataset_name,
                          output_file_name,
                          self.get_parameter("group"))
                for key in packet.get_attribute_names():
                    value = packet.get(key)
                    log.debug("%s: adding attribute to dataset %s: %s=%s",
                              self.__class__.__name__,
                              dataset_name,
                              key, value)
                    output_group[dataset_name].attrs[key] = value
                if output_file:
                    output_file.close()
            except:
                log.error('Component Failed: %s',
                          self.__class__.__name__, exc_info=True)
            # yield the CPU, allowing another component to run
            self.yield_ctrl()


class Hdf5ReadGroup(pypes.component.Component):
    """
    Read all datasets in a group
    The files are stored in self.files so that they are not prematurely
    garbage collected.

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

        #store files so that they are not garbage collected
        self.files = []

        # log successful initialization message
        log.debug('Component Initialized: %s', self.__class__.__name__)

    def run(self):
        # Define our components entry point
        while True:
            # for each file name string waiting on our input port
            packet = self.receive("in")
            if packet is not None:
                log.debug("%s received %s",
                          self.__class__.__name__,
                          packet)
                log.debug("with file name %s and data %s",
                          packet.get("file_name"),
                          packet.get("data"))
                file_name = packet.get("file_name")
                object_name = packet.get("data")
                try:
                    input_file = h5py.File(file_name)
                    input_object = [
                        dataset
                        for dataset in input_file[object_name].values()
                        if isinstance(dataset, h5py.Dataset)]
                    log.debug("%s found %d datasets",
                              self.__class__.__name__,
                              len(input_object))
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
            packet = self.receive("in")
            log.debug("%s received %s %s",
                      self.__class__.__name__,
                      packet.get("file_name"),
                      packet.get("data"))
            file_name = packet.get("file_name")
            object_name = packet.get("data")
            try:
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


def output_name(files, component_name):
    """
    Get the name of the output hdf5 file from a list of input files.

    """
    first_file_name, _ = os.path.splitext(os.path.basename(files[0]))
    last_file_name = os.path.splitext(os.path.basename(files[-1]))[0]
    dir_name = os.path.dirname(files[0])
    if len(files) > 1:
        output_file_name = os.path.join(
            dir_name, "{0}_{1}/{2}".format(
                first_file_name, last_file_name, component_name))
    else:
        output_file_name = os.path.join(
            dir_name, "{0}/{1}".format(first_file_name, component_name))
    return output_file_name
