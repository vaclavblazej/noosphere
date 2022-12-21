'''
Various ways to save the data.
'''

import os
import json
import copy

from noosphere.identifier import AlphaNumId


class MemoryDB:
    '''
    In-memory database without persistance for testing.
    '''

    def __init__(self):
        self.orig_ids = AlphaNumId(6)
        self.ids = copy.deepcopy(self.orig_ids)
        self.clear()

    def is_id(self, entry_id):
        return self.ids.is_id(entry_id)

    def get_id(self, entry):
        if 'id' not in entry:
            return None
        assert self.is_id(entry['id'])
        return entry['id']

    def all(self):
        return [copy.deepcopy(x) for x in self.db.values()]

    def get(self, entry_id):
        if str(entry_id) not in self.db:
            return None
        return copy.deepcopy(self.db[str(entry_id)])

    def insert(self, entry):
        assert 'id' not in entry
        entry['id'] = self.ids.new_id(self)
        self.db[str(self.get_id(entry))] = copy.deepcopy(entry)
        self.save()

    def update(self, entry):
        self.db[str(self.get_id(entry))] = copy.deepcopy(entry)
        self.save()

    def remove(self, entry_id):
        nodes = self.db
        nodes.pop(str(entry_id))
        self.db = nodes
        self.save()

    def load(self):
        pass

    def save(self):
        pass

    def clear(self):
        self.ids = copy.deepcopy(self.orig_ids)
        self.db = {}


class FileDB(MemoryDB):
    '''
    File database without persistance for testing.
    '''

    def __init__(self, location):
        super().__init__()
        self.location = os.path.expanduser(location)
        self.db = None
        self.load()

    def load(self):
        if os.path.exists(self.location):
            with open(self.location, "r", encoding='UTF-8') as file:
                res = json.load(file)
                self.db = res['nodes']
                self.ids.load(res['ids'])
        else:
            self.clear()
            self.save()

    def save(self):
        res = {'nodes': self.db, 'ids': self.ids.save()}
        with open(self.location, "w+", encoding='UTF-8') as file:
            json.dump(res, file, indent=4)

    def clear(self):
        super().clear()
        if os.path.exists(self.location):
            os.remove(self.location)
