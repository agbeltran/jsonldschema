import unittest
import json
import os
from collections import OrderedDict
from mock import patch
from semDiff.fullDiff import FullSemDiff, FullSemDiffMultiple, FullDiffGenerator

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
        self.assertTrue(len(self.full_diff.output[0]) == 2)
        self.assertTrue(len(self.full_diff.output[0][0]) == 0)
        self.assertTrue(len(self.full_diff.output[1]) == 1)
        self.assertTrue(len(self.full_diff.output[1][0]) == 0)
        self.assertTrue(len(self.full_diff.output) == 2)


class FullDiffGeneratorTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FullDiffGeneratorTestCase, self).__init__(*args, **kwargs)

    def test__init_(self):

        mock_resolver_patcher = patch('semDiff.fullDiff.generate_context_mapping')
        mock_resolver = mock_resolver_patcher.start()
        mock_resolver.return_value = [
            {
                "miacme_schema.json": "https://w3id.org/mircat/miacme/"
                                      "context/obo/miacme_obo_context.jsonld"
            },
            {
                "miacme_schema.json": {
                    "id": "https://w3id.org/mircat/miacme/schema/miacme_schema.json",
                    "$schema": "http://json-schema.org/draft-04/schema",
                    "title": "MIACME schema",
                    "version": "1.0",
                    "description": "JSON-schema representing MIACME reporting guideline.",
                    "type": "object",
                    "properties": {
                        "@context": {
                            "description": "The JSON-LD context",
                            "anyOf": [
                                {
                                    "type": "string"
                                },
                                {
                                    "type": "object"
                                },
                                {
                                    "type": "array"
                                }
                            ]
                        },
                        "@id": {
                            "description": "The JSON-LD identifier",
                            "type": "string",
                            "format": "uri"
                        },
                        "@type": {
                            "description": "The JSON-LD type",
                            "type": "string",
                            "enum": [
                                "Miacme"
                            ]
                        },
                        "investigation": {
                            "$ref": "investigation_schema.json#"
                        }
                    }
                }
            }
        ]

        mock_context_loader_patcher = patch('semDiff.fullDiff.load_context')
        mock_context_loader = mock_context_loader_patcher.start()
        mock_context_loader.return_value = {
            'miacme_schema.json': {
                'obo': 'http://purl.obolibrary.org/obo/',
                'Miacme': 'obo:MS_1000900',
                '@language': 'en',
                'investigation': 'obo:OBI_0000011'
            }
        }

        mock_label_loader_patcher = patch('semDiff.fullDiff.generate_labels_from_contexts')
        mock_label_loader = mock_label_loader_patcher.start()
        mock_label_loader.return_value = {
            'http://purl.obolibrary.org/obo/': None,
            'obo:MS_1000900': 'minimum information standard',
            'obo:OBI_0000011': 'planned process'
        }

        regex = {
            "/schema": "/context/obo",
            "_schema.json": "_obo_context.jsonld"
        }
        network = {
            "url": "https://w3id.org/mircat/miacme/schema/miacme_schema.json",
            "regex": regex,
            "name": "MIACME"
        }
        report = FullDiffGenerator(network, network)

        # Testing networks
        self.assertTrue(report.json["network1"]["name"] == "MIACME")
        self.assertTrue(report.json["network1"]["schemas"] == mock_resolver.return_value[1])
        self.assertTrue(report.json["network1"]["contexts"] == mock_context_loader.return_value)
        self.assertTrue(report.json["network1"] == report.json["network2"])

        # Testing labels
        self.assertTrue(report.json["labels"] == mock_label_loader.return_value)

        # Testing overlaps
        self.assertTrue(report.json["overlaps"][0].twins.first_entity == "Miacme")
        self.assertTrue(report.json["overlaps"][0].twins.first_entity ==
                        report.json["overlaps"][0].twins.second_entity)
        self.assertTrue(report.json["overlaps"][0].twins.first_entity == "Miacme")
        self.assertTrue(report.json["overlaps"][0].overlap['coverage'].relative_coverage == "100.0")
        self.assertTrue(report.json["overlaps"][0].overlap['coverage'].absolute_coverage.overlap_number == "1")
        self.assertTrue(report.json["overlaps"][0].overlap['coverage'].absolute_coverage.total_fields == "1")
        self.assertTrue(report.json["overlaps"][0].overlap['overlapping fields'][0].first_field == "investigation")
        self.assertTrue(report.json["overlaps"][0].overlap['overlapping fields'][0].first_field ==
                        report.json["overlaps"][0].overlap['overlapping fields'][0].second_field)
