#!/usr/bin/env python3

import json
import sys
import os

class GrError(RuntimeError):
    pass

class Feature:
    def __init__(self, data):
        self.data = data
    def get(self, name):
        return unwrap(self.data[name])
    def ref(self, name):
        return self.data[name]
    def id(self):
        return self.data['id']

def new_feature(graph, scope, name, version):
    loader = graph.feature('loader', True)
    link_loader = {
        loader.get('scope'): scope,
        loader.get('name'): name,
        loader.get('version'): version,
    }
    return link_loader

def warn(text):
    print('>>> WARNING <<<', text)

# == Data Keeping Structure ======================================================
# This structure
# * keeps elementary datapoints: nodes and edges
# * has methods to work with them
#
# It returns *copy* of the data and you need to save it to take effect. This is
# mainly done for internal reasons as it is hard to know what changed otherwise.
# Each *node* has an internal 'id' which is used to identify it in the database.
# Nodes have *flat* structure. Each attribute may be either dbtype or reference.
# Dbtype are standard things -- int, str, bool, etc.
# Reference is *pointer* to any another node -- just dict with 'id' attribute.
# References represent one-way edges of the graph.

class Graph:

    def __init__(self, data):
        self.data = data
        self.data.load()

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
        # loader must be added here as add_loader uses it
        root_loader = {'id':'!0','features':[ref(loader)]}
        self.data.update(root_loader)
        self.features = {'loader': loader}

    def add_loader(self, node):
        root_loader = self._get_root_loader()
        if root_loader is None or 'features' not in root_loader:
            raise GrError('Root loader is not initialized.')
        root_loader['features'].append(ref(node))
        self.update(root_loader)
        self._run_loaders()

    def feature(self, name, compulsory=False):
        if name is not None and name in self.features:
            res_feat = self.get(self.features[name])
            if res_feat:
                return Feature(res_feat)
        if not compulsory:
            return None
        raise GrError('unable to find "{}" feature in {}'.format(name, self.features))

    def _get_root_loader(self):
        try:
            return self.get('!0')
        except GrError:
            return None

    def _run_loaders(self):
        new_features = {}
        root_loader = self._get_root_loader()
        if root_loader is not None:
            assert 'features' in root_loader
            loader = self.feature('loader', True)
            for feature in root_loader['features']:
                feature = self.get(feature)
                name_id = loader.get('name')
                if name_id in feature:
                    new_features[feature[name_id]] = feature
        self.features = new_features

    #== Simple functions for elementary operations =============================

    # returns id when given either id or the whole node
    def get_id(self, entry_or_id):
        if self.data.is_id(entry_or_id):
            return entry_or_id
        res = self.data.get_id(entry_or_id)
        if res is not None:
            return res
        raise GrError('asked for an id of entry which is not an id not a node: {}'.format(entry_or_id))

    # given a query function returns all nodes which equal on the given structure
    def find(self, filter_lambda=None, ids=None):
        if ids is None:
            entries = self.data.all()
        else:
            entries = list(map(self.get, ids))
        if filter_lambda is None:
            filter_lambda = lambda x: True
        return list(filter(filter_lambda, entries))

    # returns an updated version of the entry given entry or its id
    def get(self, entry_or_id):
        assert entry_or_id is not None
        node_id = self.get_id(entry_or_id)
        if not self.data.is_id(node_id):
            raise GrError('node_id should be int, it is ' + str(type(node_id)))
        node = self.data.get(node_id)
        if node is None:
            raise GrError('node with id ' + str(node_id) + ' could not be found')
        return node

    # create a new entry and assign a new id to the node
    def insert(self, new_entry):
        assert new_entry is not None
        self.valid_entry(new_entry)
        self.data.insert(new_entry)
        self.set_other_side_of_references({}, new_entry)

    # alter an existing entry
    def update(self, entry):
        assert entry is not None
        self.valid_entry(entry)
        old_entry = self.get(entry)
        self.data.update(entry)
        self.set_other_side_of_references(old_entry, entry)

    # remove and existing entry
    def remove(self, entry_or_id):
        rem_id = self.get_id(entry_or_id)
        rem_node = self.get(rem_id)
        self.set_other_side_of_references(rem_node, {})
        self.data.remove(rem_id)

    # remove all entities and start with a clear graph
    def clear(self):
        self.data.clear()
        self.init_loader()

    #== data integrity checking ================================================

    def valid_entry(self, entry):
        attr_type_feat = self.feature('attribute_id')
        for attr_id in entry.keys():
            if attr_type_feat:
                if attr_id == attr_type_feat.get('dbtype'):
                    if entry[attr_id] not in ['str', 'int', 'float', 'ref', 'bool', None]:
                        raise GrError('dbtype has invalid value {}'.format(entry[attr_id]))
                elif self.data.is_id(attr_id):
                    attr_type = self.get(attr_id)
                    dbtype = attr_type_feat.get('dbtype')
                    array = attr_type_feat.get('array')
                    if dbtype not in attr_type or array not in attr_type:
                        warn('attribute {} used in an entry {} is invalid attribute type as it does not contain either "dbtype" or "array" attribute'.format(attr_type, entry))
                    else:
                        self.valid_attribute(entry[attr_id], attr_type[dbtype], attr_type[array])
                        continue
                elif attr_id != 'id' and not ('id' in entry and entry['id'] == '!0'):
                    loader = self.feature('loader', True)
                    name_id = loader.get('name')
                    if name_id not in entry: # means that this is not a loader
                        warn('although attribute typing is enabled an entry was inserted with plain attribute name "{}"'.format(attr_id))
                        warn('entry: {}'.format(entry))
            self.valid_attribute(entry[attr_id], None, None)

    def valid_attribute(self, attr_value, assumed_type, assumed_array):
        attr_type = self.retrieve_value_type(attr_value)
        is_array = (attr_type == 'arr')
        if assumed_array is not None:
            if is_array and not assumed_array:
                raise GrError('type is array but it should not be')
            if not is_array and assumed_array:
                raise GrError('type is not array but it should be')
        if is_array:
            types = list(filter(lambda x: x is not None, map(self.retrieve_value_type, attr_value)))
            for val in types:
                if val == 'arr':
                    raise GrError('array may not contain another array')
                if types[0] != val:
                    raise GrError('array has two different types; there are elements of types {} and {}'.format(types[0], val))
            if len(attr_value) != 0:
                attr_type = self.retrieve_value_type(attr_value[0])
            else:
                attr_type = 'none'
        if attr_type != 'none' and assumed_type is not None and assumed_type != attr_type:
            raise GrError('data inconsistency detected; value {} of type {} should have been {}'.format(attr_value, attr_type, assumed_type))

    def retrieve_value_type(self, attr_value):
        if attr_value is None:
            return 'none'
        if isinstance(attr_value, list):
            return 'arr'
        if isinstance(attr_value, str):
            return 'str'
        if isinstance(attr_value, bool):
            return 'bool'
        if isinstance(attr_value, int):
            return 'int'
        if isinstance(attr_value, float):
            return 'float'
        if 'id' in attr_value and len(attr_value.keys()) == 1:
            return 'ref'
        raise GrError('unrecognized data type of {}'.format(attr_value))

    #== double-sided references ================================================

    def set_other_side_of_references(self, old_entry, new_entry):
        # todo fixme - this function was originally written to fetch type from the entry type, go through its attributes and set the other side depending on what it targets; now we need no entry type; simply if attribute name is an id of a valid attribute with target property of the link feature then we may set the other side of the link
        attr_feat = self.feature('attribute_id')
        links_feat = self.feature('link')
        if attr_feat and links_feat:
            old_attrs_ids = unwrap(self._relation_attributes_iterator(old_entry))
            new_attrs_ids = unwrap(self._relation_attributes_iterator(new_entry))
            if new_entry is not None and 'id' in new_entry:
                entry_ref = ref(new_entry)
            elif old_entry is not None and 'id' in old_entry:
                entry_ref = ref(old_entry)
            else:
                raise GrError('Double-sided reference failed as both new and old entry is None or invalid')
            for attr_id in list(set(old_attrs_ids).union(set(new_attrs_ids))):
                attr = self.get(attr_id)
                target_attr = links_feat.get('target')
                if target_attr not in attr:
                    continue
                other_side_attr_ref = attr[target_attr]
                if other_side_attr_ref:
                    array_par = attr_feat.get('array')
                    is_array = attr[array_par]
                    other_side_attr_id = unwrap(other_side_attr_ref)
                    other_side_attr = self.get(other_side_attr_id)
                    (inserted_node_ids, removed_node_ids) = added_removed_elements_ids(old_entry, new_entry, attr_id, is_array)
                    for inserted_node_id in inserted_node_ids:
                        node = self.get(inserted_node_id)
                        if other_side_attr[array_par]:
                            node[other_side_attr_id].append(entry_ref)
                        else:
                            if other_side_attr_id in node and node[other_side_attr_id]:
                                pass # fixme - invalidate reference on the other side
                            node[other_side_attr_id] = entry_ref
                        self.data.update(node)
                    for removed_node_id in removed_node_ids:
                        node = self.get(removed_node_id)
                        if other_side_attr[array_par]:
                            node[other_side_attr_id].remove(entry_ref)
                        else:
                            node[other_side_attr_id] = None
                        self.data.update(node)

    #== utility functions for link module ======================================

    def _relation_attributes_iterator(self, entity):
        attr_type_feat = self.feature('attribute_id')
        if attr_type_feat:
            for attr_id in entity.keys():
                if self.data.is_id(attr_id):
                    attr = self.get(attr_id)
                    if attr_type_feat.get('dbtype') not in attr:
                        warn('attribute without dbtype: {}'.format(attr))
                    elif attr[attr_type_feat.get('dbtype')] == 'ref':
                        yield attr

