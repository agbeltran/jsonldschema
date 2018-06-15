import os
import unittest
from typing import Set

from cedar import schema2TemplateElement
import cedar.client
import json
from pprint import pprint
from deepdiff import DeepDiff
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

    def convert_templateElement(self, schema_filename, output_file, cedar_file_path):

        full_schema_filename = os.path.join(self._data_dir, schema_filename)
        output_schema = schema2TemplateElement.convert_template_element(full_schema_filename)
        output_schema_json = json.loads(output_schema)

        response = self.client.validate_element("production", self.production_api_key, output_schema_json)

        # save the converted file
        outfile = open(os.path.join(self._data_dir, output_file), "w")
        schema2TemplateElement.json_pretty_dump(output_schema_json, outfile)
        outfile.close()

        eq_(response.status_code, 200)
        eq_(json.loads(response.text)["validates"], "true")
        eq_(len(json.loads(response.text)["warnings"]), 0)
        eq_(len(json.loads(response.text)["errors"]), 0)

        with open(os.path.join(self._data_dir, cedar_file_path)) as cedar_file:
            cedar_schema = json.load(cedar_file)
        print("\n")

        ignored_keys = ["@type", "@id", "@context"]

        ignored_paths = [
            "root['@id']",
            "root['description']",
            "root['oslc:modifiedBy']",
            "root['pav:createdBy']",
            "root['pav:createdOn']",
            "root['pav:lastUpdatedOn']",
            "root['pav:version']",
            "root['schema:description']",
            "root['schema:name']",
            "root['schema:title']",
            "root['title']"
        ]

        for item in output_schema_json['properties']:
            if item not in ignored_keys:
                ignored_paths.append("root['properties']['"+item+"']['@id']")
                ignored_paths.append("root['properties']['" + item + "']['oslc:modifiedBy']")
                ignored_paths.append("root['properties']['" + item + "']['pav:createdBy']")
                ignored_paths.append("root['properties']['" + item + "']['pav:createdOn']")
                ignored_paths.append("root['properties']['" + item + "']['pav:lastUpdatedOn']")
                ignored_paths.append("root['properties']['" + item + "']['pav:version']")
                ignored_paths.append("root['properties']['" + item + "']['schema:description']")
                ignored_paths.append("root['properties']['" + item + "']['schema:name']")
                ignored_paths.append("root['properties']['" + item + "']['schema:title']")
                ignored_paths.append("root['properties']['" + item + "']['title']")
                ignored_paths.append("root['properties']['" + item + "']['description']")

        pprint(DeepDiff(output_schema_json, cedar_schema, verbose_level=0, exclude_paths=ignored_paths), indent=4)

    def test_convert_sample_schema(self):
        self.convert_templateElement("sample_required_name_annotated_schema.json",
                                     "sample_required_name_annotated_schema_out.json",
                                     "sample_required_name_annotated_cedar_schema.json")

    def test_convert_vendor_schema(self):
        self.convert_templateElement("person_schema.json",
                                     "person_schema_out.json",
                                     "person_cedar_schema.json")
