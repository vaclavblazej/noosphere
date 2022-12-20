FAQ
===

## Why are lists allowed in the flat structure?

Lists could be simulated with entries, however, there is a balance to strike between ease of use and expressibility.
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

It is quite unclear how to implement modules and their loading.
It should be very generic but at the same time ... functional.
Also, the system itself needs to know which modules it supports and if the data is compatible.
To tackle this, it seems that *loader* and *compatibility* modules need to arise.

## Transactions

A classical way of working with data may be beneficial here as well, even though we are trying to redefine how the data is accessed.

## Parallelization

This should be thought of
