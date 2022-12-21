'''
This is root of the Noosphere project. For an concept explanation and examples refer to the documentation http://noosphere.readthedocs.io/
'''

from noosphere.utils import ref, wrap, unwrap

class NosError(RuntimeError):
    pass

class Module:
    def __init__(self, data):
        self.data = data
    def get(self, name):
        return unwrap(self.data[name])
    def ref(self, name):
        return self.data[name]
    def id(self):
        return self.data['id']

def new_module(graph, scope, name, version):
    loader = graph.module('loader', True)
    link_loader = {
        loader.get('scope'): scope,
        loader.get('name'): name,
        loader.get('version'): version,
    }
    return link_loader

class Graph:

    def __init__(self, data):
        self.data = data
        self.data.load()
        self._run_loaders()

    #== Root loader functions ==================================================

    def init_loader(self):
        self._run_loaders()
        loader_scope = { 'name': 'scope' }
        loader_name = { 'name': 'name' }
        loader_version = { 'name': 'version' }
        self.insert(loader_scope)
        self.insert(loader_name)
        self.insert(loader_version)
        loader = {
            unwrap(loader_scope): 'blazeva1',
            unwrap(loader_name): 'loader',
            unwrap(loader_version): '0.1',
            'scope': ref(loader_scope),
            'name': ref(loader_name),
            'version': ref(loader_version),
        }
        self.data.insert(loader)
        # loader must be added here as add_module uses it
        root_loader = {'id':'!0','modules':[ref(loader)]}
        self.data.update(root_loader)
        self.modules = {'loader': loader}

    def add_module(self, node):
        root_loader = self._get_root_loader()
        if root_loader is None or 'modules' not in root_loader:
            raise NosError('Root loader is not initialized.')
        root_loader['modules'].append(ref(node))
        self.update(root_loader)
        self._run_loaders()

    def module(self, name, compulsory=False):
        if name is not None and name in self.modules:
            res_feat = self.get(self.modules[name])
            if res_feat:
                return Module(res_feat)
        if not compulsory:
            return None
        raise NosError('unable to find "{}" module in {}'.format(name, self.modules))

    def _get_root_loader(self):
        try:
            return self.get('!0')
        except NosError:
            return None

    def _run_loaders(self):
        new_modules = {}
        root_loader = self._get_root_loader()
        if not hasattr(self, 'modules'):
            self.modules = {'loader': root_loader['modules'][0]}
        if root_loader is not None:
            assert 'modules' in root_loader
            loader = self.module('loader', True)
            for module in root_loader['modules']:
                module = self.get(module)
                name_id = loader.get('name')
                if name_id in module:
                    new_modules[module[name_id]] = module
        self.modules = new_modules

    def get_modules(self):
        return self.modules

    #== Functions for elementary operations ====================================

    def get_id(self, entry_or_id):
        '''returns id when given either id or the whole node'''
        if self.data.is_id(entry_or_id):
            return entry_or_id
        res = self.data.get_id(entry_or_id)
        if res is not None:
            return res
        raise NosError('asked for an id of entry which is not an id not a node: {}'.format(entry_or_id))

    def find(self, filter_lambda=None, ids=None):
        '''given a query function returns all nodes which equal on the given structure'''
        if ids is None:
            entries = self.data.all()
        else:
            entries = [self.get(x) for x in ids]
        if filter_lambda is None:
            filter_lambda = lambda x: True
        return [x for x in entries if filter_lambda(x)]

    def get(self, entry_or_id):
        '''returns the up-to-date version of the entry given entry or its id'''
        assert entry_or_id is not None
        node_id = self.get_id(entry_or_id)
        if not self.data.is_id(node_id):
            raise NosError('node_id should be int, it is ' + str(type(node_id)))
        node = self.data.get(node_id)
        if node is None:
            raise NosError('node with id ' + str(node_id) + ' could not be found')
        return node

    def insert(self, new_entry):
        '''create a new entry and assign a new id to the node'''
        assert new_entry is not None
        self.valid_entry(new_entry)
        self.data.insert(new_entry)
        self.set_other_side_of_references({}, new_entry)

    def update(self, entry):
        '''alter an existing entry'''
        assert entry is not None
        self.valid_entry(entry)
        old_entry = self.get(entry)
        self.data.update(entry)
        self.set_other_side_of_references(old_entry, entry)

    def remove(self, entry_or_id):
        '''remove and existing entry'''
        rem_id = self.get_id(entry_or_id)
        rem_node = self.get(rem_id)
        self.set_other_side_of_references(rem_node, {})
        self.data.remove(rem_id)

    def clear(self):
        '''remove all entities and start with a clear graph'''
        self.data.clear()
        self.init_loader()
