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