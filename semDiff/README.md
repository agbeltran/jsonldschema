semdiff 
=======

This module includes methods to compare semantically JSON schemas based on associated context files.

We include methods to compare semantically:
 - entities represented in single JSON schemas (comparing the properties of the schemas)
 - a set of JSON schemas that reference each other, which we call a network of JSON schemas
 - both entities and their properties
 
We also include functionality to merge two JSON schemas and functionality to analyse 
the semantic coverage a context file provides for a given schema. 
    