# Todos

## Next todos

* change types so that any entity may have more than one
* write the documentation and make it more structured
* check that type contains the attributes - feature type_type
* consistency checking with versions in nodes - feature consistency
* types may be composed via their parameter super[]
* consider how to make extensible primitive types - map coordinates, link, etc.
    * they should have a structure, as json is subset of strings
* consider adding 'any' type which is parent of all types
* versioning - entries are backed-up automatically and it is easy to retrieve entries from a given time
* namespaces - every node has namespace of 'where it belongs'

## Done

* split type system into attr_type and type_type
* features - system checks if it implements given feature
* change parameters to ids
* change ids from int to alphanumeric
* finish type integrity checking

# Current features

todo

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
