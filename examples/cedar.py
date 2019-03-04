# import the modules
import json
import os
from cedar import schema2cedar, client

# get your api key, folder_id and user_is from the configuratio file:
configfile_path = os.path.join(os.path.dirname(__file__), "../../tests/test_config.json")
if not (os.path.exists(configfile_path)):
    print("Please, create the config file.")
with open(configfile_path) as config_data_file:
    config_json = json.load(config_data_file)
config_data_file.close()

production_api_key = config_json["production_key"]
folder_id = config_json["folder_id"]
user_id = config_json["user_id"]

# Create your schema or load it from a file
schema = {
          "id": "https://example.com/test1_main_schema.json",
          "$schema": "http://json-schema.org/draft-04/schema",
          "title": "Test case 1 for unit testing main schema",
          "description": "JSON-schema representing the first schema of the first "
                         "network used by JSONLD-SCHEMA merging unit tests.",
          "type": "object",
          "_provenance": {
              "url": "http://w3id.org/mircat/miaca/provenance.json"
          },
          "properties": {
              "@context": {
                  "description": "The JSON-LD context",
                  "anyOf": [
                      {
                          "type": "string"
                      },
                      {
                          "type": "object"
                      },
                      {
                          "type": "array"
                      }
                  ]
              },
              "@id": {
                  "description": "The JSON-LD identifier",
                  "type": "string",
                  "format": "uri"
              },
              "@type": {
                  "description": "The JSON-LD type",
                  "type": "string",
                  "enum": [
                      "Test1Main"
                  ]
              }
          }
      }

# instantiate the client
client = client.CEDARClient()

# instantiate the converter
template = schema2cedar.Schema2CedarTemplate(production_api_key, folder_id, user_id)

# Run the conversion
output_schema = template.convert_template(schema)
validation_response, validation_message = client.validate_template(
    "production",
    template.production_api_key,
    json.loads(output_schema))
