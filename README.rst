Refer to the `Documentation <http://noosphere.readthedocs.io/>`_ for usage, explanation of concepts, and code documentation.

.. image:: https://readthedocs.org/projects/noosphere/badge/?version=latest
    :target: https://noosphere.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Contrary to documentation, this document describes information for Noosphere developers.

Development of this project
---------------------------

* We are trying to adhere to `The Hitchhiker's Guide to Python <https://docs.python-guide.org/>`_.
* To raise an issue, please use `Github Issues <https://github.com/vaclavblazej/noosphere/issues/new>`_.

Todos
-----

* write basic documentation and make it more structured
* check that type contains the attributes - type_type module
* consistency checking with versions in nodes - consistency module
* types may be composed via their parameter super[]
* consider how to make extensible primitive types - map coordinates, link, etc.
    * they should have a structure, as json is subset of strings
* consider adding 'any' type which is parent of all types
* namespaces - every node has namespace of 'where it belongs'
