#!/usr/bin/env python3

import copy
import json
import sys
import os

# == Main ========================================================================

def main():
    while run_cmd(shift('Command')):
        pass

def run_cmd(cmd):
    db_name = 'data.json'
    if cmd is None:
        print('exit')
        return False
    elif cmd == '':
        print('The command is empty')
    elif cmd == 'reset':
        data = FileDB(db_name)
        data._resetdb()
    elif cmd == 'ls':
        data = Graph(db_name)
        all_nodes = data.find_nodes()
        print(json.dumps(all_nodes, indent=4))
    elif cmd == 'add':
        data = Graph(db_name)
        entry = json.loads(input())
        data.insert_node(entry)
    elif cmd == 'rem':
        pass
    elif cmd == 'exit':
        return False
    else:
        print('The command "{}" is unknown'.format(cmd))
    return True

def shift(what):
    if len(sys.argv) == 1:
        try:
            return input(what + ': ')
        except EOFError:
            return None
    res = sys.argv[1]
    sys.argv = [sys.argv[0]] + sys.argv[2:]
    return res

# == Main Logic ==================================================================

class GrError(RuntimeError):
    pass

# given an entity and its attribute return its value as an array
def get_entity_attribute_array(entity, attr, is_array):
    if attr not in entity:   return []
    else:
        value = entity[attr]
        if is_array:
            return value
        return [value]

# compare two entries' attributes and split their differences into lists
# of new elements and old elements
def added_removed_elements(old_entry, new_entry, attr_name, is_array):
    old_set = set(get_entity_attribute_array(old_entry, attr_name, is_array))
    new_set = set(get_entity_attribute_array(new_entry, attr_name, is_array))
    return (list(new_set - old_set), list(old_set - new_set))

# == Data Keeping Structure ======================================================
# This structure
# * keeps elementary datapoints: nodes and edges
# * has methods to work with them
#
# It returns *copy* of the data and you need to save it to take effect. This is
# mainly done for internal reasons as it is hard to know what changed otherwise.
# Each *node* has an internal 'id' which is used to identify it in the database.
# Nodes have *flat* structure. Each attribute may be either dbtype or reference.
# Dbtype are standard things -- number, string, boolean, etc.
# Reference is *pointer* to any another node -- just dict with 'id' attribute.
# References represent one-way edges of the graph.
#
# <<< TODO >>>
# The typing is optional, but provieds a big boost to the functionality.
# More precisely, references of nodes may be *joined* which makes the
# references bi-directional so they update automatically.

