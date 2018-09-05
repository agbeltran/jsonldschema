import unittest
from SemDiff.semDiff import SemanticComparator

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
        "firstName": "sdo:givenName",
        "familyName": "sdo:familyName",
        "fullName": "sdo:name",
        "email": "sdo:email",
        "affiliations": "sdo:affiliation",
        "roles": "sdo:roleName"
    }
}


class SemDiffTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(SemDiffTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.semantic_comparator = SemanticComparator(schema_1, context_1, schema_2, context_2)

    def test___build_context_dict(self):
        schema_input = {
            "schema": schema_1,
            "context": context_1
        }

        # This is a particular structure as we are calling a private method through its reflection
        comparator = self.semantic_comparator._SemanticComparator__build_context_dict(schema_input)
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
        processed_field = self.semantic_comparator.\
            _SemanticComparator__process_field("firstName",
                                               "sdo:givenName",
                                               context_2['@context'],
                                               {})
        self.assertTrue('https://schema.org/givenName' in processed_field.keys())
        self.assertTrue(processed_field['https://schema.org/givenName'] == ['firstName'])

    def test___compute_context_coverage(self):
        schema_input = {
            "schema": schema_1,
            "context": context_1
        }
        schema_input2 = {
            "schema": schema_2,
            "context": context_2
        }

        comparator1 = self.semantic_comparator.\
            _SemanticComparator__build_context_dict(schema_input)
        comparator2 = self.semantic_comparator.\
            _SemanticComparator__build_context_dict(schema_input2)

        coverage = self.semantic_comparator.\
            _SemanticComparator__compute_context_coverage(comparator1[0], comparator2[0])

        self.assertTrue(coverage[0].relative_coverage == "50.0")
        self.assertTrue(coverage[0].absolute_coverage[0] == "2")
        self.assertTrue(coverage[0].absolute_coverage[1] == "4")
        self.assertTrue(len(coverage[1]) == 2)

        """
        self.assertTrue(coverage[1][0].first_field == 'identifier')
        self.assertTrue(coverage[1][0].second_field == 'identifier')
        self.assertTrue(coverage[1][1].first_field == 'lastName')
        self.assertTrue(coverage[1][1].second_field == 'familyName')
        """
