# Todos

## Next todos

* consistency checking with versions in nodes - feature consistency
* check that type contains the attributes - feature type_type
* change types to traits so that any entity may have more than one
* types may be inherited
* consider how to make extensible primitive types - map coordinates, link, etc.
    * they should have a structure, as json is subset of strings
* consider adding 'any' type
* versioning - entries are backed-up automatically and it is easy to retrieve entries from a given time
* namespaces - every node has namespace of 'where it belongs'

## Done

* features - system checks if it implements the given features
* split type system into attr_type and type_type
* change parameters to ids
* change ids from int to alphanumeric
* finish type integrity checking

# Possible uses

* writing logical explanatory texts
    * node based - each chunk of text is a node
    * groupable nodes - nodes can be grouped into a node which can contain linear order over them (tree of nodes)
    * linkable nodes - nodes cacn refer to each other
    * checkable of consistency - one can write programical checks of consistency over the links, etc.
* todo list
    * nodes with todos
    * can be listed
    * can be marked as done
    * with deadline
* data structures
    * implementation of *fast* structures within the structure
* analysis of proofs
