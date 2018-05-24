import cedar.client
import unittest
import os
import json


class CEDARClientTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CEDARClientTestCase, self).__init__(*args, **kwargs)

        configfile_path = os.path.join(os.path.dirname(__file__), "test_config.mine.json")
        if not (os.path.exists(configfile_path)):
            configfile_path = os.path.join(os.path.dirname(__file__), "test_config.json")
        with open(configfile_path) as config_data_file:
            config_json = json.load(config_data_file)
            self.validate_config(config_json)

        self._data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.production_api_key = config_json["production_key"]
        self.staging_api_key = config_json["staging_key"]
        self.template_id = config_json["template_id"]
        self.folder_id = config_json["folder_id"]
        self.template_path_no_id = os.path.join(self._data_dir, config_json["example_template_file_no_id"])
        self.template_path_with_id = os.path.join(self._data_dir, config_json["example_template_file_with_id"])

    def setUp(self):
        self.client = cedar.client.CEDARClient()

    def validate_config(self, config_data):
        try:
            self.assertTrue(config_data['production_key'])
        except AssertionError as inst:
            print("Please provide an production API key before running tests")
            raise
        try:
            self.assertTrue(config_data['staging_key'])
        except AssertionError:
            print("Please provide a staging API key before running tests")
            raise
        try:
            self.assertTrue(config_data['folder_id'])
        except AssertionError:
            print("Please provide a valid folder ID before running tests")
            raise
        try:
            self.assertTrue(config_data['template_id'])
        except AssertionError:
            print("Please provide a valid template ID before running tests")
            raise

    def test_get_users(self):
        response = self.client.get_users("production", self.production_api_key)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.text != None)

    def test_get_template_content(self):
        response = self.client.get_template_content("production", self.production_api_key, self.template_id)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.text != None)

    def test_get_folder_content(self):
        response = self.client.get_folder_content('production', self.production_api_key, self.folder_id)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.text != None)

    def test_create_template(self):
        response = self.client.create_template('production', self.production_api_key, self.folder_id, self.template_path_no_id)
        self.assertTrue(response.status_code == 201)  # small trick: when creating an instance, code returned is 201
        self.assertTrue(response.text != None)

    def test_update_template(self):
        response = self.client.update_template("production", self.production_api_key, self.template_path_with_id)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.text != None)

    def test_get_users_staging(self):
        response = self.client.get_users("staging", self.staging_api_key)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.text != None)

    """
    Common method for the tests validating the elements
    """

    def validate_element(self, cedar_schema_json_filename, endpoint, api_key):
        cedar_schema_path = os.path.join(self._data_dir, cedar_schema_json_filename)
        with open(cedar_schema_path, 'r') as template:
            cedar_schema = json.load(template)
        response = self.client.validate_element(endpoint, api_key, cedar_schema)
        template.close()
        print("Test done")
        print(json.dumps(response, indent=4, sort_keys=True))
        self.assertTrue(response["validates"] == "true")
        self.assertTrue(response["warnings"] == [])
        self.assertTrue(response["errors"] == [])

    def test_validate_template(self):
        print("Trying to validate a template")
        with open(self.template_path_with_id, 'r') as template_content:
            template = json.load(template_content)
        response = self.client.validate_template("production", self.production_api_key, template)
        self.assertTrue(json.loads(response.text)["validates"] == "true")
        self.assertTrue(json.loads(response.text)["warnings"] == [])
        self.assertTrue(json.loads(response.text)["errors"] == [])

    def test_validate_element_sample(self):
        self.validate_element("example_template_with_id.json", "production", self.production_api_key)

    def test_validate_element_sample_staging(self):
        self.validate_element("sample_cedar_schema.json", "staging", self.staging_api_key)

    def test_validate_element_vendor(self):
        self.validate_element("vendor_cedar_schema.json", "production", self.production_api_key)

    def test_validate_element_vendor_staging(self):
        self.validate_element("vendor_cedar_schema.json", "staging", self.staging_api_key)