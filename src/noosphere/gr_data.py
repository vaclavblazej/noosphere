import os
import json
import copy
import random

class DbError(RuntimeError):
    pass

# saves id as an alphanumeric string values of given length
# always starts with '!' character
class AlphaNumId:
    def __init__(self, length):
        self.length = length #todo utilize length
    def load(self, saved_sata):
        self.length = saved_sata['ids_len']
    def save(self):
        return {'ids_len': self.length}
    def is_id(self, entry_id):
        if isinstance(entry_id, str):
            if entry_id == '!0': # root loader
                return True
            return entry_id[0] == '!' and entry_id[1:].isalnum() and len(entry_id) == self.length+1;
    def _next_alphanum(self):
        rnd = random.randrange(0, 2*26+10)
        if(rnd < 10):
            return str(rnd)
        rnd -= 10
        if(rnd < 26):
            return chr(ord('a') + rnd)
        rnd -= 26
        return chr(ord('A') + rnd)
    def new_id(self, db):
        while True:
            new_id = ''
            for i in range(self.length):
                new_id += self._next_alphanum()
            if(db.get(new_id) is None):
                return '!' + new_id


# saves id as a normal int
class IntId:
    def __init__(self):
        self.last_id = 100
    def load(self, saved_sata):
        self.last_id = saved_sata['last_id']
    def save(self):
        return {'last_id': self.last_id}
    def is_id(self, entry_id):
        return isinstance(entry_id, int)
    def new_id(self, db):
        res_id = self.last_id
        if db.get(res_id) is not None:
            raise DbError('new id is not unique')
        self.last_id += 1
        return res_id


# in-memory database without persistance for testing
class MemoryDB:
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
        return list(map(copy.deepcopy, self.db.values()))

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

class FileDB:

    def __init__(self, location):
        self.location = os.path.expanduser(location)
        self.db = None
        self.orig_ids = AlphaNumId(6) # should not be a list because of ref, wrap, unwrap
        self.ids = copy.deepcopy(self.orig_ids)
        self.load()

    def is_id(self, entry_id):
        return self.ids.is_id(entry_id)

    def get_id(self, entry):
        if 'id' not in entry:
            return None
        assert self.is_id(entry['id'])
        return entry['id']

    def all(self):
        return list(map(copy.deepcopy, self.db.values()))

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
        if os.path.exists(self.location):
            res = json.load(open(self.location, "r"))
            self.db = res['nodes']
            self.ids.load(res['ids'])
        else:
            self.clear()
            self.save()
            #  raise DbError('bad load, file {} does not exist'.format(self.location))

    def save(self):
        #  try:
        res = {'nodes': self.db, 'ids': self.ids.save()}
        json.dump(res, open(self.location, "w+"), indent=4)
        #  except:
            #  raise 

    def clear(self):
        self.ids = copy.deepcopy(self.orig_ids)
        self.db = {}
        if os.path.exists(self.location):
            os.remove(self.location)
