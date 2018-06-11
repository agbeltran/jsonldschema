import os
import unittest
from cedar import schema2TemplateElement
import cedar.client
import json
from nose.tools import eq_


class TestSchema2TemplateElement(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestSchema2TemplateElement, self).__init__(*args, **kwargs)

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

    def convert_templateElement(self, schema_filename, output_file):

        full_schema_filename = os.path.join(self._data_dir, schema_filename)
        output_schema = schema2TemplateElement.convert_template_element(full_schema_filename)
        output_schema_json = json.loads(output_schema)

        response = self.client.validate_element("production", self.production_api_key, output_schema_json)

        #print(json.dumps(json.loads(response.text)["errors"], indent=4))


        # save the converted file
        outfile = open(os.path.join(self._data_dir, output_file), "w")
        schema2TemplateElement.json_pretty_dump(output_schema_json, outfile)
        outfile.close()

        eq_(response.status_code, 200)
        eq_(json.loads(response.text)["validates"], "true")
        eq_(len(json.loads(response.text)["warnings"]), 0)
        eq_(len(json.loads(response.text)["errors"]), 0)

    def test_convert_sample_schema(self):
        self.convert_templateElement("sample_required_name_schema.json", "sample_required_name_schema_out.json")

    def test_convert_vendor_schema(self):
        self.convert_templateElement("vendor_schema.json", "vendor_schema_out.json")
