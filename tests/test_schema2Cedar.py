import os
import unittest
import json
from deepdiff import DeepDiff
from nose.tools import eq_
from cedar import schema2Cedar, client


class TestSchema2Cedar(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestSchema2Cedar, self).__init__(*args, **kwargs)
        self.input_schema_file = "data/schema.json"
        self.output_schema_file = "data/schema_out.json"
        self.cedar_schema_file = "cedar_schema.json"

    def setUp(self):
        self._data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.client = client.CEDARClient()
        self.templateElement = schema2Cedar.Schema2CedarTemplateElement()
        self.template = schema2Cedar.Schema2CedarTemplate()

    @staticmethod
    def local_validate(converted_schema, cedar_schema):

        # set up the main keys we want to ignore (like dates ...)
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
            "root['title']",
            "root['_ui']['order']"
        ]

        # set up the properties keys we want to ignore (like dates ...)
        for item in converted_schema['properties']:
            if item not in ignored_keys:
                ignored_paths.append("root['properties']['" + item + "']['@id']")
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

        eq_(DeepDiff(converted_schema, cedar_schema, exclude_paths=ignored_paths), {})

    def convert_template(self):
        output_schema = self.template.convert_template(self.input_schema_file)
        validation_response = self.client.validate_template("production",
                                                            self.template.production_api_key,
                                                            json.loads(output_schema))

        # save the converted file
        output_schema_file = open(os.path.join(self.cedar_schema_file), "w")
        self.template.json_pretty_dump(json.loads(output_schema), self.output_schema_file)
        output_schema_file.close()

        response = self.client.create_template("production",
                                               self.template.production_api_key,
                                               self.template.folder_id,
                                               os.path.join(self.output_schema_file))

    def convert_template_element(self):
        output_schema = self.templateElement.convert_template_element(self.input_schema_file)
        validation_respons = self.client.validate_element("production",
                                                          self.templateElement.production_api_key,
                                                          json.loads(output_schema))

        # save the converted file
        output_schema_file = open(os.path.join(self.cedar_schema_file), "w")
        self.template.json_pretty_dump(json.loads(output_schema), self.output_schema_file)
        output_schema_file.close()

        response = self.client.create_template_element("production",
                                                       self.templateElement.production_api_key,
                                                       self.templateElement.folder_id,
                                                       os.path.join(self.output_schema_file))

    def test_convert_template(self):
        self.convert_template()

    def test_convert_template_element(self):
        self.convert_template_element()
