
import os
import json
import copy

class DbError(RuntimeError):
    pass

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


class MemoryDB:
    pass

class FileDB:

    def __init__(self, location):
        self.location = os.path.expanduser(location)
        self.db = None
        self.ids = IntId()
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
        self.ids = IntId()
        self.db = {}
        if os.path.exists(self.location):
            os.remove(self.location)
