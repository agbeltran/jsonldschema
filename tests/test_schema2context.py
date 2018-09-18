import unittest
from utils.schema2context import create_context_template, process_schema_name

person_schema = {
    "id": "https://w3id.org/dats/schema/person_schema.json",
    "$schema": "http://json-schema.org/draft-04/schema",
    "title": "DATS person schema",
    "description": "A human being",
    "type": "object",
    "properties": {
        "@context": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "object"
                }
            ]
        },
        "@id": {"type": "string", "format": "uri"},
        "@type": {"type": "string", "format": "uri"},
        "identifier": {
            "description": "Primary identifier for the person.",
            "$ref": "identifier_info_schema.json#"
        },
        "lastName": {
            "description": "The person's family name.",
            "type": "string"
        }
    },
    "additionalProperties": False
}
schema_name = 'identifier_info_schema.json'
base = {
    "sdo": "https://schema.org",
    "obo": "http://purl.obolibrary.org/obo/"
}


class TestSchema2Context(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestSchema2Context, self).__init__(*args, **kwargs)

    def test_create_context_template(self):
        new_context = create_context_template(person_schema, base, process_schema_name(schema_name))
        self.assertTrue(list(new_context.keys())[0] == 'sdo')
        self.assertTrue(list(new_context.keys())[1] == 'obo')

        self.assertTrue('sdo' in new_context['sdo']["@context"].keys())
        self.assertTrue(new_context['sdo']["@context"]['sdo'] == "https://schema.org")
        self.assertTrue('IdentifierInfo' in new_context['sdo']["@context"].keys())
        self.assertTrue(new_context['sdo']["@context"]['@language'] == 'en')
        self.assertTrue('lastName' in new_context['sdo']["@context"].keys())
        self.assertTrue('identifier' in new_context['sdo']["@context"].keys())

        self.assertTrue('obo' in new_context['obo']["@context"].keys())
        self.assertTrue(new_context['obo']["@context"]['obo'] == "http://purl.obolibrary.org/obo/")
        self.assertTrue('IdentifierInfo' in new_context['obo']["@context"].keys())
        self.assertTrue(new_context['obo']["@context"]['@language'] == 'en')
        self.assertTrue('lastName' in new_context['obo']["@context"].keys())
        self.assertTrue('identifier' in new_context['obo']["@context"].keys())

    def test_process_schema_name(self):
        print(process_schema_name(schema_name))
        self.assertTrue(process_schema_name(schema_name) == "IdentifierInfo")
