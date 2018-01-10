import os
import unittest
from cedar.jsonschema2cedar import *
import cedar.client
import json


class TestJSONschema2cedar(unittest.TestCase):

    def setUp(self):
        self._data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.client = cedar.client.CEDARClient()

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


    def convert(self, schema_filename, cedar_schema_filename, conversion_output_filename):
        full_schema_filename = os.path.join(self._data_dir, schema_filename)
        output_schema = cedar.jsonschema2cedar.convert_template_element(full_schema_filename)
        output_schema_json = json.loads(output_schema)
        cedar_schema_file = open(os.path.join(self._data_dir, cedar_schema_filename), "rb")
        cedar_schema_json = json.load(cedar_schema_file)
        comparison = diff_dicts(output_schema_json, cedar_schema_json, cedar.jsonschema2cedar.IGNORE_KEYS)
        print(comparison)

        ### save converted file
        outfile = open(os.path.join(self._data_dir, conversion_output_filename), "w")
        json_pretty_dump(output_schema_json, outfile)

        ### validate converted file
        self.validate_converted_file(output_schema, "production", "agb_production.apiKey")
        cedar_schema_file.close()
        outfile.close()

    def test_convert_vendor(self):
        self.convert("vendor_schema.json", 'vendor_cedar_schema.json', 'vendor_cedar_schema_out.json')

    def test_convert_sample(self):
        self.convert("sample_schema.json", 'sample_cedar_schema.json', 'sample_cedar_schema_out.json')

    def test_convert_sample(self):
        self.convert("sample_schema_required_name.json", 'sample_cedar_schema_required_name.json', 'sample_cedar_schema_required_name_out.json')
