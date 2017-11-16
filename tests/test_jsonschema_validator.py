import os
import unittest
import util.jsonschema_validator


class TestJSONschemaValidator(unittest.TestCase):

    def setUp(self):
        self._data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_convert_vendor(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "vendor_cedar_schema.json"))

    def test_convert_sample(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "sample_cedar_schema.json"))
