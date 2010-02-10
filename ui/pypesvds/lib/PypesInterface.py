from pypes.pipeline import Dataflow
import pkg_resources
import logging
import os
import json
import traceback
from pylons import config

log = logging.getLogger(__name__)

ENTRYPOINT = 'pypesvds.plugins'
PLUGIN_DIR = os.path.join(os.path.dirname(__file__), '../plugins')

def init_plugins():
    log.info('Initializing Studio Plugins from %s' % config['plugin_dir'])
    try:
        if not os.path.exists(config['plugin_dir']):
            os.mkdir(config['plugin_dir'])
    except:
        log.info('Unable to create plugins directory: %s' % config['plugin_dir'])
    eggs, errors = pkg_resources.working_set.find_plugins(pkg_resources.Environment([PLUGIN_DIR, config['plugin_dir']]))
    map(pkg_resources.working_set.add, eggs)
    plugins = {}
    for egg in eggs:
        egg.activate()
        for name in egg.get_entry_map(ENTRYPOINT):
            entry_point = egg.get_entry_info(ENTRYPOINT, name)
            cls = entry_point.load()
            if not hasattr(cls, '__metatype__'):
                cls.__metatype__ = ''
            if cls.__metatype__ in plugins:
                d = plugins[cls.__metatype__]
                d[cls.__name__] = cls
                plugins[cls.__metatype__] = d
            else:
                d = {}
                d[cls.__name__] = cls
                plugins[cls.__metatype__] = d
    return plugins

