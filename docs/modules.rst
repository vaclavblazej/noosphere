# Available modules

## Module Loader

The system should load modules using a generalized way.
We call this system *loader*.

As the loader is also a module it creates itself and data it needs on database initialization.
(How to make cooperation with other loaders possible needs investigation.)

The main entry which contains data necessary for loaders has id `!0`.
Inside this entry we find an attribute `modules` which contains list of references to data of respective modules.

```json
"!bWda7k": {
    "!0cGTHT": "scope_name",
    "!QS48j5": "module_name",
    "!lp13Ut": 24,
    "type_type": { "id": "!hHSi5e" },
    "attr_type": { "id": "!Kxf13S" },
    "type": { "id": "!xcDTWj" },
    "name": { "id": "!goaN2C" },
    "attrs": { "id": "!rTxhPH" },
    "id": "!bWda7k"
}
```

## Attribute Id

Instead of naming attributes by strings we name them by ids to allow attribute typing.
See an example of an entry.

```json
"!bWda7k": {
    "!0cGTHT": 2,
    "!QS48j5": "example_name",
    "!lp13Ut": { "id": "!hHSi5e" },
    "id": "!bWda7k"
}
```

The id points to an entry which describes type of the attribute.
Attribute type entry contains 

## Types

Entries are allowed to have a type defined.
The type lists attributes should be included in the entry.


# Other modules which are not implemented (yet)

## Parser

A general grammar format should be defined.
Then, a general parser and writer can be implemented.
With these modules, the program can read and write general data-formats.

## Internal Programming Language

At first stage, a language similar to assembly should be implemented.
The source code is saved in the database entries.
The code is interpreted.

## Module Compatibility
