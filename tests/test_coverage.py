import unittest
import os
import json
from SemDiff.coverage import Coverage

class CoverageTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CoverageTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        data_path = os.path.join(os.path.dirname(__file__), "./data")
        self.schema = json.load(open(os.path.join(data_path, "schema1.json")))
        self.context1 = json.load(open(os.path.join(data_path, "context1.json")))
        self.context2 = json.load(open(os.path.join(data_path, "context2.json")))

    def test_json_schema_context_coverage(self):
        [overlap, diff] = Coverage.json_schema_context_coverage(self.schema, self.context1)
        self.assertTrue("identifier" in overlap)
        self.assertTrue("lastName" in overlap)
        self.assertTrue("fullName" in overlap)
        self.assertTrue("firstName" in overlap)
        self.assertTrue("alternateIdentifiers" in diff)


    def test_json_schema_context_mapping(self):
       mappings = Coverage.json_schema_context_mapping(self.schema, self.context1, self.context2)
       self.assertTrue(mappings["fullName"] == ['sdo:name', 'sdo:name'])