class DataFlowGraph(object):
    def __init__(self):
        self._workflow = None
        self._config = None
        self._graph = None
        # load plugins
        self.plugins = init_plugins()
        self.plugin_registry = {}
        # load each type here...
        try:
            self._filters = self.plugins['FILTER'].keys()
        except:
            self._filters = []
        else:
            self.plugin_registry.update(self.plugins['FILTER'])

        try:
            self._transformers = self.plugins['TRANSFORMER'].keys()
        except:
            self._transformers = []
        else:
            self.plugin_registry.update(self.plugins['TRANSFORMER'])

        try:
            self._operators = self.plugins['OPERATOR'].keys()
        except:
            self._operators = []
        else:
            self.plugin_registry.update(self.plugins['OPERATOR'])

        try:
            self._extractors = self.plugins['EXTRACTOR'].keys()
        except:
            self._extractors = []
        else:
            self.plugin_registry.update(self.plugins['EXTRACTOR'])           

        try:
            self._input_adapters = self.plugins['ADAPTER'].keys()
        except:
            self._input_adapters = []
        else:
            self.plugin_registry.update(self.plugins['ADAPTER'])

        try:
            self._output_adapters = self.plugins['PUBLISHER'].keys()
        except:
            self._output_adapter = []
        else:
            self.plugin_registry.update(self.plugins['PUBLISHER'])
            
        self._registered_instances = {}
        fp = None
        
        try:
            fp = open('projects/default.txt', 'r')
            jsconfig = fp.read()
            config = json.loads(jsconfig)
        except:
            pass
        else:
            self.loadConfig(config)
        finally:
            if fp is not None:
                fp.close()

    def newInstance(self, className):
        try:
            className = className.replace(' ', '')
            cls = self.plugin_registry[className]
            this_instance = cls()
        except:
            # need to complain about invalid className
            log.error('Failed to create component %s - Invalid Classname' % className)
            log.debug('Plugin Registry Dump:', self.plugin_registry)
            return None
        else:
            key = str(hash(this_instance))
            self._registered_instances[key] = this_instance
            return key

    def removeInstance(self, key):
        try:
            self._registered_instances[key]
        except:
            log.error('Failed to delete component %s - Instance not found' % key)
            log.debug('Registered Instances: %s' % self._registered_instances)
        else:
            self._registered_instances.pop(key)

    def Inputs(self, key):
        #return self._registered_instances[key].Inputs
        # needs error handling here...
        return self._registered_instances[key].get_in_ports()

    def Outputs(self, key):
        #return self._registered_instances[key].Outputs
        return self._registered_instances[key].get_out_ports()

    def Instance(self, key):
        return self._registered_instances[key]

    def update(self, jsconfig):
        statusText = 'Unidentified Error Saving Project'
        # close any existing workflow
        if self.Workflow is not None:
            try:
                self.Workflow.close()
            except:
                pass

        # set the new updated config from the UI
        try:
            self._config = json.loads(jsconfig)
        except:
            statusText = 'This Project Configuration is Bad'
        else:
            # Check for valid input component 
            (in_status, inputs) = self.config_has_valid_input()
            (out_status, outputs) = self.config_has_valid_output()

            if in_status is False:
                statusText = 'Unable To Save Configuration<br><br>No Valid Adapter Specified<br>.'
            # Check for valid output component
            elif out_status is False:
                statusText = 'Unable To Save Configuration<br><br>No Valid Publisher Specified<br>.'
            else:
                # translate the current config into a usable DAG
                result = self.translate()
                if result is False:
                    statusText = 'Error Translating Supplied Configuration'
                # check the connectivity of the graph
                elif not self.is_connected(inputs, outputs):
                    statusText = 'Unable To Save Project<br><br>Found Broken Path Between Producer and Publisher.<br>'
                else:
                    # Build the new workflow
                    try:
                        try:
                            # get the core count from the config
                            cores = int(config['cores'])
                            # has to be at least 1
                            if cores < 1:
                                cores = 1
                        except:
                            log.warning('Could not get core count from config.')
                            traceback.print_exc()
                            log.warning('Defaulting to core count of 1')
                            cores = 1

                        #log.info('Core count: %s' % cores)
                        self.Workflow = Dataflow(self.Graph, cores)
                    except:
                        statusText = 'Error Constructing Workflow'
                    else:
                        statusText = 'Project Successfully Saved'
                        # Save config here...
                        fp = None
                        try:
                            fp = open('projects/default.txt', 'w')
                            fp.write(jsconfig)
                        except:
                            log.error('Unable to save configuration')
                        else:
                            log.info('Configuration successfully saved')
                        finally:
                            if fp is not None:
                                fp.close()

        return statusText

    def is_connected(self, starts, ends):
        for start in starts:
            for end in ends:
                connected = self.find_path(self.Graph, self._registered_instances[start], self._registered_instances[end])
                if connected is None:
                    return False
        return True

    def find_path(self, graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if not graph.has_key(start):
            return None
        for node in graph[start]:
            if node not in path:
                newpath = self.find_path(graph, node, end, path)
                if newpath: 
                    return newpath
        return None

    def _get_workflow(self):
        return self._workflow

    def _set_workflow(self, wf):
        self._workflow = wf

    def _get_config(self):
        return self._config

    def _set_config(self, config):
        self._config = config

    def _get_graph(self):
        return self._graph

    def _set_graph(self, graph):
        self._graph = graph

    def config_has_valid_input(self):
        valid_input = False
        valid_inputs = []
        for container in self.Config['containers']:
            if container['type'] == 'Adapters':
                valid_input = True
                valid_inputs.append(container['cid'])
        return (valid_input, valid_inputs)

    def config_has_valid_output(self):
        valid_output = False
        valid_outputs = []
        for container in self.Config['containers']:
            if container['type'] == 'Publishers':
                valid_output = True
                valid_outputs.append(container['cid'])
        return (valid_output, valid_outputs)

    def translate(self):
        status = None
        G = {}
        for entry in self.Config['wires']:
            try:
                source_container_id = entry['src']['moduleId']
                target_container_id = entry['tgt']['moduleId']
                input = entry['tgt']['termid']
                output = entry['src']['termid']
                source_key = self.Config['containers'][source_container_id]['cid']
                target_key = self.Config['containers'][target_container_id]['cid']
                source = self._registered_instances[source_key]
                target = self._registered_instances[target_key]
            except:
                status = False
            else:
                if G.has_key(source):
                    current_children = G[source]
                    current_children[target] = (output, input)
                    G[source] = current_children
                else:
                    G[source] = {target:(output, input)}
                status = True

        # set the graph 
        self.Graph = G
        return status

    def send(self, doc):
        statusText = 'Unexpected Error Running Project'

        if self.Workflow is not None:
            self.Workflow.send(doc)
            statusText = 'Documented Submitted Sucessfully'
        else:
            log.error('No workflow defined')
            statusText = 'No Active Workflow Defined'

        return statusText

    def _get_filters(self):
        self._filters.sort()
        return self._filters

    def _get_operators(self):
        self._operators.sort()
        return self._operators

    def _get_extractors(self):
        self._extractors.sort()
        return self._extractors

    def _get_input_adapters(self):
        self._input_adapters.sort()
        return self._input_adapters

    def _get_output_adapters(self):
        self._output_adapters.sort()
        return self._output_adapters

    def _get_transformers(self):
        self._transformers.sort()
        return self._transformers

    def getComponentConfig(self, id):
        try:
            params = self._registered_instances[id].get_parameters()
        except:
            log.error('Could not get component with id %s' % id)
            params = 'null'
        log.debug('Component Parameters: %s' % params)
        return params

    def setParam(self, id, param, value):
        try:
            self._registered_instances[id].set_parameter(param, value)
            log.debug('Setting Parameters: %s = %s' % (param, value))
        except:
            log.error('Unable to set paramaters: %s' % (param, value))

    # class properties
    Config = property(_get_config, _set_config)
    Graph = property(_get_graph, _set_graph)
    Workflow = property(_get_workflow, _set_workflow)
    Filters = property(_get_filters)
    Transformers = property(_get_transformers)
    Extractors = property(_get_extractors)
    InputAdapters = property(_get_input_adapters)
    OutputAdapters = property(_get_output_adapters)
    Operators = property(_get_operators)

    def loadConfig(self, config):
        for mod in config['containers']:
            this_mod = mod['filterName']
            id = self.newInstance(this_mod)
            mod['cid'] = id
            try:
                for key, val in mod['params'].items():
                    self.setParam(id, key, val[0])
            except:
                pass

        self.update(json.dumps(config))