# == Utility functions ===========================================================

# functions ref, unwrap, and wrap are made for reference work
# as each reference is coded as {'id': identificator} it is easier
# to have these functions to work with the identificator itself

# given an object or a list of objects construct just a reference to them
def ref(reference):
    return wrap(unwrap(reference))
# given an one or more object or references, retrieve their ids
def unwrap(reference):
    try:
        return list(map(lambda x: x['id'], iter(reference)))
    except TypeError:
        pass
    assert 'id' in reference
    return reference['id']
# given one or more ids construct respective references
def wrap(reference):
    if(isinstance(reference, list)):
        return list(map(lambda x: {'id': x}, iter(reference)))
    return {'id': reference}

# given an entity and its attribute return its value as an array
def get_entity_attribute_array(entity, attr_id, is_array):
    if entity is None or attr_id not in entity:
        return []
    value = entity[attr_id]
    if value is None:
        return []
    if is_array:
        return unwrap(value)
    return [unwrap(value)]

# compare two entries' attributes and split their differences into lists
# of new elements and old elements
def added_removed_elements_ids(old_entry, new_entry, attr_id, is_array):
    old_set = set(get_entity_attribute_array(old_entry, attr_id, is_array))
    new_set = set(get_entity_attribute_array(new_entry, attr_id, is_array))
    return (list(new_set - old_set), list(old_set - new_set))
