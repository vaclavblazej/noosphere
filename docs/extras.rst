Extras
======

Modules
-------

Modules of this interpreter may be activated by the read entries.
New module may be added by `add_module`.

See the `Modules documentation <./docs/modules.md>`_.

Setup and run the backend
-------------------------

The backend is coded with flask and is configured to run with uwsgi.
Setup inspired from post `How To Serve Flask Applications with uWSGI and Nginx on Ubuntu 20.04 <https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-20-04>`_.

The initial setup was made with the following commands.

::

    sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
    sudo apt install python3-venv
    python3 -m venv venv
    source venv/bin/activate
    pip3 install wheel
    pip3 install uwsgi flask

Run the server manually with the following commands.

::

    source venv/bin/activate
    uwsgi config.ini
    deactivate

Structure
=========


Identification of entries
-------------------------

The simplicity of the flat structure implies that if we want to save some complex structure, we need to create references among entries.
To do so an attribute named `id` is used.
A specific value of an `id` is irrelevant, it should be unique for each entry.

A reference is the object with only `id` attribute so a reference to the entry of the above example would be `{"id": "!QS48j5"}`.

Retrieval and work with entries
-------------------------------

The entries are returned via *copy*.
Race conditions could be prevented with *consistency* module.

Implementation
--------------

We use `python3` to make a prototype of the system and its more effective reimplementation is expected.
The data is the main way which dictates how it should be interated with so once a sufficient level of abstraction is reached the underlying system will be only a matter of tradeoffs, not functionality.

Our implementation uses six alphanumerals with `!` symbol at the beginning, e.g., `!f3UGJA`, `!4ImlZA`, or `!bWda7k`.
This way of doing ids is easily replacable.
