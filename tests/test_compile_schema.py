import unittest
from utils import compile_schema
import json
from deepdiff import DeepDiff
from jsonschema.validators import RefResolver


class CompileSchemaTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CompileSchemaTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.schema_URL = "https://w3id.org/dats/schema/study_schema.json#"

    def test_resolve_reference(self):
        expected_output = json.load(open('data/study_schema.json'))

        ref_resolved = compile_schema.resolve_reference(self.schema_URL)
        output_value = json.loads(json.dumps(ref_resolved))
        output_expected = json.loads(json.dumps(expected_output))
        self.assertTrue(DeepDiff(output_value, output_expected) == {})

        ref_2_resolved = compile_schema.resolve_reference("fakeURL")
        self.assertTrue(isinstance(ref_2_resolved, type))
        # TODO: test for exception, not type

    def test_get_name(self):
        expected_output = "study_schema.json"
        schema_name = compile_schema.get_name(self.schema_URL)
        self.assertTrue(schema_name == expected_output)

    def test_resolve_schema_references(self):

        expected_output = json.load(open('data/compile_test.json'))

        processed_schemas = {}
        schema_url = 'https://w3id.org/dats/schema/person_schema.json#'
        processed_schemas[compile_schema.get_name(schema_url)] = '#'
        data = compile_schema.resolve_schema_references(compile_schema.resolve_reference(schema_url),
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
        expected_output = json.loads(json.dumps(json.load(open('data/compile_test.json'))))

        self.assertTrue(DeepDiff(output_value, expected_output) == {})
