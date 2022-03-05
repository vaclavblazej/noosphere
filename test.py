#!/usr/bin/env python3

import os

import gr
from gr import unwrap
import gr_types
import gr_data

test_file = '.test_tmp.json'

# == Run tests one by one ========================================================

def test():
    print('testing')
    test_file_db()
    test_basic_functionality()
    test_simple_integrity()
    test_attribute_type_system()
    test_type_system()
    test_link_system()

# == Utility functions ===========================================================

def insert_okay(graph, node):
    graph.insert(node)
    graph.remove(node)
    node.pop('id')

def insert_fails(graph, node):
    try:
        assert graph.insert(node) # fails on return
    except gr.GrError:
        pass

# == Test functions ==============================================================

def test_link_system():
    print('Operations with link system')
    graph = gr.Graph(gr_data.MemoryDB())
    graph.clear()
    gr_types.init_attribute_id_system(graph)
    gr_types.init_link_sysem(graph)
    attr_feat = graph.module('attribute_id')
    link_feat = graph.module('link')
    children_attr = gr_types.new_attr(graph, 'children', 'ref', True)
    graph.insert(children_attr)
    parent_attr = gr_types.new_attr(graph, 'parent', 'ref')
    graph.insert(parent_attr)
    children_attr = graph.get(children_attr)
    children_attr[link_feat.get('target')] = gr.ref(parent_attr)
    graph.update(children_attr)
    parent_attr = graph.get(parent_attr)
    node_id_attr = gr_types.new_attr(graph, 'node_id', 'int')
    graph.insert(node_id_attr)
    node_id_attr_id = unwrap(node_id_attr)
    assert unwrap(parent_attr[link_feat.get('target')]) == unwrap(children_attr)
    # now, build a tree
    for node_id in range(0, 6):
        graph.insert({node_id_attr_id: node_id, unwrap(children_attr): [], unwrap(parent_attr): None})
    for (to, fr) in enumerate([0, 1, 1, 1, 3]): # parent list for nodes 1..
        to += 1
        fr_node = graph.find(lambda x: node_id_attr_id in x and x[node_id_attr_id] == fr)[0]
        to_node = graph.find(lambda x: node_id_attr_id in x and x[node_id_attr_id] == to)[0]
        #  fr_node['children'].append(gr.ref(to_node)) # not needed thanks to links
        to_node[unwrap(parent_attr)] = gr.ref(fr_node)
        graph.update(to_node)
    # check that 1 has exactly 3 children
    assert len(graph.find(lambda x: node_id_attr_id in x and x[node_id_attr_id] == 1)[0][unwrap(children_attr)]) == 3
    # check that everyone has a parent
    for i in range(1, 6):
        assert graph.find(lambda x: node_id_attr_id in x and x[node_id_attr_id] == i)[0][unwrap(parent_attr)] is not None
    graph.clear()

def test_type_system():
    print('Type system integrity checking')
    graph = gr.Graph(gr_data.MemoryDB())
    graph.clear()
    gr_types.init_attribute_id_system(graph)
    gr_types.init_type_system(graph)

def test_attribute_type_system():
    print('Attribute type integrity checking')
    graph = gr.Graph(gr_data.MemoryDB())
    graph.clear()
    gr_types.init_attribute_id_system(graph)
    test_type = {}
    graph.insert(test_type)
    attrs = [
        gr_types.new_attr(graph, 'intpar', 'int', False),
        gr_types.new_attr(graph, 'strpar', 'str', False),
        gr_types.new_attr(graph, 'boolpar', 'bool', False),
        gr_types.new_attr(graph, 'floatpar', 'float', False),
        gr_types.new_attr(graph, 'refpar', 'ref', False),
        gr_types.new_attr(graph, 'arrintpar', 'int', True),
        gr_types.new_attr(graph, 'arrstrpar', 'str', True),
        gr_types.new_attr(graph, 'arrboolpar', 'bool', True),
        gr_types.new_attr(graph, 'arrfloatpar', 'float', True),
        gr_types.new_attr(graph, 'arrrefpar', 'ref', True),
    ]
    id_map = dict()
    attr_type = graph.module('attribute_id')
    for attr in attrs:
        graph.insert(attr)
        id_map[attr[attr_type.get('name')]] = unwrap(attr)
    graph.update(test_type)
    node = {}
    # okay simple attributes
    node[id_map['intpar']] = 'test text'
    insert_fails(graph, node) # wrong type
    node[id_map['intpar']] = []
    insert_fails(graph, node) # wrong array
    node[id_map['intpar']] = 1
    insert_okay(graph, node)
    node[id_map['strpar']] = 1
    insert_fails(graph, node)
    node[id_map['strpar']] = 1.2
    insert_fails(graph, node)
    node[id_map['strpar']] = {}
    insert_fails(graph, node)
    node[id_map['strpar']] = 'test'
    insert_okay(graph, node)
    node[id_map['refpar']] = 'bad'
    insert_fails(graph, node)
    node[id_map['refpar']] = gr.ref(test_type) # good reference
    insert_okay(graph, node)
    node[id_map['boolpar']] = 1
    insert_fails(graph, node)
    node[id_map['boolpar']] = False
    insert_okay(graph, node)
    node[id_map['arrstrpar']] = [2, 3]
    insert_fails(graph, node)
    node[id_map['arrstrpar']] = []
    insert_okay(graph, node)
    node[id_map['arrstrpar']] = ['a', 'b']
    insert_okay(graph, node)
    node[id_map['arrrefpar']] = [gr.ref(test_type)]
    insert_okay(graph, node)
    graph.clear()

