#!/usr/bin/env python3

from gr import ref, unwrap, wrap, new_feature
import copy

def new_type(graph, name):
    type_type_feat = graph.feature('type_type')
    attr_type_feat = graph.feature('attr_type')
    res = {}
    res[type_type_feat.get('name')] = name
    res[type_type_feat.get('type')] = type_type_feat.ref('type_type')
    res[type_type_feat.get('attrs')] = []
    return res

def new_attr(graph, name, dbtype, array=False):
    type_type_feat = graph.feature('type_type')
    attr_type_feat = graph.feature('attr_type')
    res = {}
    res[type_type_feat.get('name')] = name
    res[type_type_feat.get('type')] = type_type_feat.ref('attr_type')
    res[attr_type_feat.get('array')] = array
    res[attr_type_feat.get('dbtype')] = dbtype
    return res

def init_link_sysem(graph):
    type_feat = graph.feature('type_type', True)
    attr_type = graph.get(type_feat.get('attr_type'))
    target_attr = new_attr(graph, 'target', 'ref')
    graph.insert(target_attr)
    target_attr[unwrap(target_attr)] = ref(target_attr)
    graph.update(target_attr)

    link_loader = new_feature(graph, 'blazeva1', 'link', '0.1')
    link_loader['target'] = ref(target_attr)
    graph.insert(link_loader)
    graph.add_loader(link_loader)

def init_type_system(graph):
    type_type = {}
    attr_type = {}
    name_attr = {}
    type_attr = {}
    attrs_attr = {}
    array_attr = {}
    dbtype_attr = {}
    for entry in [type_type, attr_type, name_attr, type_attr, attrs_attr, array_attr, dbtype_attr]:
        graph.insert(entry) # obtain ids

    type_type[unwrap(name_attr)] = 'Type'
    type_type[unwrap(type_attr)] = ref(type_type)
    type_type[unwrap(attrs_attr)] = [ref(name_attr), ref(type_attr), ref(attrs_attr)]
    graph.update(type_type)

    attr_type[unwrap(name_attr)] = 'Attr'
    attr_type[unwrap(type_attr)] = ref(type_type)
    attr_type[unwrap(attrs_attr)] = [ref(name_attr), ref(type_attr), ref(array_attr), ref(dbtype_attr)]
    graph.update(attr_type)

    for entry in [name_attr, type_attr, attrs_attr, array_attr, dbtype_attr]:
        entry[unwrap(type_attr)] = ref(attr_type)
        entry[unwrap(array_attr)] = False
        graph.update(entry)

    name_attr[unwrap(name_attr)] = 'name'
    name_attr[unwrap(dbtype_attr)] = 'str'
    type_attr[unwrap(name_attr)] = 'type'
    type_attr[unwrap(dbtype_attr)] = 'ref'
    attrs_attr[unwrap(name_attr)] = 'attrs'
    attrs_attr[unwrap(dbtype_attr)] = 'ref'
    attrs_attr[unwrap(array_attr)] = True
    array_attr[unwrap(name_attr)] = 'array'
    array_attr[unwrap(dbtype_attr)] = 'bool'
    dbtype_attr[unwrap(name_attr)] = 'dbtype'
    dbtype_attr[unwrap(dbtype_attr)] = 'str'
    for entry in [name_attr, type_attr, attrs_attr, array_attr, dbtype_attr]:
        graph.update(entry)

    loader = graph.feature('loader', True)
    # todo fixup loader scope, name, and version to be valid attribute types
    #  loader_entry = graph.get(loader.id())
    #  loader_scope = graph.get(loader_entry['scope'])
    #  loader_scope[type_attr]
    #  loader_name = { 'name': 'name' }
    #  loader_version = { 'name': 'version' }
    attr_type_loader = {
        loader.get('scope'): 'blazeva1',
        loader.get('name'): 'attr_type',
        loader.get('version'): '0.1',
        'name': ref(name_attr),
        'dbtype': ref(dbtype_attr),
        'array': ref(array_attr),
    }
    type_type_loader = {
        loader.get('scope'): 'blazeva1',
        loader.get('name'): 'type_type',
        loader.get('version'): '0.1',
        'type_type': ref(type_type),
        'attr_type': ref(attr_type),
        'type': ref(type_attr),
        'name': ref(name_attr),
        'attrs': ref(attrs_attr),
    }

    graph.insert(attr_type_loader)
    graph.insert(type_type_loader)

    graph.add_loader(attr_type_loader)
    graph.add_loader(type_type_loader)
