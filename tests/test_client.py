import cedar.client
import unittest
import os
import json


class CEDARClientTestCase(unittest.TestCase):

    def setUp(self):
        self.client = cedar.client.CEDARClient()
        self._data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_get_users(self):
        api_key_file = os.path.join(self._data_dir, "agb_production.apikey")
        with open(api_key_file, 'r') as f:
            api_key = f.read()
        response = self.client.get_users("production", api_key)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.text != None)

    def test_get_template_content(self):
        api_key_file = os.path.join(self._data_dir, "agb_staging.apikey")
        template_id = "b31c2aa9-1ea0-4a66-b3ee-c550d8a2aa2e"
        with open(api_key_file, 'r') as f:
            api_key = f.read()
        response = self.client.get_template_content("production", api_key, template_id)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.text != None)

    def test_get_folder_content(self):
        api_key_file = os.path.join(self._data_dir, "agb_staging.apikey")
        folder_id = "6226f622-dfd9-441e-bab1-816c10398fc0"
        with open(api_key_file, 'r') as f:
            api_key = f.read()
        response = self.client.get_folder_content('production', api_key, folder_id)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.text != None)

    def test_create_template(self):
        api_key_file = os.path.join(self._data_dir, "agb_staging.apikey")
        folder_id = "6226f622-dfd9-441e-bab1-816c10398fc0"
        with open(api_key_file, 'r') as f:
            api_key = f.read()
        template_path = os.path.join(self._data_dir, "example_template.json")
        response = self.client.create_template('production', api_key, folder_id, template_path)
        print(response)
        self.assertTrue(response.status_code == 201) #small trick: when creating an instance, code returned is 201, not 200
        self.assertTrue(response.text != None)


    def test_get_users_staging(self):
        api_key_file = os.path.join(self._data_dir, "agb_staging.apikey")
        with open(api_key_file, 'r') as f:
            api_key = f.read()
        response = self.client.get_users("staging", api_key)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.text != None)




    """
    Common method for the tests validating the elements
    """

    def validate_element(self, cedar_schema_json_filename, endpoint, endpoint_key_filename):
        cedar_schema_path = os.path.join(self._data_dir, cedar_schema_json_filename)
        api_key_file_path = os.path.join(self._data_dir, endpoint_key_filename)
        with open(api_key_file_path, 'r') as f:
            api_key = f.read()
        cedar_schema_file = open(cedar_schema_path, 'rb')
        cedar_schema = json.load(cedar_schema_file)
        response = self.client.validate_element(endpoint, api_key, cedar_schema)
        cedar_schema_file.close()
        print("Test done")
        self.assertTrue(response["validates"] == "true")
        self.assertTrue(response["warnings"] == [])
        self.assertTrue(response["errors"] == [])


    def test_validate_element_sample(self):
        self.validate_element("sample_cedar_schema.json", "production", "agb_production.apikey")

    def test_validate_element_sample_staging(self):
        self.validate_element("sample_cedar_schema.json", "staging", "agb_staging.apikey")

    def test_validate_element_vendor(self):
        self.validate_element("vendor_cedar_schema.json", "production", "agb_production.apikey")

    def test_validate_element_vendor_staging(self):
        self.validate_element("vendor_cedar_schema.json", "staging", "agb_staging.apikey")