System basics
=============

Data representation
-------------------

How complicated can data be?
One entry can be a simple list of numbers or a complex nested structure of interlinked information.
Many simple entries may be represented in a table but for more complex ones we need references that model their connections.

To represent complexly interlinked data we opt for a flat json structure.
Every object is identified with its ``id`` attribute.
One object can reference another with a structure as ``{ "id": "<val>" }``.
Attributes can hold primitives, arrays, or references to other entries.
Arrays cannot contain further arrays and entries cannot contain substructures, this means no nesting is possible and we get a flat database structure.
This does not hinder expressibility because we can reference other entries.

::

    {
        "id": "!QS48j5",
        "name": "Entry example",
        "version": "0.1",
        "few_primes": [2, 3, 5, 7, 11, 13, 17, 19],
        "reference": { "id": "!0cGTHT" },
        "more_references": [
            { "id": "!f3UGJA" },
            { "id": "!4ImlZA" },
            { "id": "!bWda7k" }
        ]
    }

Attributes can contain one of the following primitive types:

* ``integer`` -- standard numbers such as 0, 1, 4, -2, etc.
* ``decimal number`` -- like 1.0, 0.5, -3.1415, etc.
* ``string`` -- sequence of characters
* ``boolean`` -- contains either true or false
* ``reference`` -- points to another entry

Additionally, attributes can contain lists of values of the same primitive type.
Lists cannot be nested.

.. note::

   Noosphere is more of a concept than an implementation.
   The flat structure is the model we choose to utilize as it is quite simple but also powerful.
   Other implementations of the system will choose a data model that better suits their needs.

Meta information and modules
----------------------------

Data by itself may represent many things and to make them concrete we take advantage of e.g. typing and linking.
Similarly, we can reason about the database as whole.
The database can use auxiliary systems but to use them correctly we need to know which database does and which does not use such features.
We call such features **modules**.

To load modules we need to set a data entry that can be read when we wish to use the database.
This can be reminiscent to grub which loads operating system on boot, or the main function in a codebase.
We opt to use the entry which is identified with id ``!0``.
In there, you will find a single parameter named ``0`` that holds a list of references.
It should look like this::

    {
        "id": "!0",
        "0": [
            { "id": "!f3UGJA" },
            { "id": "!4ImlZA" },
            { "id": "!bWda7k" }
        ]
    }

Parameter names
---------------

The data by itself have no meaning -- numbers like ``4`` tells nothing until we have some context.
We may gather some notion from the attribute (e.g. ``age``), but still, this does not have nearly enough expressive power.
As first of the *modules* we propose this needs to be tackled by having *ids* as parameter names to have special meaning -- that of parameter descriptors.
They give context to the parameter such as name, type, and its restrictions.

