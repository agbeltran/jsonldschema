from collections import OrderedDict
from nose.tools import eq_
from mock import patch
from utils import compile_schema


class TestCaseSchemaCompiler(object):

    def __init__(self, *args, **kwargs):
        super(TestCaseSchemaCompiler, self).__init__(*args, **kwargs)

    @classmethod
    def setup_class(cls):
        cls.mock_resolver_patcher = patch('utils.compile_schema.RefResolver.resolve')
        cls.mock_resolver = cls.mock_resolver_patcher.start()
        cls.mock_json_patcher = patch('utils.compile_schema.json.loads')
        cls.mock_json = cls.mock_json_patcher.start()
        cls.compiler = compile_schema

    @classmethod
    def teardown_class(cls):
        cls.mock_resolver_patcher.stop()
        cls.mock_json_patcher.stop()

    def test_get_name(self):
        expected_name = self.compiler.get_name("https://w3id.org/dats/schema/study_schema.json#")
        eq_(expected_name, 'study_schema.json')

    def test_resolve_reference(self):
        self.mock_json.return_value = "{'test':'test'}"
        tested_output = self.compiler.resolve_reference(
            "https://w3id.org/dats/schema/person_schema.json#")
        eq_(tested_output, self.mock_json.return_value)
        self.mock_json_patcher.stop()

    def test_resolve_reference_exception(self):
        tested_output = self.compiler.resolve_reference("123")
        eq_(type(tested_output), type)

    def test_schema_key_class(self):
        tested_output = self.compiler.SchemaKey
        eq_(tested_output.ref, "$ref")
        eq_(tested_output.items, "items")
        eq_(tested_output.properties, "properties")
        eq_(tested_output.definitions, "definitions")
        eq_(tested_output.pattern_properties, "patternProperties")
        eq_(tested_output.sub_patterns, ['anyOf', 'oneOf', 'allOf'])

    def test_resolve_schema_references(self):

        schema = {
            "id": "schemas/test.json#",
            "definitions": {
                "field_1": {"$ref": "second_test.json#"}
            },
            "properties": OrderedDict({
                "field_1": {"$ref": "second_test.json#"},
                "field_2": {
                    "type": "array",
                    "items": {
                        "anyOf": [
                            {
                                "$ref": "second_test.json"
                            }
                        ]
                    }
                }
            })
        }
        loaded_schemas = {
            "test.json": schema,
        }
        self.mock_json_patcher.start()
        self.mock_resolver.return_value = ["", {
            "id": "schemas/second_test.json",
            "properties": {
                "name": {
                    "description": "test description",
                    "type": "string"
                }
            }
        }]

        expected_output = OrderedDict({
            "id": "schemas/test.json#",
            "definitions": {
                "field_1": OrderedDict({"$ref": "#/properties/field_1"})
            },
            "properties": {
                "field_1": OrderedDict({
                    "id": "schemas/second_test.json",
                    "properties": {
                        "name": OrderedDict({
                            "description": "test description",
                            "type": "string"
                        })
                    }
                }),
                "field_2": OrderedDict({
                    "type": "array",
                    "items": OrderedDict({
                        "anyOf": [{
                            "$ref": "#/properties/field_1"
                        }]
                    })
                })
            }
        })

        output_json = self.compiler.resolve_schema_references(schema, loaded_schemas)
        eq_(output_json, expected_output)

        output_json = self.compiler.resolve_schema_references(schema, loaded_schemas, "123")
        eq_(output_json, expected_output)
