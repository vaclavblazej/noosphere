# Structure

The data is saved in a flat json-like format.
This means that each entry contains many string-named attributes.
Each attribute contains a value.
See an example.

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

Attributes can contain one of the following primitive types.

* integer - standard numbers such as 0, 1, 4, -2, etc.
* decimal number - like 1.0, 0.5, -3.1415, etc.
* string - sequence of characters
* boolean - contains either true or false
* reference - points to another entry

Additionally, attributes can contain lists of values of the same primitive type.
Lists may not be nested.

# Identification of entries

The simplicity of the flat structure implies that if we want to save some complex structure, we need to create references among entries.
To do so an attribute named `id` is used.
A specific value of an `id` is irrelevant, it should be unique for each entry.

A reference is the object with only `id` attribute so a reference to the entry of the above example would be `{"id": "!QS48j5"}`.

# Retrieval and work with entries

The entries are returned via *copy*.
Race conditions could be prevented with *consistency* module.

# Implementation

We use `python3` to make a prototype of the system and its more effective reimplementation is expected.
The data is the main way which dictates how it should be interated with so once a sufficient level of abstraction is reached the underlying system will be only a matter of tradeoffs, not functionality.

Our implementation uses six alphanumerals with `!` symbol at the beginning, e.g., `!f3UGJA`, `!4ImlZA`, or `!bWda7k`.
This way of doing ids is easily replacable.

# FAQ

## Why are lists allowed in the flat structure?

Lists could be simulated with entries, however, there is a balance to strike between ease of use and expressability.
In a way, lists can be thought of as a sugar syntax for some underlying structure.
More complex structures should be also done in the system (e.g. set), but it is yet unclear whether they should be available by default or added with modules.
If modules are used then complex primitive types are probably defined within the entries, but if they are checked and worked with, then they are not hardcoded in the module.
This would mean necessity of gds inner programming language, which is quite far from being implemented.

# Why are entries returned by a copy?

If a reference is returned, then all the references point to the same object and any change is immediately propagated -- this is quite hard to implement

If a copy is returned, then different copies of the value can be changed at the same time which may result in inconsistencies -- this is however checkable.
This promotes locality of use of the fetched values, which is a good practice by itself.

# Discussion

## How should the modules be implemented

It is quite unclear how to imeplement modules and their loading.
It should be very generic but at the same time ... functional.
Also, the system itself needs to know which modules it supports and if the data is compatible.
To tackle this, it seems that *loader* and *compatibility* modules need to arise.

## Transactions

A classical way of working with data may be beneficial here as well, eventhough we are trying to redefine how the data is accessed.

## Parallelization

This should be thought of
