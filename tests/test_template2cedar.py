import os
import unittest
from cedar import template2cedar
import cedar.client
import json
from nose.tools import eq_


class TestTemplate2cedar(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTemplate2cedar, self).__init__(*args, **kwargs)

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

    def convert_template(self, schema_filename, output_file, cedar_schema_file):

        """
        cedar_schema_path = os.path.join(self._data_dir, cedar_schema_file)
        with open(cedar_schema_path) as cedar_schema:
            data = json.load(cedar_schema)
            response = self.client.validate_template("production", self.production_api_key, data)
        """

        full_schema_filename = os.path.join(self._data_dir, schema_filename)
        output_schema = template2cedar.convert_template(full_schema_filename)
        output_schema_json = json.loads(output_schema)

        outfile = open(os.path.join(self._data_dir, output_file), "w")
        template2cedar.json_pretty_dump(output_schema_json, outfile)
        outfile.close()

        response = self.client.validate_template("production", self.production_api_key, output_schema_json)

        eq_(response.status_code, 200)
        eq_(json.loads(response.text)["validates"], "true")
        eq_(len(json.loads(response.text)["warnings"]), 0)
        eq_(len(json.loads(response.text)["errors"]), 0)

    def test_convert_access_schema(self):
        self.convert_template("access_schema.json", "access_schema_out.json", "access_cedar_schema.json")