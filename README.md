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

## Setup and run the backend

The backend is coded with flask and is configured to run with uwsgi.
Setup inspired from post [How To Serve Flask Applications with uWSGI and Nginx on Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-20-04).

The initial setup was made with the following commands.
```
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
pip3 install wheel
pip3 install uwsgi flask
```

Run the server manually with the following commands.
```
source venv/bin/activate
uwsgi config.ini
deactivate
```
