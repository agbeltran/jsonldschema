import unittest
import json
import os
from collections import OrderedDict
from semDiff.fullDiff import FullSemDiff, FullSemDiffMultiple

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


class FellSemDiffMultipleTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FellSemDiffMultipleTestCase, self).__init__(*args, **kwargs)
        data_path = os.path.join(os.path.dirname(__file__), "data/")
        prepared_input = os.path.join(data_path, "fullDiff_input_example.json")
        with open(prepared_input, 'r') as input_file:
            self.mapping = json.load(input_file, object_pairs_hook=OrderedDict)
            input_file.close()

    def setUp(self):
        self.full_diff = FullSemDiffMultiple(self.mapping['networks'])

    def test___init__(self):
        expected_overlaps = [
            [
                [
                    "Annotation",
                    "Annotation"
                ],
                {
                    "coverage": [
                        "100.0",
                        [
                            "2",
                            "2"
                        ]
                    ],
                    "overlapping fields": [
                        [
                            "value",
                            "value"
                        ],
                        [
                            "valueIRI",
                            "valueIRI"
                        ]
                    ],
                    "ignored fields": []
                }
            ],
            [
                [
                    "Organization",
                    "Organization"
                ],
                {
                    "coverage": [
                        "125.0",
                        [
                            "5",
                            "4"
                        ]
                    ],
                    "overlapping fields": [
                        [
                            "identifier",
                            "identifier"
                        ],
                        [
                            "name",
                            "name"
                        ],
                        [
                            "name",
                            "abbreviation"
                        ],
                        [
                            "abbreviation",
                            "name"
                        ],
                        [
                            "abbreviation",
                            "abbreviation"
                        ],
                        [
                            "location",
                            "location"
                        ],
                        [
                            "roles",
                            "roles"
                        ]
                    ],
                    "ignored fields": [
                        "alternateIdentifiers",
                        "relatedIdentifiers",
                        "extraProperties"
                    ]
                }
            ],
            [
                [
                    "Person",
                    "Person"
                ],
                {
                    "coverage": [
                        "100.0",
                        [
                            "7",
                            "7"
                        ]
                    ],
                    "overlapping fields": [
                        [
                            "identifier",
                            "identifier"
                        ],
                        [
                            "fullName",
                            "fullName"
                        ],
                        [
                            "firstName",
                            "firstName"
                        ],
                        [
                            "lastName",
                            "lastName"
                        ],
                        [
                            "email",
                            "email"
                        ],
                        [
                            "affiliations",
                            "affiliations"
                        ],
                        [
                            "roles",
                            "roles"
                        ]
                    ],
                    "ignored fields": [
                        "alternateIdentifiers",
                        "relatedIdentifiers",
                        "middleInitial",
                        "extraProperties"
                    ]
                }
            ],
            [
                [
                    "Place",
                    "Place"
                ],
                {
                    "coverage": [
                        "100.0",
                        [
                            "6",
                            "6"
                        ]
                    ],
                    "overlapping fields": [
                        [
                            "identifier",
                            "identifier"
                        ],
                        [
                            "name",
                            "name"
                        ],
                        [
                            "description",
                            "description"
                        ],
                        [
                            "postalAddress",
                            "postalAddress"
                        ],
                        [
                            "geometry",
                            "geometry"
                        ],
                        [
                            "coordinates",
                            "coordinates"
                        ]
                    ],
                    "ignored fields": [
                        "alternateIdentifiers",
                        "relatedIdentifiers"
                    ]
                }
            ]
        ]

        self.assertTrue(len(self.full_diff.output[0][0]) == 0)
        self.assertTrue(len(self.full_diff.output[1][0]) == 0)

        expected_overlaps_as_string = json.dumps(expected_overlaps)
        for item in self.full_diff.output[0][1]:
            print(json.dumps(item))
            print(expected_overlaps_as_string)
            self.assertTrue(json.dumps(item) in expected_overlaps_as_string)
