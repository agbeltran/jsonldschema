import unittest
import os
import json
from semDiff.compareEntities import EntityCoverage


class SemDiffTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(SemDiffTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        data_path = os.path.join(os.path.dirname(__file__), "./data")
        self.schema_1 = json.load(open(os.path.join(data_path, "schema1.json")))
        open(os.path.join(data_path, "schema1.json"))
        self.schema_2 = json.load(open(os.path.join(data_path, "schema2.json")))
        open(os.path.join(data_path, "schema1.json"))
        self.context_1 = json.load(open(os.path.join(data_path, "context1.json")))
        self.context_2 = json.load(open(os.path.join(data_path, "context2.json")))

        self.semantic_comparator = EntityCoverage(self.schema_1,
                                                  self.context_1,
                                                  self.schema_2,
                                                  self.context_2)

    def test___build_context_dict(self):
        schema_input = {
            "schema": self.schema_1,
            "context": self.context_1
        }

        # This is a particular structure as we are calling a private method through its reflection
        comparator = self.semantic_comparator._EntityCoverage__build_context_dict(schema_input)
        self.assertTrue(comparator[1] == ['alternateIdentifiers'])
        self.assertTrue(len(comparator[0]) == 4)
        self.assertTrue('https://schema.org/identifier' in comparator[0].keys())
        self.assertTrue(comparator[0]['https://schema.org/identifier'] == ['identifier'])
        self.assertTrue('https://schema.org/name' in comparator[0].keys())
        self.assertTrue(comparator[0]['https://schema.org/name'] == ['fullName'])
        self.assertTrue('https://schema.org/givenName' in comparator[0].keys())
        self.assertTrue(comparator[0]['https://schema.org/givenName'] == ['firstName'])
        self.assertTrue('https://schema.org/familyName' in comparator[0].keys())
        self.assertTrue(comparator[0]['https://schema.org/familyName'] == ['lastName'])

    def test___process_field(self):

        # Test Case 2
        processed_field = self.semantic_comparator.\
          _EntityCoverage__process_field("firstName",
                                         "https://schema.org/givenName",
                                         self.context_2['@context'],
                                         {})
        self.assertTrue('https://schema.org/givenName' in processed_field.keys())
        self.assertTrue(processed_field['https://schema.org/givenName'] == ['firstName'])

        # Test Case 2
        processed_field = self.semantic_comparator. \
            _EntityCoverage__process_field("firstName",
                                           "https://schema.org/givenName",
                                           self.context_2['@context'],
                                           {"https://schema.org/givenName": ["firstName"]})
        self.assertTrue('firstName' in processed_field['https://schema.org/givenName'])

        # Test Case 3
        processed_field = self.semantic_comparator. \
            _EntityCoverage__process_field("firstName",
                                           "sdo:givenName",
                                           self.context_2['@context'],
                                           {"https://schema.org/givenName": []})
        self.assertTrue(processed_field['https://schema.org/givenName'] == ['firstName'])

    def test___compute_context_coverage(self):
        schema_input = {
            "schema": self.schema_1,
            "context": self.context_1
        }
        schema_input2 = {
            "schema": self.schema_2,
            "context": self.context_2
        }

        comparator1 = self.semantic_comparator.\
            _EntityCoverage__build_context_dict(schema_input)
        comparator2 = self.semantic_comparator.\
            _EntityCoverage__build_context_dict(schema_input2)

        coverage = self.semantic_comparator.\
            _EntityCoverage__compute_context_coverage(comparator1[0], comparator2[0])

        self.assertTrue(coverage[0].relative_coverage == "50.0")
        self.assertTrue(coverage[0].absolute_coverage[0] == "2")
        self.assertTrue(coverage[0].absolute_coverage[1] == "4")
        self.assertTrue(len(coverage[1]) == 2)


        schema_input_3 = {
            "schema": self.schema_1,
            "context": {
                "@context": {}
            }
        }
        comparator3 = self.semantic_comparator. \
            _EntityCoverage__build_context_dict(schema_input_3)
        coverage = self.semantic_comparator. \
            _EntityCoverage__compute_context_coverage(comparator1[0], comparator3[0])

