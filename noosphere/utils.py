'''
Utility functions

Functions ref, unwrap, and wrap are made for reference work as each reference is coded as {'id': identificator} it is easier to have these functions to work with the identificator itself.
'''


def ref(reference):
    '''Given an object or a list of objects construct just a reference to them.'''
    return wrap(unwrap(reference))

def unwrap(reference):
    '''Given an one or more object or references, retrieve their ids.'''
    try:
        return [x['id'] for x in iter(reference)]
    except TypeError:
        pass
    assert 'id' in reference
    return reference['id']

def wrap(reference):
    '''Given one or more ids construct respective references.'''
    if(isinstance(reference, list)):
        return [{'id': x} for x in iter(reference)]
    return {'id': reference}