class Graph:

    def __init__(self, location):
        self.data = FileDB(location)

    #== Simple functions for elementary operations =============================

    # checks whether a thing is a valid id
    def is_id(self, identifier):
        return isinstance(identifier, int)

    # returns id when given either id or the whole node
    def get_id(self, entry_or_id):
        if self.is_id(entry_or_id):
            return entry_or_id
        if 'id' in entry_or_id:
            assert entry_or_id['id'] is not None
            return entry_or_id['id']
        raise GrError('asked for an id of entry which is not an id not a node: {}'.format(entry_or_id))

    # given a query function returns all nodes which equal on the given structure
    def find_nodes(self, filter_lambda=None):
        if filter_lambda is None:
            filter_lambda = lambda x: True
        return list(filter(filter_lambda, self.data._get('nodes').items()))

    # returns an updated version of the entry given entry or its id
    def get_node(self, entry_or_id):
        node_id = self.get_id(entry_or_id)
        if not self.is_id(node_id):
            raise GrError('node_id should be int, it is ' + str(type(node_id)))
        nodes = self.data._get('nodes')
        if str(node_id) in nodes:
            return copy.deepcopy(nodes[str(node_id)])
        else:
            raise GrError('node with id ' + str(node_id) + ' could not be found')

    # create a new entry and assign a new id to the node
    def insert_node(self, new_entry):
        assert 'id' not in new_entry
        new_entry['id'] = self.data.db['last_node_id']
        self.data._set('last_node_id', self.data._get('last_node_id') + 1)
        self.update_node(new_entry)

    # alter an existing entry
    def update_node(self, entry):
        self.data.db['nodes'][str(self.get_id(entry))] = entry
        self.data.save()

    # remove and existing entry
    def delete_node(self, entry_or_id):
        rem_id = self.get_id(entry_or_id)
        rem_node = self.get_node(rem_id)
        nodes = self.data._get('nodes')
        del nodes[rem_id]
        self.data._set('nodes', nodes)

    #== utility functions to be used by higher level functions =================

    def _relation_attributes_iterator(self, entity):
        entity_type = self.get_node(entity)
        assert 'attrs' in entity_type
        for attr_id in entity_type['attrs']:
            attr = self.get_node(attr_id)
            if attr['value'] == 'relation':
                attr['array'] = 'array' in attr and attr['array']
                yield attr

    # set old reference values to a new entity
    def _substitute_references(self, entity, old_entity):
        res = copy.deepcopy(entity)
        if not old_entity:
            old_entity = {}
        try:
            assert 'type' in res
            for attr in self._relation_attributes_iterator(res['type']):
                assert 'name' in attr
                attr_name = attr['name']
                if attr_name not in old_entity:
                    old_entity[attr_name] = '' # todo: which default value?
                res[attr_name] = old_entity[attr_name]
        except GrError:
            pass
        return res

    # save a new node with a new id, don't fix its references
    def _add_raw_node(self, new_entry):
        assert 'id' not in new_entry
        new_entry['id'] = self.data.db['last_node_id']
        self.data._set('last_node_id', self.data._get('last_node_id') + 1)
        self._set_raw_node(new_entry)
        return new_entry

    # set a node, don't fix its references
    def _set_raw_node(self, new_entry):
        assert 'id' in new_entry
        assert new_entry['id'] is not None
        self.data.db['nodes'][str(new_entry['id'])] = new_entry

    def _set_node_without_references(self, new_entry):
        try:
            old_entity = self.get_node(new_entry['id'])
        except GrError:
            old_entity = None
        self._set_raw_node(self._substitute_references(new_entry, old_entity))

    #== higher level functions for graphs ======================================

    # change edges in db so that the entry contains the same references as the given entry
    def _modify_references(self, new_entry):
        old_entry = self.get_node(new_entry['id'])
        assert old_entry is not None
        if 'type' in new_entry:
            # type change is not allowed, remove and add instead
            assert old_entry['type'] == new_entry['type']
            try:
                entity_type = self.get_node(new_entry['type'])
                for attr in self._relation_attributes_iterator(entity_type):
                    attr_name = attr['name']
                    is_array = attr['array']
                    (new_nodes, removed_nodes) = added_removed_elements(old_entry, new_entry, attr_name, is_array)
                    for removed_node in removed_nodes:
                        self._rem_edge(old_entry, attr, removed_node)
                    for new_node in new_nodes:
                        self._add_edge(old_entry, attr, new_node)
            except GrError:
                print('entry type is not in db:', new_entry)
        else:
            print('entry does not have a type:', new_entry)
        self.data.db['nodes'][str(old_entry['id'])] = old_entry

    def _set_entry_attr(self, entry, attr, value):
        is_array = attr['array']
        attr_name = attr['name']
        if is_array:
            if attr_name not in entry: entry[attr_name] = []
            entry[attr_name] += [value]
        else:
            entry[attr_name] = value

    def _rem_entry_attr(self, entry, attr, value):
        is_array = attr['array']
        attr_name = attr['name']
        if is_array:
            if attr_name not in entry:
                entry[attr_name] = []
            if value not in entry[attr_name]:
                raise GrError('attempt to remove value ' + value + ' which is not in ' + attr['name'] + ' of object with id ' + entry['id'])
            res_set = set(entry[attr_name])
            res_set.remove(value)
            entry[attr_name] = list(res_set)
        else:
            entry[attr_name] = None

    # add mutual reference ids
    def _add_edge(self, entry, attr, value):
        self._set_entry_attr(entry, attr, value)
        self._set_raw_node(entry)
        target_node = self.get_node(value)
        target_attribute = self.get_node(attr['target'])
        self._set_entry_attr(target_node, target_attribute, entry['id'])
        self._set_raw_node(target_node)

    # remove mutual reference ids
    def _rem_edge(self, entry, attr, value):
        self._rem_entry_attr(entry, attr, value)
        self._set_raw_node(entry)
        target_node = self.get_node(value)
        target_attribute = self.get_node(attr['target'])
        self._rem_entry_attr(target_node, target_attribute, entry['id'])
        self._set_raw_node(target_node)

    def add_connection(self, fr, to):
        if self.is_id(fr):
            fr = self.get_node(fr)
        if self.is_id(to):
            to = self.get_node(to)
        fr_type = self.get_node(fr['type'])
        if fr_type['name'] != 'Attr':
            raise GrError('The first argument of add_connection must be of type Attribute')
        to_type = self.get_node(to['type'])
        if to_type['name'] == 'Type':
            # since the given node is Type we create a new attribute which will track this connection
            par_name = '_' + fr['name']
            attr_attr = Attr(par_name, 'relation', True)
            self.insert_node(attr_attr)
            to_type['attrs'] += [attr_attr]
            to = attr_attr
            to_type = self.get_node(to['type'])
        if to_type['name'] != 'Attr':
            raise GrError('The second argument of an add_connection must be of type Attribute or Type')
        fr['target'] = to['id']
        to['target'] = fr['id']
        self._set_raw_node(fr)
        self._set_raw_node(to)

    #  def find_nodes(self, type_id):
        #  assert not self.is_id(type_id)
        #  nodes = self.data._get('nodes')
        #  res = []
        #  for key in nodes.items():
            #  node = self.get_node(key) # intentional - to have a proper object regardles of representation
            #  node_type = self.get_node(node['type'])
            #  if node_type['id'] == type_id:
                #  res += [node]
        #  return res


