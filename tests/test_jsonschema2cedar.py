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


    def convert(self, schema_filename, cedar_schema_filename):
        full_schema_filename = os.path.join(self._data_dir, schema_filename)
        output_schema = cedar.jsonschema2cedar.convert_template_element(full_schema_filename)
        output_schema_json = json.loads(output_schema)
        cedar_schema_file = open(os.path.join(self._data_dir, cedar_schema_filename), "rb")
        cedar_schema_json = json.load(cedar_schema_file)
        comparison = equal_dicts(output_schema_json, vendor_cedar_schema_json, cedar.jsonschema2cedar.IGNORE_KEYS)
        print(comparison)

    def test_convert_vendor(self):
        vendor_schema = os.path.join(self._data_dir, "vendor_schema.json")
        output_schema = cedar.jsonschema2cedar.convert_template_element(vendor_schema)
        output_schema_json = json.loads(output_schema)
        ### compare json schema output with json schema produced by cedar tool (minus UI specific values)
        vendor_cedar_schema_file = open(os.path.join(self._data_dir, 'vendor_cedar_schema.json'), "rb")
        vendor_cedar_schema_json = json.load(vendor_cedar_schema_file)
        comparison = equal_dicts(output_schema_json, vendor_cedar_schema_json, cedar.jsonschema2cedar.IGNORE_KEYS)
        print(comparison)

        self.validate_converted_file(vendor_cedar_schema_file, "production", "agb_production.apiKey")

        vendor_cedar_schema_file.close()

        outfile  = open(os.path.join(self._data_dir, 'vendor_cedar_schema_out.json'), "w")
        json_pretty_dump(output_schema_json, outfile)
        outfile.close()


    def test_convert_sample(self):
        sample_schema = os.path.join(self._data_dir, "sample_schema.json")
        sample_cedar_schema = cedar.jsonschema2cedar.convert_template_element(sample_schema)
        output_schema_json = json.loads(sample_cedar_schema)

        sample_cedar_schema_file = open(os.path.join(self._data_dir, 'sample_cedar_schema.json'), "rb")
        sample_cedar_schema_json = json.load(sample_cedar_schema_file)
        comparison = equal_dicts(output_schema_json, sample_cedar_schema_json, cedar.jsonschema2cedar.IGNORE_KEYS)
        print(comparison)
        sample_cedar_schema_file.close()

        #print(sample_cedar_schema)
        self.validate_converted_file(sample_cedar_schema, "production", "agb_production.apiKey")

