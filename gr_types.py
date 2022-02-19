#!/usr/bin/env python3

import gr
import copy
import json
import sys
import os

# Typing allows graph to infer which entities or attributes use some automatic functionality.

class Type(dict):
    def __init__(self, name, desc):
        self['name'] = name
        self['desc'] = desc
        global type_type
        self['type'] = gr.ref(type_type)
        self['attrs'] = []
        self['rev_types'] = []

class Attr(dict):
    def __init__(self, name, dbtype, array=False):
        self['name'] = name
        global attr_type
        self['type'] = gr.ref(attr_type)
        self['array'] = array
        self['dbtype'] = dbtype
        if self['dbtype'] == 'ref':
            self['target'] = None
        self['rev_attrs'] = []

def init_type_system(graph):
    # first, type to which all nodes representing types point to
    global type_type
    type_type = {
        'name': 'Type',
        'desc': 'Each node in the database should have one attribute called "type" which defines its structure. When the type of a node is THIS node then the node itself defines a new structure. This is achieved by connection with nodes of type (nodeid) 101 via attribute "attrs".',
        'type': None,
        'attrs': [],
        'rev_types': [],
    }
    graph.insert(type_type) # now we have id, so create a two-side relation
    type_type['type'] = gr.ref(type_type)
    type_type['rev_types'].append(gr.ref(type_type))
    graph.update(type_type)

    # prepare type for all nodes which represent attributes
    global attr_type
    attr_type = Type('Attr', 'Each node N which has "type" set to 100 defines a node structure. Every other node having "type" set to N should contain all parameters which are contained in attribute "attrs" in N. Each attribute contains "name" which says the attribyte description string, and "value" which says type of what can be saved to the attribute.')
    graph.insert(attr_type)
    type_type['rev_types'].append(gr.ref(attr_type))
    graph.update(type_type)

    name_attr = Attr('name', 'str')
    desc_attr = Attr('desc', 'str')
    type_attr = Attr('type', 'ref', False)
    attrs_attr = Attr('attrs', 'ref', True)
    rev_types_attr = Attr('rev_types', 'ref', True)

    array_attr = Attr('array', 'bool')
    dbtype_attr = Attr('dbtype', 'str')
    target_attr = Attr('target', 'ref')
    rev_attrs_attr = Attr('rev_attrs', 'ref', True)

    for attr in [name_attr, desc_attr, type_attr, attrs_attr, rev_types_attr, array_attr, dbtype_attr, target_attr, rev_attrs_attr]:
        graph.insert(attr)
        attr_type[rev_types_attr['name']].append(gr.ref(attr))
    for attr in [name_attr, desc_attr, type_attr, attrs_attr, rev_types_attr]:
        type_type['attrs'].append(gr.ref(attr))
        attr[rev_attrs_attr['name']].append(gr.ref(type_type))
        graph.update(attr)
    for attr in [name_attr, type_attr, array_attr, dbtype_attr, target_attr, rev_attrs_attr]:
        attr_type['attrs'].append(gr.ref(attr))
        attr[rev_attrs_attr['name']].append(gr.ref(attr_type))
        graph.update(attr)
    graph.update(type_type)
    graph.update(attr_type)

    target_attr['target'] = gr.ref(target_attr)
    graph.update(target_attr)
    attrs_attr['target'] = gr.ref(rev_attrs_attr)
    rev_attrs_attr['target'] = gr.ref(attrs_attr)
    graph.update(attrs_attr)
    graph.update(rev_attrs_attr)
    type_attr['target'] = gr.ref(rev_types_attr)
    rev_types_attr['target'] = gr.ref(type_attr)
    graph.update(type_attr)
    graph.update(rev_types_attr)
