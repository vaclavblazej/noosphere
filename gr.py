#!/usr/bin/env python3

import json
import sys
import os

import gr_types

class GrError(RuntimeError):
    pass

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
#
# <<< TODO >>>
# The typing is optional, but provieds a big boost to the functionality.
# More precisely, references of nodes may be *joined* which makes the
# references bi-directional so they update automatically.

class Graph:

    def __init__(self, data):
        self.data = data
        self.data.load()

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

    #== data integrity checking ================================================

    def get_attr_type(self, entry, attr_name):
        if 'type' not in entry or entry['type'] is None:
            return None
        entry_type = self.get(entry['type'])
        attrs_type_ids = unwrap(entry_type['attrs'])
        for attr_type_id in attrs_type_ids:
            attr_type = self.get(attr_type_id)
            if 'name' in attr_type and attr_type['name'] == attr_name:
                return attr_type
        return None

    def valid_entry(self, entry):
        for attr in entry.keys():
            assumed_type = None
            assumed_array = None
            if attr == 'dbtype':
                if entry[attr] not in ['str', 'int', 'float', 'ref', 'bool', None]:
                    raise GrError('dbtype has invalid value {}'.format(entry[attr]))
            attr_type = self.get_attr_type(entry, attr)
            if attr_type is not None:
                assumed_type = attr_type['dbtype']
                assumed_array = attr_type['array']
            self.valid_attribute(entry[attr], assumed_type, assumed_array)

    def valid_attribute(self, attr_value, assumed_type, assumed_array):
        attr_type = self.retrieve_value_type(attr_value)
        is_array = (attr_type == 'arr')
        if assumed_array is not None:
            if is_array and not assumed_array:
                raise GrError('type is array byt should not be')
            if not is_array and assumed_array:
                raise GrError('type is not array byt should be')
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
        old_attrs = []
        new_attrs = []
        # fixme the removed types should be just removed; and added just added
        if ('type' in old_entry) and (old_entry['type'] is not None):
            old_attrs = unwrap(self._relation_attributes_iterator(old_entry))
        if ('type' in new_entry) and (new_entry['type'] is not None):
            new_attrs = unwrap(self._relation_attributes_iterator(new_entry))
        if new_entry is not None and 'id' in new_entry:
            entry_ref = ref(new_entry)
        else:
            entry_ref = ref(old_entry)
        for attr_id in list(set(old_attrs).union(set(new_attrs))):
            attr = self.get(attr_id)
            attr_name = attr['name']
            is_array = attr['array']
            target = attr['target']
            #  print(attr)
            if target:
                other_side_attr = self.get(target)
                #  print(old_entry)
                #  print(new_entry)
                (inserted_node_ids, removed_node_ids) = added_removed_elements_ids(old_entry, new_entry, attr_name, is_array)
                #  print(inserted_node_ids, removed_node_ids)
                for node_id in inserted_node_ids:
                    node = self.get(node_id)
                    if other_side_attr['array']:
                        node[other_side_attr['name']].append(entry_ref)
                    else:
                        if node[other_side_attr['name']] is not None:
                            pass # fixme - invalidate reference on the other side
                        node[other_side_attr['name']] = entry_ref
                    self.data.update(node)
                for node_id in removed_node_ids:
                    node = self.get(node_id)
                    if other_side_attr['array']:
                        node[other_side_attr['name']].remove(entry_ref)
                    else:
                        node[other_side_attr['name']] = None
                    self.data.update(node)

    #== utility functions to be used by higher level functions =================

    def _relation_attributes_iterator(self, entity):
        entity_type = self.get(entity['type'])
        assert 'attrs' in entity_type
        for attr_id in entity_type['attrs']:
            attr = self.get(attr_id)
            if attr['dbtype'] == 'ref':
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
    try:
        return list(map(lambda x: {'id': x}, iter(reference)))
    except TypeError:
        pass
    assert isinstance(reference, int)
    return {'id': reference}

# given an entity and its attribute return its value as an array
def get_entity_attribute_array(entity, attr, is_array):
    if entity is None or attr not in entity:
        return []
    value = entity[attr]
    if value is None:
        return []
    if is_array:
        return unwrap(value)
    return [unwrap(value)]

# compare two entries' attributes and split their differences into lists
# of new elements and old elements
def added_removed_elements_ids(old_entry, new_entry, attr_name, is_array):
    old_set = set(get_entity_attribute_array(old_entry, attr_name, is_array))
    new_set = set(get_entity_attribute_array(new_entry, attr_name, is_array))
    return (list(new_set - old_set), list(old_set - new_set))