# ==== type system =================

def set_if_exists(var, tp):
    if tp and 'id' in tp:
        var['type'] = tp['id']
    else:
        var['type'] = None

class Type(dict):
    def __init__(self, name, desc):
        self['name'] = name
        self['desc'] = desc
        global type_type
        set_if_exists(self, type_type)
        self['attrs'] = []

class Attr(dict):
    def __init__(self, name, value, array=False):
        dict.__init__()
        self['name'] = name
        self['value'] = value
        if array:
            self['array'] = array
        global attr_type
        set_if_exists(self, attr_type)

def init_type_system(d):
    # first, create raw types without references
    global type_type
    type_type = None # is set so that Type creation doesn't fail on nonexistant global varialbe
    type_type = Type('Type', 'Each node in the database should have one attribute called "type" which defines its structure. When the type of a node is THIS node then the node itself defines a new structure. This is achieved by connection with nodes of type (nodeid) 101 via attribute "attrs".') 
    global attr_type
    attr_type = Type('Attr', 'Each node N which has "type" set to 100 defines a node structure. Every other node having "type" set to N should contain all parameters which are contained in attribute "attrs" in N. Each attribute contains "name" which says the attribyte description string, and "value" which says type of what can be saved to the attribute.')
    # create raw attributes
    name_attr = Attr('name', 'string')
    type_attr = Attr('type', 'relation', False)
    desc_attr = Attr('desc', 'string')
    attrs_attr = Attr('attrs', 'relation', True)
    value_attr = Attr('value', 'dbtype')
    array_attr = Attr('array', 'boolean')
    # _type_attr = Attr('_type', 'relation', True})
    # _attrs_attr = Attr('_attrs', 'relation', True})

    # add the types so that
    d._add_raw_node(type_type)
    d._add_raw_node(attr_type)

    attributes = [name_attr, type_attr, desc_attr, attrs_attr, value_attr, array_attr]
    for attr in attributes:
        attr['type'] = attr_type['id'] # needed for connections
        d._add_raw_node(attr)

    # type needs to be set for add connection as it check if type is Attr or Type
    type_type['type'] = type_type['id']
    attr_type['type'] = type_type['id']

    d.add_connection(type_attr, type_type)
    d.add_connection(attrs_attr, attr_type)

    # d._add_edge(type_type, type_attr, type_type['id'])
    # d._add_edge(attr_type, type_attr, type_type['id'])

    # d._set_raw_node(type_type)
    # d._set_raw_node(attr_type)

    # # attributes of type must be added manually as the type system is not initialized yet
    # # the problem would arise as we count deltas, the type of this instance is not yet initialized
    # # so the references will not propagate; after setting these values we may initialize all
    # # type definitions normally
    # for attr in [name_attr['id'], type_attr['id'], desc_attr['id'], attrs_attr['id']]:
    #     d._add_edge(type_type, attrs_attr, attr)

    # # changing only the references and saving the instance will propagate the references to
    # # respective objects
    # attr_type['attrs'] = [name_attr['id'], type_attr['id'], value_attr['id'], array_attr['id']]
    # d.update_node(attr_type)
    # assert '_type' in d.get_node(type_type['id'])


# == Data Utility ================================================================

class FileDB(object):

    def __init__(self, location):
        self.location = os.path.expanduser(location)
        self.db = None
        self.load(self.location)

    def load(self, location):
        if os.path.exists(location):
            self._load()
        else:
            self._resetdb()
        return True

    def save(self):
        return self._dumpdb()

    def delete(self):
        os.remove(self.location)

    def _load(self):
        self.db = json.load(open(self.location, "r"))

    def _dumpdb(self):
        try:
            json.dump(self.db, open(self.location, "w+"), indent=4)
            return True
        except:
            return False

    def _resetdb(self):
        self.db = {
            'nodes':{},
            'last_node_id':100,
        }
        self._dumpdb()
        return True

    def _set(self, key, value):
        try:
            self.db[str(key)] = value
            self._dumpdb()
            return True
        except Exception as exc:
            print("[X] Error Saving Values to Database : " + str(exc))
            return False

    def _get(self, key):
        try:
            return self.db[key]
        except KeyError:
            print("No Value Can Be Found for " + str(key))
            return False

    def _delete(self, key):
        if not key in self.db:
            return False
        del self.db[key]
        self._dumpdb()
        return True

# == Main Initialization =========================================================

if __name__ == '__main__':
    main()

