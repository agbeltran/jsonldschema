# CEDAR Client

**client.py**: implements a client of the CEDAR API with functionality to validate resources, create and delete folders, update templates and template elements

**schema2cedar.py**: implements a conversion from a generic JSON schemas to CEDAR template element and CEDAR templates.
The conversion engine relies on [jinja2](http://jinja.pocoo.org/). 


## CEDAR Documentation

### CEDAR Template Model v1.3.0

[Document](https://docs.google.com/document/d/1ugcE0eoNhZuEuaeQES4hNRri4VokcXBt0cfH91Sc5wc/edit#heading=h.ailpqdfgccfl))

### CEDAR Template Model v1.4.0

[Document](https://docs.google.com/document/d/1mfrnIOvmzeA6nWIQbE6zuMmac2D52hnS4Pu6IrQs-Hg/edit#heading=h.ailpqdfgccfl) 


### CEDAR code and API 


- Model validation library:
http://github.com/metadatacenter/cedar-model-validation-library/

- Python scripts:
https://github.com/metadatacenter/cedar-util/tree/develop/scripts

- REST APIs Quick start guide:  
https://github.com/metadatacenter/cedar-docs/wiki/CEDAR-REST-APIs


Resources

- https://resource.metadatacenter.org/api/

- https://resource.metadatacenter.org/swagger-api/swagger.json

Staging
- https://resource.staging.metadatacenter.org



#### Validation

https://resource.metadatacenter.org/api/#!/Validate/post_command_validate

