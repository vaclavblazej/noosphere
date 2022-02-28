#!/usr/bin/env python3

from gr import ref, unwrap, wrap, new_feature
import copy

def new_type(graph, name):
    type_type_feat = graph.feature('type')
    attr_type_feat = graph.feature('attribute_id')
    res = {}
    res[type_type_feat.get('name')] = name
    res[type_type_feat.get('type')] = [type_type_feat.ref('type_type')]
    res[type_type_feat.get('attrs')] = []
    return res

def new_attr(graph, name, dbtype, array=False):
    type_type_feat = graph.feature('type')
    attr_type_feat = graph.feature('attribute_id')
    res = {}
    res[attr_type_feat.get('name')] = name
    if type_type_feat:
        res[type_type_feat.get('type')] = [type_type_feat.ref('attribute_id')]
    res[attr_type_feat.get('array')] = array
    res[attr_type_feat.get('dbtype')] = dbtype
    return res

def init_link_sysem(graph):
    target_attr = new_attr(graph, 'target', 'ref')
    graph.insert(target_attr)
    target_attr[unwrap(target_attr)] = ref(target_attr)
    graph.update(target_attr)

    link_loader = new_feature(graph, 'blazeva1', 'link', '0.1')
    link_loader['target'] = ref(target_attr)
    graph.insert(link_loader)
    graph.add_loader(link_loader)

def init_type_system(graph):
    attr_id_feat = graph.feature('attribute_id', True)
    attr_name_attr = graph.get(attr_id_feat.get('name'))
    attr_dbtype_attr = graph.get(attr_id_feat.get('dbtype'))
    attr_array_attr = graph.get(attr_id_feat.get('array'))

    type_type = {}
    attr_type = {}
    name_attr = new_attr(graph, 'name', 'str')
    types_attr = new_attr(graph, 'type', 'ref')
    attrs_attr = new_attr(graph, 'attrs', 'ref', True)
    for entry in [type_type, attr_type, name_attr, types_attr, attrs_attr]:
        graph.insert(entry) # obtain ids

    type_type[unwrap(name_attr)] = 'Type'
    type_type[unwrap(types_attr)] = ref(type_type)
    type_type[unwrap(attrs_attr)] = [ref(name_attr), ref(types_attr), ref(attrs_attr)]
    graph.update(type_type)

    attr_type[unwrap(name_attr)] = 'Attr'
    attr_type[unwrap(types_attr)] = ref(type_type)
    attr_type[unwrap(attrs_attr)] = [ref(name_attr), ref(types_attr)]
    graph.update(attr_type)

    for entry in [name_attr, types_attr, attrs_attr, attr_dbtype_attr, attr_name_attr, attr_array_attr]:
        entry[unwrap(types_attr)] = ref(attr_type)
        graph.update(entry)

    loader = graph.feature('loader', True)
    #  loader_scope = graph.get(loader.get('scope'))
    #  loader_scope[unwrap(type_type)] = False
    #  graph.update(loader_scope)
    #  loader_name = graph.get(loader.get('name'))
    #  loader_name[unwrap(type_type)] = False
    #  graph.update(loader_name)
    #  loader_version = graph.get(loader.get('version'))
    #  loader_version[unwrap(type_type)] = False
    #  graph.update(loader_version)
    #  loader_type = {
        #  unwrap(name_attr): 'Loader attr',
        #  unwrap(types_attr): ref(type_type),
        #  unwrap(attrs_attr): [ref(loader_scope), ref(loader_name), ref(loader_version), ref(type_type)],
    #  }
    #  graph.insert(loader_type)

    type_type_loader = {
        loader.get('scope'): 'blazeva1',
        loader.get('name'): 'type',
        loader.get('version'): '0.1',
        'type_type': ref(type_type),
        'attr_type': ref(attr_type),
        'type': ref(types_attr),
        'name': ref(name_attr),
        'attrs': ref(attrs_attr),
    }
    graph.insert(type_type_loader)
    graph.add_loader(type_type_loader)

def init_attribute_id_system(graph):
    name_attr = {}
    attrs_attr = {}
    array_attr = {}
    dbtype_attr = {}
    for entry in [name_attr, attrs_attr, array_attr, dbtype_attr]:
        graph.insert(entry) # obtain ids

    for entry in [name_attr, attrs_attr, array_attr, dbtype_attr]:
        entry[unwrap(array_attr)] = False
        graph.update(entry)

    name_attr[unwrap(name_attr)] = 'name'
    name_attr[unwrap(dbtype_attr)] = 'str'
    attrs_attr[unwrap(name_attr)] = 'attrs'
    attrs_attr[unwrap(dbtype_attr)] = 'ref'
    attrs_attr[unwrap(array_attr)] = True
    array_attr[unwrap(name_attr)] = 'array'
    array_attr[unwrap(dbtype_attr)] = 'bool'
    dbtype_attr[unwrap(name_attr)] = 'dbtype'
    dbtype_attr[unwrap(dbtype_attr)] = 'str'
    for entry in [name_attr, attrs_attr, array_attr, dbtype_attr]:
        graph.update(entry)

    loader = graph.feature('loader', True)
    loader_scope = graph.get(loader.get('scope'))
    loader_scope[unwrap(dbtype_attr)] = 'str'
    loader_scope[unwrap(array_attr)] = False
    graph.update(loader_scope)
    loader_name = graph.get(loader.get('name'))
    loader_name[unwrap(dbtype_attr)] = 'str'
    loader_name[unwrap(array_attr)] = False
    graph.update(loader_name)
    loader_version = graph.get(loader.get('version'))
    loader_version[unwrap(dbtype_attr)] = 'str'
    loader_version[unwrap(array_attr)] = False
    graph.update(loader_version)

    attr_type_loader = {
        loader.get('scope'): 'blazeva1',
        loader.get('name'): 'attribute_id',
        loader.get('version'): '0.1',
        'name': ref(name_attr),
        'dbtype': ref(dbtype_attr),
        'array': ref(array_attr),
    }
    graph.insert(attr_type_loader)
    graph.add_loader(attr_type_loader)
