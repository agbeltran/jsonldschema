import os
import unittest
import cedar.jsonschema2cedar
import cedar.client
import json


class TestJSONschema2cedar(unittest.TestCase):

    def setUp(self):
        self._data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.client = cedar.client.CEDARClient()

    def json_pretty_dump(self, json_object, output_file):
        return json.dump(json_object,  output_file, sort_keys=True, indent=4, separators=(',', ': '))


    def validate_converted_file(self, cedar_schema, endpoint, endpoint_key_filename):
        # get api key
        api_key_file_path = os.path.join(self._data_dir, endpoint_key_filename)
        with open(api_key_file_path, 'r') as f:
            api_key = f.read()
        response = self.client.validate_element(endpoint, api_key, cedar_schema)
        print(response)
        self.assertTrue(response["validates"] == "true")
        self.assertTrue(response["warnings"] == [])
        self.assertTrue(response["errors"] == [])

    def test_convert_vendor(self):
        vendor_schema = os.path.join(self._data_dir, "vendor_schema.json")
        output_schema = cedar.jsonschema2cedar.convert_template_element(vendor_schema)
        output_schema_json = json.loads(output_schema)
        outfile  = open(os.path.join(self._data_dir, 'vendor_cedar_schema_out.json'), "w")
        json.dump(output_schema_json, outfile, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
        outfile.close()
        ### compare json schema output with json schema produced by cedar tool (minus UI specific values


        #with open(os.path.join(self._data_dir, 'vendor_cedar_schema_out.json'), 'w') as outfile:
        #    self.json_pretty_dump(output_schema, outfile)
        #self.validate_converted_file(output_schema, "production", "agb_production.apiKey")

    def test_convert_sample(self):
        sample_schema = os.path.join(self._data_dir, "sample_schema.json")
        sample_cedar_schema = cedar.jsonschema2cedar.convert_template_element(sample_schema)
        #print(sample_cedar_schema)
        self.validate_converted_file(sample_cedar_schema, "production", "agb_production.apiKey")

