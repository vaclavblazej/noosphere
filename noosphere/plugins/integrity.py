'''
Data integrity checker for a flat structure database.


'''

from noosphere import NosError

def retrieve_value_type(attr_value):
    if attr_value is None:
        return 'none'
    if isinstance(attr_value, list):
        return 'arr'
    if isinstance(attr_value, str):
        return 'str'
    if isinstance(attr_value, bool):
        return 'bool'
    if isinstance(attr_value, int):
        return 'int'
    if isinstance(attr_value, float):
        return 'float'
    if 'id' in attr_value and len(attr_value.keys()) == 1:
        return 'ref'
    raise NosError('unrecognized data type of {}'.format(attr_value))

def valid_entry(self, entry):
    attr_type_feat = self.module('attribute_id')
    for attr_id in entry.keys():
        if attr_type_feat:
            if attr_id == attr_type_feat.get('dbtype'):
                if entry[attr_id] not in ['str', 'int', 'float', 'ref', 'bool', None]:
                    raise NosError('dbtype has invalid value {}'.format(entry[attr_id]))
            elif self.data.is_id(attr_id):
                attr_type = self.get(attr_id)
                dbtype = attr_type_feat.get('dbtype')
                array = attr_type_feat.get('array')
                if dbtype not in attr_type or array not in attr_type:
                    warn('attribute {} used in an entry {} is invalid attribute type as it does not contain either "dbtype" or "array" attribute'.format(attr_type, entry))
                else:
                    self.valid_attribute(entry[attr_id], attr_type[dbtype], attr_type[array])
                    continue
            elif attr_id != 'id' and not ('id' in entry and entry['id'] == '!0'):
                loader = self.module('loader', True)
                name_id = loader.get('name')
                if name_id not in entry: # means that this is not a loader
                    warn('although attribute typing is enabled an entry was inserted with plain attribute name "{}"'.format(attr_id))
                    warn('entry: {}'.format(entry))
        self.valid_attribute(entry[attr_id], None, None)

def valid_attribute(self, attr_value, assumed_type, assumed_array):
    attr_type = retrieve_value_type(attr_value)
    is_array = (attr_type == 'arr')
    if assumed_array is not None:
        if is_array and not assumed_array:
            raise NosError('type is array but it should not be {}'.format(attr_value))
        if not is_array and assumed_array:
            raise NosError('type is not array but it should be {}'.format(attr_value))
    if is_array:
        types = list(filter(lambda x: x is not None, map(retrieve_value_type, attr_value)))
        for val in types:
            if val == 'arr':
                raise NosError('array may not contain another array')
            if types[0] != val:
                raise NosError('array has two different types; there are elements of types {} and {}'.format(types[0], val))
        if len(attr_value) != 0:
            attr_type = retrieve_value_type(attr_value[0])
        else:
            attr_type = 'none'
    if attr_type != 'none' and assumed_type is not None and assumed_type != attr_type:
        raise NosError('data inconsistency detected; value {} of type {} should have been {}'.format(attr_value, attr_type, assumed_type))
