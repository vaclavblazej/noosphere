'''
Managing identifiers within a database.
'''

import random

def _rand_alphanum():
    rnd = random.randrange(0, 2*26+10)
    if(rnd < 10):
        return str(rnd)
    rnd -= 10
    if(rnd < 26):
        return chr(ord('a') + rnd)
    rnd -= 26
    return chr(ord('A') + rnd)


class AlphaNumId:
    '''
    Saves ID as an alphanumeric string value of given length.
    It always starts with '!' character.
    '''

    def __init__(self, length):
        self.length = length

    def load(self, saved_sata):
        self.length = saved_sata['ids_len']

    def save(self):
        return {'ids_len': self.length}

    def is_id(self, entry_id):
        if isinstance(entry_id, str):
            if entry_id == '!0': # exception for the root loader
                return True
            return entry_id[0] == '!' and entry_id[1:].isalnum() and len(entry_id) == self.length+1

    def new_id(self, db):
        while True:
            new_id = [_rand_alphanum() for _ in range(self.length)]
            if(db.get(new_id) is None):
                return '!' + new_id


class IntId:
    '''
    Saves ID as an integer.
    '''

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
            res_id += 1
        self.last_id = res_id + 1
        return res_id
