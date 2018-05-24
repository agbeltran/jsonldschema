Utility code for the Minimum Information Requirements Catalogue.

Functionality included:
 - conversion of a generic json-schema, and especially mircat json schemas, into a CEDAR template json-schema

### Create and use a virtual environment

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Setup

To run the CEDAR client tests, you will need to configure a few variables in /tests/test_config.json.
You will need to provide:
- your staging and production API keys
- an existing and valid folder ID on which you can read/write content on the production server
- an existing and valid template ID on which you can read/write content on the production server

You can also configure the "example_template_file_no_id" and "example_template_file_with_id" file path to point to 
another local json schema. When creating a new template on the server, a schema without an ID is necessary (the ID will
be automatically given by the server); when updating a template, the ID is retrieved automatically from the file and 
you the corresponding template gets updated on the server.

[![Build Status](https://travis-ci.org/FAIRsharing/mircat-tools.svg?branch=master)](https://travis-ci.org/FAIRsharing/mircat-tools)
