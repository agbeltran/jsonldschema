
This folder contains JSON schemas and variables used for testing the functionality of the code.

- sample_schema.json: simple JSON schema representing the sample information, the only attribute included is the name of the sample
- sample_cedar_schema.json: it is the JSON schema generated through the CEDAR interface, which corresponds to sample_schema.json
- vendor_schema.json: simple JSON schema representing vendor (example taken from MIACA) with four attributes
- vendor_cedar_schema.sjon: it is the JSON schema generated through the CEDAR interface corresponding to vendor_schema.json
- example_template_no_id: a template to upload on the server but stripped out of it's @id attribute (allocated by the server)
- example_template_with_id: a template to upload on the server (be sure to have a @id attribute set to the template you want to modify)
- test_config.json: this is the configuration file for the unit tests. Inside, you can modify;
    - the name of both api key files (production and staging), in order to import your own keys (need to be setup at install)
    - the folder id which will be used to create new template and retrieve folder content (need to be setup at install)
    - the template id which will be used to retrieve the content of a template (need to be setup at install)
    - the names of both example template files so that you can use your own (need to be setup at install)


- this folder should also contain the api key files for production and staging service which can be personalized using test_config.json