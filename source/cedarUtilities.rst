CEDAR utilities
===============


The CEDAR utilities main function is to allow a user to transform a JSON-Schema draft 4 network into a CEDAR schema
network.

.. literalinclude:: /../examples/cedar.py

---------------


The CEDAR client will provide all the links the the CEDAR API functionality such as get, post and updates on templates,
template elements, folders, instances ect ...


.. automodule:: client
    :members:

---------------

The schema2cedar classes will help you transform your JSON schemas draft 04 into compatible CEDAR schemas

.. automodule:: schema2cedar
    :members:

