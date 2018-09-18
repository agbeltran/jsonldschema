import unittest
from SemDiff.mergeEntities import EntityMerge

schema_1 = {
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
        "@type": {"type": "string", "enum": ["Person"]},
        "identifier": {
            "description": "Primary identifier for the person.",
            "$ref": "identifier_info_schema.json#"
        },
        "alternateIdentifiers": {
            "description": "Alternate identifiers for the person.",
            "type": "array",
            "items": {
                "$ref": "alternate_identifier_info_schema.json#"
            }
        },
        "fullName": {
            "description": "The first name, any middle names, and surname of a person.",
            "type": "string"
        },
        "firstName": {
            "description": "The given name of the person.",
            "type": "string"
        },
        "lastName": {
            "description": "The person's family name.",
            "type": "string"
        }
    },
    "additionalProperties": False
}
context_1 = {
    "@context": {
        "sdo": "https://schema.org/",
        "Person": "sdo:Person",
        "identifier": {
            "@id": "sdo:identifier",
            "@type": "sdo:Text"
        },
        "firstName": "sdo:givenName",
        "lastName": "sdo:familyName",
        "fullName": "sdo:name",
        "email": "sdo:email",
        "affiliations": "sdo:affiliation",
        "roles": "sdo:roleName"
    }
}

schema_2 = {
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
        "familyName": {
            "description": "The person's family name.",
            "type": "string"
        }
    },
    "additionalProperties": False
}
context_2 = {
    "@context": {
        "sdo": "https://schema.org/",
        "Person": "sdo:Person",
        "identifier": {
            "@id": "sdo:identifier",
            "@type": "sdo:Text"
        },
        "familyName": "sdo:familyName",
        "email": "sdo:email",
        "affiliations": "sdo:affiliation",
        "roles": "sdo:roleName"
    }
}


class EntityMergeTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(EntityMergeTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.merge = EntityMerge(schema_2, context_2, schema_1, context_1)

    def test___init__(self):

        # Verify that all fields in schema_2 are the same in the final output schema
        for field in schema_2["properties"]:
            self.assertTrue(self.merge.output_schema["properties"][field] == schema_2[
                "properties"][field])

        # Verify that all fields in context_2 are the same in the final output context
        for field in context_2["@context"]:
            self.assertTrue(self.merge.output_context["@context"][field] == context_2[
                "@context"][field])

        # Verify that fields from schema_1 that aren't common with schema_2 are also in the
        # final output
        self.assertTrue("alternateIdentifiers" in self.merge.output_schema["properties"].keys())
        self.assertTrue("fullName" in self.merge.output_schema["properties"].keys())
        self.assertTrue("firstName" in self.merge.output_schema["properties"].keys())

        # Verify that fields from context_1 that aren't common with context_2 are also in the
        # final output
        self.assertTrue("alternateIdentifiers" not in self.merge.output_context[
            "@context"].keys())
        self.assertTrue("fullName" in self.merge.output_context["@context"].keys())
        self.assertTrue("firstName" in self.merge.output_context["@context"].keys())