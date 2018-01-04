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


    def test_validate_element_sample(self):
        sample_cedar_schema_path = os.path.join(self._data_dir, "sample_cedar_schema.json")
        api_key_file_path = os.path.join(self._data_dir, "agb_production.apikey")
        with open(api_key_file_path, 'r') as f:
            api_key = f.read()
        sample_cedar_schema_file = open(sample_cedar_schema_path, 'rb')
        sample_cedar_schema = json.load(sample_cedar_schema_file)
        response = self.client.validate_element("production", api_key, sample_cedar_schema)
        sample_cedar_schema_file.close()
        print(response)
        self.assertTrue(response["validates"] == "true")
        self.assertTrue(response["warnings"] == [])
        self.assertTrue(response["errors"] == [])

    def test_validate_element_sample_staging(self):
        sample_cedar_schema_path = os.path.join(self._data_dir, "sample_cedar_schema.json")
        api_key_file = os.path.join(self._data_dir, "agb_staging.apikey")
        with open(api_key_file, 'r') as f:
            api_key = f.read()
        sample_cedar_schema_file = open(sample_cedar_schema_path, 'rb')
        sample_cedar_schema = json.load(sample_cedar_schema_file)
        response = self.client.validate_element("staging", api_key, sample_cedar_schema)
        sample_cedar_schema_file.close()
        self.assertTrue( response["validates"] == "true")
        self.assertTrue(response["warnings"] == [])
        self.assertTrue(response["errors"] == [])

    def test_validate_element_vendor(self):
        sample_cedar_schema = os.path.join(self._data_dir, "vendor_cedar_schema.json")
        api_key_file = os.path.join(self._data_dir, "agb_production.apikey")
        with open(api_key_file, 'r') as f:
            api_key = f.read()
        response = self.client.validate_element("production", api_key, sample_cedar_schema)
        print(response)
        self.assertTrue(response["validates"] == "true")
        self.assertTrue(response["warnings"] == [])
        self.assertTrue(response["errors"] == [])

    def test_validate_element_vendor_staging(self):
        sample_cedar_schema = os.path.join(self._data_dir, "vendor_cedar_schema.json")
        api_key_file = os.path.join(self._data_dir, "agb_staging.apikey")
        with open(api_key_file, 'r') as f:
            api_key = f.read()
        response = self.client.validate_element("staging", api_key, sample_cedar_schema)
        print(response)
        self.assertTrue(response["validates"] == "true")