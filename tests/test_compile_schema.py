import unittest
import os
import json
from deepdiff import DeepDiff
from jsonschema.validators import RefResolver
from utils import compile_schema


class CompileSchemaTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CompileSchemaTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.schema_URL = "https://w3id.org/dats/schema/study_schema.json#"
        mapping_dir = os.path.join(os.path.dirname(__file__), "data")

        with open(os.path.join(mapping_dir, "study_schema.json")) as file_opened:
            self.study_schema = json.load(file_opened)
            file_opened.close()
        with open(os.path.join(mapping_dir, "compile_test.json")) as file_opened:
            self.expected_output = json.load(file_opened)
            file_opened.close()

    def test_resolve_reference(self):
        ref_resolved = compile_schema.resolve_reference(self.schema_URL)
        output_value = json.loads(json.dumps(ref_resolved))
        output_expected = json.loads(json.dumps(self.study_schema))
        self.assertTrue(DeepDiff(output_value, output_expected) == {})

        ref_2_resolved = compile_schema.resolve_reference("fakeURL")
        self.assertTrue(isinstance(ref_2_resolved, type))
        # TODO: test for exception, not type

    def test_get_name(self):
        expected_output = "study_schema.json"
        schema_name = compile_schema.get_name(self.schema_URL)
        self.assertTrue(schema_name == expected_output)

    def test_resolve_schema_references(self):

        expected_output = self.expected_output
        processed_schemas = {}
        schema_url = 'https://w3id.org/dats/schema/person_schema.json#'
        processed_schemas[compile_schema.get_name(schema_url)] = '#'
        data = compile_schema.resolve_schema_references(
                               compile_schema.resolve_reference(schema_url),
                               processed_schemas,
                               schema_url)

        output_value = json.loads(json.dumps(data))
        output_expected = json.loads(json.dumps(expected_output))
        self.assertTrue(DeepDiff(output_value, output_expected) == {})

    def test__resolve_schema_references(self):
        schema_url = 'https://w3id.org/dats/schema/person_schema.json#'
        processed_schemas = {compile_schema.get_name(schema_url): '#'}

        schema = compile_schema.resolve_reference(schema_url)
        resolver = RefResolver(schema_url, schema, store={})
        data = compile_schema._resolve_schema_references(schema,
                                                         resolver,
                                                         processed_schemas,
                                                         '#')

        output_value = json.loads(json.dumps(data))
        expected_output = json.loads(json.dumps(self.expected_output))

        self.assertTrue(DeepDiff(output_value, expected_output) == {})
