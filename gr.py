#!/usr/bin/env python3

import datetime
import json
import os

def get_id(entry):
    if 'id' in entry_or_id:
        return entry_or_id['id']
    else:
        return entry_or_id

def added_removed_elements(old, new):
    old_set = set(old)
    new_set = set(new)
    return (new_set - old_set, old_set - new_set)

class FileDB(object):
    def __init__(self, location):
        self.location = os.path.expanduser(location)
        self.load(self.location)

    def load(self, location):
        if os.path.exists(location):
            self._load()
        else:
            self._resetdb()
        return True

    def save(self):
        return self._dumpdb()

    def _load(self):
        self.db = json.load(open(self.location, "r"))

    def _dumpdb(self):
        try:
            json.dump(self.db, open(self.location, "w+"), indent=4)
            return True
        except:
            return False

    def _resetdb(self):
        self.db={
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
        except Exception as e:
            print("[X] Error Saving Values to Database : " + str(e))
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

    # create a new entry and assign a new id to the node
    def add_node(self, new_entry):
        # assert('type' in new_entry and new_entry['type'] or new)
        assert('id' not in new_entry)
        new_entry['id'] = self.db['last_node_id']
        self._set('last_node_id', self._get('last_node_id') + 1)
        self.set_node(new_entry)

    def set_node(self, new_entry):
        assert('id' in new_entry and new_entry['id'] != None)
        old_entry = self.get_node(new_entry['id'])
        if old_entry:
            assert(old_entry['type'] == new_entry['type']) # not allowed, remove and add instead
        else:
            old_entry = {}
        if 'type' in new_entry and new_entry['type'] != None:
            node_type = self.get_node(new_entry['type'])
            for attr_id in node_type['attrs']:
                attr = self.get_node(attr_id)
                if attr['dbtype']['value'] == 'relation':
                    attr_name = attr['name']
                    is_array = 'array' in attr['dbtype'] and attr['dbtype']['array']
                    change = ([], [])
                    if is_array:
                        change = added_removed_elements(new_entry[attr_name], old_entry[attr_name] or {})
                    elif new_entry[attr_name] != old_entry[attr_name]:
                        change = ([new_entry[attr_name]], [old_entry[attr_name]])
                    (new, rem) = change
                    for n in new: self.add_edge(new_entry['id'], n)
                    for r in rem: self.rem_edge(new_entry['id'], r)

        self.db['nodes'][new_entry['id']] = new_entry

    def rem_node(self, entry_or_id):
        rem_id = get_id(entry_or_id)
        nodes = self._get('nodes')
        del nodes[rem_id]
        self._set('nodes', nodes)
        (fr, to) = self.get_edges(rem_id)
        for f in fr: self.rem_edge(f)
        for t in to: self.rem_edge(t)

    def get_node(self, node_id):
        nodes = self._get('nodes')
        if node_id in nodes:
            node = nodes[node_id]
        else:
            node = None
        return node

    def get_nodes(self, node_ids):
        nodes = self._get('nodes')
        return map(node_ids, lambda ID : nodes[ID])

    def find_nodes(self, typename):
        return filter(self._get('nodes'), lambda N : N['type']==typename)

    def add_edge(self, fr, to):
        pass


# ==== type system =================

class Type(dict):
    def __init__(self, name, desc, typeid = None):
        self['name'] = name
        self['desc'] = desc
        self['type'] = typeid
        self['attrs'] = []

class Attr(dict):
    def __init__(self, name, typeid, dbtype):
        self['name'] = name
        self['type'] = typeid
        self['dbtype'] = dbtype

class Member(dict):
    def __init__(self, tp, attr=None):
        self['type'] = tp['id']
        if attr: self['attr'] = attr['id']

class EdgeType(dict):
    def __init__(self, d, fr, to):
        d.add_node(fr)
        d.add_node(to)
        self['from'] = fr
        self['to'] = to

class Edge(dict):
    def __init__(self, fr, to, edge_type):
        self['type'] = edge_type
        self['from'] = fr
        self['to'] = to

def init_type_system(d):
    type_type = Type('Type', 'Each node in the database should have one attribute called "type" which defines its structure. When the type of a node is THIS node then the node itself defines a new structure. This is achieved by connection with nodes of type (nodeid) 1 via attribute "attrs".') 
    d.add_node(type_type)
    type_type['type'] = type_type['id']

    attr_type = Type('Attr', 'Each node N which has "type" set to 0 defines a node structure. Every other node having "type" set to N should contain all parameters which are contained in attribute "attrs" in N. Each attribute contains "name" which says the attribyte description string, and "dbtype" which says what can be saved to the attribute.', type_type['id'])
    d.add_node(attr_type)

    member_type = Type('Member', 'Nodes of this type direct to an attribute of a given type. This is needed because one attribute may be used in multiple types.', type_type['id'])
    d.add_node(member_type)

    edge_type = Type('EdgeType', 'Defines types of nodes which represent connections among other two nodes. The API converts this data automatically from and to references. One way connections should leave attr field empty.', type_type['id'])
    d.add_node(edge_type)

    name_attr = Attr('name', attr_type['id'], {'value': 'string'})
    type_attr = Attr('type', attr_type['id'], {'value': 'relation'})
    attr_attr = Attr('attr', attr_type['id'], {'value': 'relation'})
    desc_attr = Attr('desc', attr_type['id'], {'value': 'string'})
    attrs_attr = Attr('attrs', attr_type['id'], {'value': 'relation', 'array': True})
    dbtype_attr = Attr('dbtype', attr_type['id'], {'value': 'dbtype'})
    from_attr = Attr('from', attr_type['id'], {'value': 'relation'})
    to_attr = Attr('to', attr_type['id'], {'value': 'relation'})
    d.add_node(name_attr)
    d.add_node(type_attr)
    d.add_node(attr_attr)
    d.add_node(desc_attr)
    d.add_node(attrs_attr)
    d.add_node(dbtype_attr)
    d.add_node(from_attr)
    d.add_node(to_attr)

    def register_edge_type(et):
        d.add_node(et)
        tp = d.get_node(et['from']['type'])
        attr = d.get_node(et['from']['attr'])
        print(tp)
        print(attr)
    register_edge_type(EdgeType(d, Member(type_type, type_attr), Member(type_type)))
    # d.add_node(EdgeType(d, Member(type_type, attrs_attr), Member(attr_type)))
    # d.add_node(EdgeType(d, Member(member_type, attr_type), Member(attr_type)))
    # d.add_node(EdgeType(d, Member(edge_type, from_attr), Member(member_type)))
    # d.add_node(EdgeType(d, Member(edge_type, to_attr), Member(member_type)))

    type_type['attrs'] = [name_attr['id'], type_attr['id'], desc_attr['id'], attrs_attr['id']]
    attr_type['attrs'] = [name_attr['id'], type_attr['id'], dbtype_attr['id']]
    member_type['attrs'] = [type_attr['id'], attr_attr['id']]
    edge_type['attrs'] = [from_attr['id'], to_attr['id']]
    d.set_node(type_type)
    d.set_node(attr_type)
    d.set_node(member_type)
    d.set_node(edge_type)

# ==== main ========================

def main():
    d = FileDB('test')
    d._resetdb()
    init_type_system(d)
    d.save()

if __name__ == '__main__':
    main()

