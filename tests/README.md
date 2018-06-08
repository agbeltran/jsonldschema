Test cases and test configuration files:

- test_client.py: test class for the CEDAR client functionality

- test_config.json: this is the configuration file for the unit tests. Inside, you can modify;
    - the name of both api key files (production and staging), in order to import your own keys (need to be setup at install)
    - the folder id which will be used to create new template and retrieve folder content (need to be setup at install)
    - the template id which will be used to retrieve the content of a template (need to be setup at install)
    - the names of both example template files so that you can use your own (need to be setup at install)
    
- test_jsonschema2cedar.py: test class for the conversion between JSON schemas and CEDAR template elements and templates

- test_jsonschema_validatory.py: test class to validate test JSON schemas and JSON instances

- test_mock_client.py: a test class for the CEDAR client with mocked objects    
