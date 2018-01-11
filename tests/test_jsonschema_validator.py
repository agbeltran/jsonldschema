import os
import unittest
import util.jsonschema_validator


class TestJSONschemaValidator(unittest.TestCase):

    def setUp(self):
        self._data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_annotated_sample_cedar(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "annotated_sample_cedar_schema.json"))

    def test_sample_cedar(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "sample_cedar_schema.json"))

    def test_sample_cedar_required_name(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "sample_cedar_schema_required_name.json"))

    def test_sample(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "sample_schema.json"))

    def test_sample_required_name(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "sample_schema_required_name.json"))

    def test_vendor_cedar(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "vendor_cedar_schema.json"))

    def test_vendor(self):
        self.assertTrue(util.jsonschema_validator.validate_schema(self._data_dir, "vendor_schema.json"))

    def test_sample_instance(self):
        errors = util.jsonschema_validator.validate_instance(self._data_dir, "sample_schema.json", self._data_dir, "sample_data.json", 1, {})
        self.assertTrue(errors.__len__()==0)