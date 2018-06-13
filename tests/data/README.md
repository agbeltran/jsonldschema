
This folder contains JSON schemas and variables used for testing the functionality of the code.

- **sample_schema.json**:
  simple JSON schema representing the sample information, the only attribute included is the name of the sample

- **sample_cedar_schema.json**: 
  it is the JSON schema generated through the CEDAR interface, which corresponds to sample_schema.json
  
- **sample_required_name.json**:
  the sample_schema extended to make the name attribute required
 
- **sample_required_name_cedar_schema.json**:
  the CEDAR template corresponding to sample_required_name.json
  
- **sample_required_name_annotated.json**:
  the sample_required_name schema with the addition that the schema is annotated with type OBI_0000747   
   
- **vendor_schema.json**: 
  simple JSON schema representing vendor (example taken from MIACA) with four attributes
  
- **vendor_cedar_schema.json**: 
  it is the JSON schema generated through the CEDAR interface corresponding to vendor_schema.json
  
- **example_template_no_id.json**: 
  a template to upload on the server but stripped out of it's @id attribute (allocated by the server)
  
- **example_template_with_id.json**: 
  a template to upload on the server (be sure to have a @id attribute set to the template you want to modify)


- this folder should also contain the api key files for production and staging service which can be personalized using test_config.json