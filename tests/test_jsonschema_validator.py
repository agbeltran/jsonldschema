import os
import unittest
import util.jsonschema_validator


class TestJSONschemaValidator(unittest.TestCase):

    def setUp(self):
        self._data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_convert_vendor(self):
        vendor_schema = os.path.join(self._data_dir, "vendor_schema.json")
        self.assertTrue(util.jsonschema_validator.validate_schema_file(vendor_schema))

    def test_convert_sample(self):
        sample_schema = os.path.join(self._data_dir, "sample_schema.json")
        self.assertTrue(util.jsonschema_validator.validate_schema_file(sample_schema))
