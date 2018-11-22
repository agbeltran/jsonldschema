import os
import unittest
import json
from deepdiff import DeepDiff
from nose.tools import eq_
from cedar import schema2cedar, client


# Set some required variables
configfile_path = os.path.join(os.path.dirname(__file__), "../test_config.json")
if not (os.path.exists(configfile_path)):
    print("Please, create the config file.")
with open(configfile_path) as config_data_file:
    config_json = json.load(config_data_file)
config_data_file.close()

production_api_key = config_json["production_key"]
folder_id = config_json["folder_id"]
user_id = config_json["user_id"]


class TestSchema2Cedar(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestSchema2Cedar, self).__init__(*args, **kwargs)
        data_path = os.path.join(os.path.dirname(__file__), "../data/")
        self.input_schema_file = os.path.join(data_path, "person_schema.json")
        self.output_schema_file_element = os.path.join(data_path, "person_schema_element_out.json")
        self.output_schema_file_template = os.path.join(data_path, "person_schema_template_out.json")

    def setUp(self):
        self._data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.client = client.CEDARClient()
        self.templateElement = schema2cedar.Schema2CedarTemplateElement(production_api_key,
                                                                        folder_id,
                                                                        user_id)
        self.template = schema2cedar.Schema2CedarTemplate(production_api_key,
                                                          folder_id,
                                                          user_id)

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

    def test_convert_template(self):

        with open(self.input_schema_file, 'r') as orig_schema_file:
            # Load the JSON schema and close the file
            schema_as_json = json.load(orig_schema_file)
        orig_schema_file.close()

        output_schema = self.template.convert_template(schema_as_json)
        validation_response, validation_message = self.client.validate_template("production",
                                                                                self.template.production_api_key,
                                                                                json.loads(output_schema))

        print("validation response---> ", validation_response)
        print("validation message---> ", json.dumps(validation_message))

        print("----- output schema -------")
        print(output_schema)
        print("----- end of output schema -------")

        if validation_response:
            # save the converted file
            output_schema_file = open(os.path.join(self.output_schema_file_template), "w")
            self.template.json_pretty_dump(json.loads(output_schema), output_schema_file)
            output_schema_file.close()

            response = self.client.create_template("production",
                                               self.template.production_api_key,
                                               self.template.folder_id,
                                               output_schema)
            print(response)
        else:
            raise Exception('Invalid template conversion: ', validation_message)

    def test_convert_template_element(self):

        with open(self.input_schema_file, 'r') as orig_schema_file:
            # Load the JSON schema and close the file
            schema_as_json = json.load(orig_schema_file)
        orig_schema_file.close()

        output_schema = self.templateElement.convert_template_element(schema_as_json)

        print("----- output schema -------")
        print(output_schema)
        print("----- end of output schema -------")

        validation_response, validation_message = self.client.validate_element("production",
                                                                               self.templateElement.production_api_key,
                                                                               json.loads(output_schema))



        print("validation response---> ", validation_response)
        print("validation message---> ", validation_message)

        if validation_response:
            # save the converted file
            output_schema_file = open(self.output_schema_file_element, "w")
            self.template.json_pretty_dump(output_schema, output_schema_file)
            output_schema_file.close()

            response = self.client.create_template_element("production",
                                                           self.templateElement.production_api_key,
                                                           self.templateElement.folder_id,
                                                           os.path.join(self.output_schema_file_element))
            print(response.json())
        else:
            raise Exception('Invalid template element conversion: ', validation_message)
