import cedar.client
import unittest
import os

class CEDARClientTestCase(unittest.TestCase):


    def setUp(self):
        self.client = cedar.client.CEDARClient()
        self._data_dir = os.path.join(os.path.dirname(__file__), "data")


    def test_get_users(self):
        self.client.get_users()

    def test_validate_element_sample(self):
        sample_cedar_schema = os.path.join(self._data_dir, "sample_cedar_schema.json")
        api_key_file = os.path.join(self._data_dir, "agb_production.apikey")
        with open(api_key_file, 'r') as f:
            api_key = f.read()
        self.client.validate_element("production", api_key, sample_cedar_schema)

    def test_validate_element_vendor(self):
        sample_cedar_schema = os.path.join(self._data_dir, "vendor_cedar_schema.json")
        api_key_file = os.path.join(self._data_dir, "agb_production.apikey")
        with open(api_key_file, 'r') as f:
            api_key = f.read()
        self.client.validate_element("production", api_key, sample_cedar_schema)