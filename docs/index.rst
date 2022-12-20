Documentation
=============

.. warning::

   This documentation is for a project which is not yet fully implemented.
   You could say it uses *documentation driven development*.
   The aim is to keep this documentation as accurate as possible with the final version of the project as the development progresses.

Noosphere provides a way to work with data without worrying about details.
Even though the main body of this project is theoretical we also provide an implementation.

Main features:

* **Expressive data representation:** The structure allows us to save complex data in a simple way.
* **Independent:** The system is designed to be independent of any specific format or language.
* **Modular:** Capabilities like *typing* can be added through modules.

You may quickstart the system using the following commands.
Consider reading the docs further if the system seems mysterious.

::

    pip3 install noosphere
    nos init database.json
    nos web database.json

What follows is a comprehensive introduction into noosphere.

.. toctree::
   :maxdepth: 2

   intro/start
   system/introduction
   modules/introduction

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
   :maxdepth: 1
   :caption: Extras

   installation
   changelog
   glossary
