
from noosphere import NosError
from noosphere.utils import ref, unwrap

# given an entity and its attribute return its value as an array
def get_entity_attribute_array(entity, attr_id, is_array):
    if entity is None or attr_id not in entity:
        return []
    value = entity[attr_id]
    if value is None:
        return []
    if is_array:
        return unwrap(value)
    return [unwrap(value)]

#== double-sided references ================================================

def set_other_side_of_references(self, old_entry, new_entry):
    # todo fixme - this function was originally written to fetch type from the entry type, go through its attributes and set the other side depending on what it targets; now we need no entry type; simply if attribute name is an id of a valid attribute with target property of the link module then we may set the other side of the link
    attr_feat = self.module('attribute_id')
    links_feat = self.module('link')
    if attr_feat and links_feat:
        old_attrs_ids = unwrap(self._relation_attributes_iterator(old_entry))
        new_attrs_ids = unwrap(self._relation_attributes_iterator(new_entry))
        if new_entry is not None and 'id' in new_entry:
            entry_ref = ref(new_entry)
        elif old_entry is not None and 'id' in old_entry:
            entry_ref = ref(old_entry)
        else:
            raise NosError('Double-sided reference failed as both new and old entry is None or invalid')
        for attr_id in list(set(old_attrs_ids).union(set(new_attrs_ids))):
            attr = self.get(attr_id)
            target_attr = links_feat.get('target')
            if target_attr not in attr:
                continue
            other_side_attr_ref = attr[target_attr]
            if other_side_attr_ref:
                array_par = attr_feat.get('array')
                is_array = attr[array_par]
                other_side_attr_id = unwrap(other_side_attr_ref)
                other_side_attr = self.get(other_side_attr_id)
                (inserted_node_ids, removed_node_ids) = added_removed_elements_ids(old_entry, new_entry, attr_id, is_array)
                for inserted_node_id in inserted_node_ids:
                    node = self.get(inserted_node_id)
                    if other_side_attr[array_par]:
                        node[other_side_attr_id].append(entry_ref)
                    else:
                        if other_side_attr_id in node and node[other_side_attr_id]:
                            pass # fixme - invalidate reference on the other side
                        node[other_side_attr_id] = entry_ref
                    self.data.update(node)
                for removed_node_id in removed_node_ids:
                    node = self.get(removed_node_id)
                    if other_side_attr[array_par]:
                        node[other_side_attr_id].remove(entry_ref)
                    else:
                        node[other_side_attr_id] = None
                    self.data.update(node)

#== utility functions for link module ======================================

def _relation_attributes_iterator(self, entity):
    attr_type_feat = self.module('attribute_id')
    if attr_type_feat:
        for attr_id in entity.keys():
            if self.data.is_id(attr_id):
                attr = self.get(attr_id)
                if attr_type_feat.get('dbtype') not in attr:
                    warn('attribute without dbtype: {}'.format(attr))
                elif attr[attr_type_feat.get('dbtype')] == 'ref':
                    yield attr

# compare two entries' attributes and split their differences into lists
# of new elements and old elements
def added_removed_elements_ids(old_entry, new_entry, attr_id, is_array):
    old_set = set(get_entity_attribute_array(old_entry, attr_id, is_array))
    new_set = set(get_entity_attribute_array(new_entry, attr_id, is_array))
    return (list(new_set - old_set), list(old_set - new_set))
