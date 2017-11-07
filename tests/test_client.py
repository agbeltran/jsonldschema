import cedar.client
import unittest
import os

class CEDARClientTestCase(unittest.TestCase):


    def setUp(self):
        self.client = cedar.client.CEDARClient()
        self._data_dir = os.path.join(os.path.dirname(__file__), "data")


    def test_get_users(self):
        self.client.get_users()

    def test_validate_template(self):
        sample_cedar_schema = os.path.join(self._data_dir, "sample_cedar_schema.json")
        api_key_file = os.path.join(self._data_dir, "agb.apikey")
        api_key = str = open(api_key_file, 'r').read()
        self.client.validate_template("staging", api_key, sample_cedar_schema)