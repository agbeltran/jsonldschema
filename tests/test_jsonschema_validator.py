import os
import unittest
import util.jsonschema_validator


class TestJSONschemaValidator(unittest.TestCase):

    def setUp(self):
        self._data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_cedar_sample(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "sample_cedar_schema.json"))

    def test_cedar_schema_required(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "sample_cedar_schema_required_name.json"))

    def test_sample_schema(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "sample_schema.json"))

    def test_sample_schema_required_name(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "sample_schema_required_name.json"))

    def test_vendor_cedar_schema(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "vendor_cedar_schema.json"))

    def test_vendor_schema(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "vendor_schema.json"))