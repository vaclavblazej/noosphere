#!/usr/bin/env python3

import os

import gr
import gr_types
import gr_data

test_file = '.test_tmp.json'

def test():
    print('testing')
    file_db_tests()
    simple_graph()
    simple_integrity()
    type_integrity()
    #  references()

def insert_okay(graph, node):
    graph.insert(node)
    graph.delete(node)
    node.pop('id')

def insert_fails(graph, node):
    try:
        assert graph.insert(node) # fails on return
    except gr.GrError:
        node.pop('id')


def references():
    print('Operations with references')
    graph = gr.Graph(gr_data.FileDB(test_file))
    graph.reset()
    gr_types.init_type_system(graph)
    for node in graph.find():
        assert node['type'] is not None
    tree_node_type = gr_types.Type('Test', 'almost empty desc')
    graph.insert(tree_node_type)
    type_node = graph.find(lambda x:x['name']=='Type')[0]
    # the type sets itself correctly
    assert tree_node_type['type']['id'] == type_node['id']
    # the information propagates to the other side of the relation
    assert tree_node_type['id'] in gr.unwrap(type_node['rev_types'])
    children_attr = gr_types.Attr('children', 'ref', True)
    graph.insert(children_attr)
    parent_attr = gr_types.Attr('parent', 'ref')
    graph.insert(parent_attr)
    tree_node_type['attrs'] = gr.ref([children_attr, parent_attr])
    graph.update(tree_node_type)
    children_attr = graph.get(children_attr)
    children_attr['target'] = gr.ref(parent_attr)
    graph.update(children_attr)
    parent_attr = graph.get(parent_attr)
    # custom types propagate targets
    assert parent_attr['target']['id'] == children_attr['id']

    # now, build a tree
    for node_id in range(0, 6):
        graph.insert({'type': gr.ref(tree_node_type), 'node_id': node_id, 'children': [], 'parent': None})
    for (to, fr) in enumerate([0, 1, 1, 1, 3]): # parent list for nodes 1..
        to += 1
        fr_node = graph.find(lambda x: 'node_id' in x and x['node_id'] == fr)[0]
        to_node = graph.find(lambda x: 'node_id' in x and x['node_id'] == to)[0]
        #  fr_node['children'].append(gr.ref(to_node))
        to_node['parent'] = gr.ref(fr_node)
        graph.update(to_node)
    # check that 1 has exactly 3 children
    assert len(graph.find(lambda x: 'node_id' in x and x['node_id'] == 1)[0]['children']) == 3
    # check that everyone has a parent
    for i in range(1, 6):
        print(graph.find(lambda x: 'node_id' in x and x['node_id'] == i)[0])
        assert graph.find(lambda x: 'node_id' in x and x['node_id'] == i)[0]['parent'] is not None
    #  graph.data.delete()

def type_integrity():
    print('Type integrity checking')
    graph = gr.Graph(gr_data.FileDB(test_file))
    graph.reset()
    gr_types.init_type_system(graph)
    test_type = gr_types.Type('Test Type', 'test desc')
    graph.insert(test_type)
    attrs = [
        gr_types.Attr('intpar', 'int', False),
        gr_types.Attr('strpar', 'str', False),
        gr_types.Attr('boolpar', 'bool', False),
        gr_types.Attr('floatpar', 'float', False),
        gr_types.Attr('refpar', 'ref', False),
        gr_types.Attr('arrintpar', 'int', True),
        gr_types.Attr('arrstrpar', 'str', True),
        gr_types.Attr('arrboolpar', 'bool', True),
        gr_types.Attr('arrfloatpar', 'float', True),
        gr_types.Attr('arrrefpar', 'ref', True),
    ]
    for attr in attrs:
        graph.insert(attr)
        test_type['attrs'].append(gr.ref(attr))
        graph.update(test_type)
    node = gr_types.Type('Test', 'test description')
    # okay simple attributes
    node['intpar'] = 1
    insert_okay(graph, node)
    # todo here - continue testing
    #  node['intpar'] = 'test text'
    #  insert_fails(graph, node)
    #  node['test'] = 1.2
    #  insert_okay(graph, node)
    #  node['test'] = 'test'
    #  insert_okay(graph, node)
    #  node['test'] = {'id': 100}
    #  insert_okay(graph, node)
    #  node['test'] = []
    #  insert_okay(graph, node)
    #  node['test'] = [1, 2, 3]
    #  insert_okay(graph, node)
    #  node['test'] = ["a", "b"]
    #  insert_okay(graph, node)
    #  node['test'] = [{'id': 1}, {'id': 2}]
    #  insert_okay(graph, node)
    # malformed simple attributes
    #  node['test'] = {}
    #  insert_fails(graph, node) # empty struct attr
    #  node['test'] = {'id': 100, 'extra': False}
    #  insert_fails(graph, node) # extra attrs in ref
    #  node['test'] = [{'bad': 10}]
    #  insert_fails(graph, node) # must contain okay entries
    #  node['test'] = [[]]
    #  insert_fails(graph, node) # may not contain array
    #  node['test'] = [{}, {}]
    #  insert_fails(graph, node) # may not contain invalid objects
    #  node['test'] = ['a', 2]
    #  insert_fails(graph, node) # arrays must be uniformly typed

def simple_integrity():
    print('Simple integrity checking')
    graph = gr.Graph(gr_data.FileDB(test_file))
    graph.reset()
    gr_types.init_type_system(graph)
    node = gr_types.Type('Test', 'test description')
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

def simple_graph():
    print('Graph elementary functionality')
    graph = gr.Graph(gr_data.FileDB(test_file))
    graph.reset()
    entity = {'name': 'test node'}
    graph.insert(entity)
    assert 'id' in entity # insert adds id to the entity
    entity_id = entity['id']
    assert gr.is_id(entity_id) # the id is valid
    entity_copy = graph.get(entity_id)
    assert entity == entity_copy # what you save is what you get
    entity_copy['is_copy'] = True
    assert entity != entity_copy # the copy is not the original entity
    for i in range(0, 10):
        graph.insert({'num': i})
    assert len(graph.find()) == 11 # find returns all by default
    assert len(graph.find(lambda x: 'num' in x and x['num'] == 5)) == 1
    assert len(graph.find(lambda x: 'num' not in x)) == 1
    entity['title'] = entity['name']
    entity.pop('name')
    graph.update(entity)
    updated_entity = graph.get(entity)
    assert 'title' in updated_entity # updates to the entity took place
    assert 'name' not in updated_entity # removing entity values is possible
    assert 'id' in updated_entity and updated_entity['id'] == entity_id # id does not change
    graph.delete(entity_id)
    assert len(graph.find()) == 10 # removing of an entity by id worked
    graph.delete(graph.find(lambda x: 'num' in x and x['num'] == 5)[0])
    assert len(graph.find()) == 9 # removing of an entity by entity worked
    graph.data.delete()

def file_db_tests():
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
    data.load(test_file)
    # what is saved is the same as what is retrieved
    assert entity == data.db
    data.delete()
    # the file is successfully removed
    assert not os.path.exists(test_file)

if __name__ == '__main__':
    test()
