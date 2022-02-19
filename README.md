# Todos

## Next todos

* consistency checking
* change types to traits so that any entity may have more than one
* change parameters to ids
* types may be inherited
* consider how to make extensible primitive types - map coordinates, link, etc.
    * they should have a structure, as json is subset of strings
* consider adding any type
* versioning - entries are backed-up automatically and it is easy to retrieve entries from a given time
* namespaces - every node has namespace of 'where it belongs'
* features - system checks if it implements the given features
    * system says which primitive types it supports

## Done

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
