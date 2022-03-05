*A way to work with data without worying about details.*

Note that this project is still [work in progress](./docs/work.md); help is appreciated.

# todo

* database of problems and solutions

# Graph data storage

This projects aims to make an universal system to work with data.

Concisely said, the data is presented as flat json objects which represent entries.
Attributes can hold primitives, arrays, or references to other entries.

```json
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
```

You may work with the data using any compatible system.
One compatible rudimentary system is available within this repository.

The main difference from classical data storages (files or databases) is that this is an intermediate format.
Its implementation may use files or databases to implement the data storage but working with it does not depend on the storage.

The format is general enough that it can convey information to the storage system.
This allows additional functionality to be added to the system via modules.
The data itself configure which modules are activated and their settings.

See [in-depth explanation of this system](./docs/system.md).

## Modules

Modules of this interpreter may be activated by the read entries.
New module may be added by `add_module`.

See the [Modules documentation](./docs/modules.md).

## Projects

There are several small projects which present how to use this system.
They are in a separate repository [gr-web](https://github.com/vaclavblazej/gr-web) and use the `api.py` rest interface implementation.
