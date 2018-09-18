import unittest
from semDiff.fullDiff import FullSemDiff

DATS_contexts = {
    "person_schema.json": {
        "sdo": "https://schema.org/",
        "Person": "sdo:Person",
        "identifier": "sdo:identifier",
        "firstName": "sdo:givenName",
        "lastName": "sdo:familyName",
        "fullName": "sdo:name",
        "email": "sdo:email",
        "affiliations": "sdo:affiliation",
        "roles": "sdo:roleName"
    },
    "identifier_info_schema.json": {
        "sdo": "https://schema.org/",
        "Identifier": "sdo:Thing",
        "identifier": "sdo:identifier",
        "identifierSource": {
            "@id": "sdo:Property",
            "@type": "sdo:Text"
        }
    }
}
MIACA_contexts = {
    "source_schema.json": {
        "sdo": "https://schema.org/",
        "Source": "sdo:Person",
        "identifier": "sdo:identifier",
        "firstName": "sdo:givenName",
        "lastName": "sdo:familyName",
        "fullName": "sdo:name",
        "email": "sdo:email",
        "affiliations": "sdo:affiliation",
        "roles": "sdo:roleName"
    },
    "identifier_info_schema.json": {
        "sdo": "https://schema.org/",
        "Identifier_info": "sdo:Thing",
        "identifier": "sdo:identifier",
        "identifierSource": {
            "@id": "sdo:Property",
            "@type": "sdo:Text"
        }
    }
}
DATS_schemas = {
    "person_schema.json": {
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
    },
    "identifier_info_schema": {
    }
}
MIACA_schemas = {
    "source_schema.json": {
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
    },
    "identifier_info_schema.json": {

    }
}
networks_contexts = [DATS_contexts, MIACA_contexts]


class FullSemDiffTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FullSemDiffTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.full_diff = FullSemDiff(networks_contexts, DATS_schemas, MIACA_schemas)

    def test___init__(self):
        # Testing twin names
        self.assertTrue(self.full_diff.twins[0].twins.first_entity == 'Person')
        self.assertTrue(self.full_diff.twins[0].twins.second_entity == 'Source')

        # Testing overlap
        self.assertTrue(str(self.full_diff.twins[0].overlap['coverage'].relative_coverage)
                        == "25.0")
        self.assertTrue(str(self.full_diff.twins[0].overlap['coverage']
                            .absolute_coverage.overlap_number) == "1")
        self.assertTrue(str(self.full_diff.twins[0].overlap['coverage']
                            .absolute_coverage.total_fields) == "4")
        self.assertTrue(self.full_diff.twins[0].overlap['overlapping fields'][0].first_field
                        == "identifier")
        self.assertTrue(self.full_diff.twins[0].overlap['overlapping fields'][0].second_field
                        == "identifier")

        # Testing ignored fields
        self.assertTrue(self.full_diff.twins[0].overlap['ignored fields'][0]
                        == 'alternateIdentifiers')
