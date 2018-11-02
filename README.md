
[![Build Status](https://travis-ci.org/FAIRsharing/jsonldschema.svg?branch=master)](https://travis-ci.org/FAIRsharing/jsonldschema)
[![Coverage Status](https://coveralls.io/repos/github/FAIRsharing/jsonldschema/badge.svg?branch=master)](https://coveralls.io/github/FAIRsharing/jsonldschema?branch=master)
[![Documentation Status](https://readthedocs.org/projects/jsonldschema/badge/?version=docs)](https://jsonldschema.readthedocs.io/en/latest/?badge=latest)

Utility code for the Minimum Information Requirements Catalogue.

Functionality included:
 - validation of JSON schemas
 - comparison between JSON schemas
 - conversion of a generic json-schema, and especially mircat json schemas, into a CEDAR template json-schema
 - CEDAR API function: get folders and templates content, upload or update templates, get users ...

### Create and use a virtual environment

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Setup

To run the tests related to the [CEDAR client](https://github.com/FAIRsharing/jsonldschema/tree/master/tests/integration), you will need to:

- make a copy of the ```/tests/test_config.json.sample``` file:

```bash
cp /tests/test_config.json.sample /tests/test_config.json
```
 
and configure a few variables in your local file ```/tests/test_config.json```.

You will need to provide:
- your staging and production CEDAR API keys (include the key string in the corresponding attribute)
- an existing and valid CEDAR folder ID on which you can read/write content on the production server
- an existing and valid CEDAR template ID on which you can read/write content on the production server
- a valid user ID which will become the author of created content (UUID on your CEDAR user profile page, https://cedar.metadatacenter.org/profile)


You can also configure the "example_template_file_no_id" and "example_template_file_with_id" file path to point to 
other local JSON schemas. These two schemas are needed for the following cases:

- when creating a new template on the server, a schema without an ID is necessary (the ID will
be automatically given by the server); 
- when updating a template, the ID is retrieved automatically from the file and 
the corresponding template gets updated on the server.
