
import os
import json

#  class MemoryDB(object):

class FileDB(object):

    def __init__(self, location):
        self.location = os.path.expanduser(location)
        self.db = None
        self.load(self.location)

    def load(self, location):
        if os.path.exists(location):
            self.db = json.load(open(self.location, "r"))
        else:
            self.db = {}
        return True

    def save(self):
        try:
            json.dump(self.db, open(self.location, "w+"), indent=4)
            return True
        except:
            return False

    def delete(self):
        if os.path.exists(self.location):
            os.remove(self.location)
