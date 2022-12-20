Task list
=========

In this example, we implement a rudimentary **task-list** using noosphere.

As a first step, we write down an example entries into ``temp.json`` file::

    {
        "tasks": [
            {
                "title": "Learn noosphere",
                "created": "2022-11-30 20:12",
                "completed": "2022-12-02 14:03",
                "deadline": "2022-12-07",
                "tags": ["learning"]
            },
            {
                "title": "Meditate",
                "created": "2022-11-30 20:14",
                "completed": null,
                "deadline": "2022-12-02",
                "tags": ["health", "important"]
            }
        ]
    }

We shall use structure recognition to infer what we want to create.
In this light, if we made a template that covers more of the possible results we would get a nicer result.
Initiate the system into file ``database.json`` while using the template we just created::

    nos init --template temp.json database.json

Now, we may start an interactive web interpreter with::

    nos web database.json

The interface we get may not be the best one for the task, but still, we should be able to create, edit, and delete tasks.
