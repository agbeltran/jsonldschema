import os
import unittest
from cedar.jsonschema2cedar import *
import cedar.client
import json
import validate.jsonschema_validator
import diff.jsonschema_diff


class TestJSONschema2cedar(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestJSONschema2cedar, self).__init__(*args, **kwargs)

        configfile_path = os.path.join(os.path.dirname(__file__), "test_config.json")
        if not (os.path.exists(configfile_path)):
            configfile_path = os.path.join(os.path.dirname(__file__), "test_config.json.sample")
        with open(configfile_path) as config_data_file:
            config_json = json.load(config_data_file)

        self._data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.production_api_key = config_json["production_key"]
        self.staging_api_key = config_json["staging_key"]
        self.template_id = config_json["template_id"]
        self.folder_id = config_json["folder_id"]
        self.template_path_no_id = os.path.join(self._data_dir, config_json["example_template_file_no_id"])
        self.template_path_with_id = os.path.join(self._data_dir, config_json["example_template_file_with_id"])

    def setUp(self):
        self._data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.client = cedar.client.CEDARClient()

    def validate_converted_file(self, cedar_schema, endpoint):
        response = self.client.validate_element(endpoint, self.production_api_key, cedar_schema)
        self.assertTrue(json.loads(response.text)["validates"] == "true")
        self.assertTrue(json.loads(response.text)["warnings"] == [])
        self.assertTrue(json.loads(response.text)["errors"] == [])

        """
        # get api key
        api_key_file_path = os.path.join(self._data_dir, endpoint_key_filename)
        with open(api_key_file_path, 'r') as f:
            api_key = f.read()
        response = self.client.validate_element(endpoint, api_key, cedar_schema)
        print(response)
        f.close()
        self.assertTrue(response["validates"] == "true")
        self.assertTrue(response["warnings"] == [])
        self.assertTrue(response["errors"] == [])
        """

    def convert(self, schema_filename, cedar_schema_filename, conversion_output_filename):

        full_schema_filename = os.path.join(self._data_dir, schema_filename)
        output_schema = cedar.jsonschema2cedar.convert_template_element(full_schema_filename)
        output_schema_json = json.loads(output_schema)
        self.assertTrue(validate.jsonschema_validator.validate_schema_file(output_schema_json))
        self.validate_converted_file(output_schema_json, "production")

        """
        cedar_schema_file = os.path.join(self._data_dir, cedar_schema_filename)
        with open(cedar_schema_file) as f:
            cedar_schema_json = json.loads(f.read())
        f.close()
        self.validate_converted_file(cedar_schema_json, "production")
        """

        # Display the differences between the two JSON
        #diff.jsonschema_diff.compare_dicts(output_schema_json, cedar_schema_json, cedar.jsonschema2cedar.IGNORE_KEYS, 0)

        # save the converted file
        outfile = open(os.path.join(self._data_dir, conversion_output_filename), "w")
        json_pretty_dump(output_schema_json, outfile)
        outfile.close()

    def test_convert_vendor(self):
        self.convert("vendor_schema.json", 'vendor_cedar_schema.json', 'vendor_cedar_schema_out.json')

    def test_convert_sample(self):
        self.convert("sample_schema.json", 'sample_cedar_schema.json', 'sample_cedar_schema_out.json')

    def test_convert_sample_required_name(self):
        self.convert("sample_required_name_annotated_schema.json", 'sample_required_name_annotated_cedar_schema.json', 'sample_required_name_annotated_schema_out.json')
