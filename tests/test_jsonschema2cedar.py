import os
import unittest
import cedar.jsonschema2cedar


class TestJSONschema2cedar(unittest.TestCase):

    def setUp(self):
        self._data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_convert_vendor(self):
        vendor_schema = os.path.join(self._data_dir, "vendor_schema.json")
        vendor_cedar_schema = cedar.jsonschema2cedar.convert_template_element(vendor_schema)
        print(vendor_cedar_schema)
        ###validate the CEDAR schema

    def test_convert_sample(self):
        sample_schema = os.path.join(self._data_dir, "sample_schema.json")
        sample_cedar_schema = cedar.jsonschema2cedar.convert_template_element(sample_schema)
        print(sample_cedar_schema)
        ###validate the CEDAR schema