def test_simple_integrity():
    print('Simple integrity checking')
    graph = gr.Graph(gr_data.MemoryDB())
    graph.clear()
    node = {'name': 'Test node'}
    insert_okay(graph, node)
    # okay simple attributes
    node['test'] = 1
    insert_okay(graph, node)
    node['test'] = 1.2
    insert_okay(graph, node)
    node['test'] = 'test'
    insert_okay(graph, node)
    node['test'] = {'id': 100}
    insert_okay(graph, node)
    node['test'] = []
    insert_okay(graph, node)
    node['test'] = [1, 2, 3]
    insert_okay(graph, node)
    node['test'] = ["a", "b"]
    insert_okay(graph, node)
    node['test'] = [{'id': 1}, {'id': 2}]
    insert_okay(graph, node)
    # malformed simple attributes
    node['test'] = {}
    insert_fails(graph, node) # empty struct attr
    node['test'] = {'id': 100, 'extra': False}
    insert_fails(graph, node) # extra attrs in ref
    node['test'] = [{'bad': 10}]
    insert_fails(graph, node) # must contain okay entries
    node['test'] = [[]]
    insert_fails(graph, node) # may not contain array
    node['test'] = [{}, {}]
    insert_fails(graph, node) # may not contain invalid objects
    node['test'] = ['a', 2]
    insert_fails(graph, node) # arrays must be uniformly typed
    graph.clear()

def test_basic_functionality():
    print('Graph elementary functionality')
    graph = gr.Graph(gr_data.MemoryDB())
    graph.clear()
    entity = {'name': 'test node'}
    graph.insert(entity)
    assert 'id' in entity # insert adds id to the entity
    entity_id = unwrap(entity)
    assert graph.get_id(entity_id) # the id is valid
    assert entity == graph.get(entity_id) # what you save is what you get
    entity_copy_via_get = graph.get(entity_id)
    entity_copy_via_get['is_copy'] = True
    assert entity != entity_copy_via_get # the copy from get is not the original entity
    entity_copy_via_find = graph.find(lambda x: True, [entity_id])[0]
    entity_copy_via_find['is_copy'] = True
    assert entity != entity_copy_via_find # the copy from find is not the original entity
    for i in range(0, 10):
        graph.insert({'num': i})
    assert len(graph.find(lambda x: 'num' in x and x['num'] == 5)) == 1
    assert len(graph.find(lambda x: 'num' in x and x['num'] != 5)) == 9
    entity['title'] = entity['name']
    entity.pop('name')
    graph.update(entity)
    updated_entity = graph.get(entity)
    assert 'title' in updated_entity # updates to the entity took place
    assert 'name' not in updated_entity # removing entity values is possible
    assert 'id' in updated_entity and unwrap(updated_entity) == entity_id # id does not change
    size = len(graph.find())
    graph.remove(entity_id)
    assert len(graph.find()) == size-1 # removing of an entity by id worked
    graph.remove(graph.find(lambda x: 'num' in x and x['num'] == 5)[0])
    assert len(graph.find()) == size-2 # removing of an entity by entity worked
    graph.clear()

def test_file_db():
    print('FileDB implementation')
    data = gr_data.FileDB(test_file)
    entity = {
        'val': 12,
        'str': 'string text',
        'double': 12.3,
        'arr': [1, 2, 3],
        'struct': {'arr struct': [{}, {'a':2}, {'b':3, 'c':4}]}
    }
    data.db = entity
    data.save()
    data.db = {} # clear db to check if it loads correctly
    data.load()
    # what is saved is the same as what is retrieved
    assert entity == data.db
    data.clear()
    # the file is successfully removed
    assert not os.path.exists(test_file)

# == Test invocation =============================================================

if __name__ == '__main__':
    test()
