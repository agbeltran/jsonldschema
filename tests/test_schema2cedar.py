from mock import patch
import json
from nose.tools import assert_true
from cedar.schema2cedar import Schema2CedarTemplate, Schema2CedarTemplateElement
from random import randint
import os

production_api_key = str(randint(1, 100))
folder_id = str(randint(1, 100))
user_id = str(randint(1, 100))


class TestSchema2Cedar(object):

    @classmethod
    def setup_class(cls):
        cls.cedarTemplate = Schema2CedarTemplate(production_api_key, folder_id, user_id)
        cls.cedarTemplateElement = Schema2CedarTemplateElement(production_api_key,
                                                               folder_id,
                                                               user_id)

        cls.mock_request_patcher = patch('cedar.schema2cedar.requests.request')
        cls.mock_json_patcher = patch('cedar.schema2cedar.json.loads')

        cls.mock_request = cls.mock_request_patcher.start()
        cls.mock_json = cls.mock_json_patcher.start()

    @classmethod
    def teardown_class(cls):
        cls.mock_request_patcher.stop()

    def test_convert_template(self):
        self.mock_request.return_value.status_code = 200
        path = os.path.join(os.path.dirname(__file__), "./data")
        with open(os.path.join(path, "schema.json"), 'r') as orig_schema_file:
            # Load the JSON schema and close the file
            schema_as_json = json.load(orig_schema_file)
        orig_schema_file.close()

        response = self.cedarTemplate.convert_template(schema_as_json)
        assert_true(response)

    def test_convert_template_element(self):
        self.mock_request.return_value.status_code = 200

        path = os.path.join(os.path.dirname(__file__), "./data")
        with open(os.path.join(path, "schema.json"), 'r') as orig_schema_file:
            # Load the JSON schema and close the file
            schema_as_json = json.load(orig_schema_file)
        orig_schema_file.close()

        response = self.cedarTemplateElement.convert_template_element(schema_as_json)
        assert_true(response)

    def test_set_prop_context(self):
        self.mock_json_patcher.stop()
        path = os.path.join(os.path.dirname(__file__), "./data")
        with open(os.path.join(path, "schema1.json"), 'r') as orig_schema_file:
            # Load the JSON schema and close the file
            schema_as_json = json.load(orig_schema_file)
        orig_schema_file.close()

        # testing set_prop_context
        expected_prop_context = {
            "skos": {
                "type": "string",
                "format": "uri",
                "enum": [
                    "http://www.w3.org/2004/02/skos/core#"
                ]
            },
            "skos:notation": {
                "type": "object",
                "properties": {
                    "@type": {
                        "type": "string",
                        "enum": [
                            "xsd:string"
                        ]
                    }
                }
            },
            "pav:createdOn": {
                "properties": {
                    "@type": {
                        "enum": [
                            "xsd:dateTime"
                        ],
                        "type": "string"
                    }
                },
                "type": "object"
            },
            "pav:lastUpdatedOn": {
                "properties": {
                    "@type": {
                        "enum": [
                            "xsd:dateTime"
                        ],
                        "type": "string"
                    }
                },
                "type": "object"
            },
            "pav:createdBy": {
                "properties": {
                    "@type": {
                        "enum": [
                            "@id"
                        ],
                        "type": "string"
                    }
                },
                "type": "object"
            },
            "schema:isBasedOn": {
                "properties": {
                    "@type": {
                        "enum": [
                            "@id"
                        ],
                        "type": "string"
                    }
                },
                "type": "object"
            },
            "schema:name": {
                "properties": {
                    "@type": {
                        "enum": [
                            "xsd:string"
                        ],
                        "type": "string"
                    }
                },
                "type": "object"
            },
            "schema:description": {
                "properties": {
                    "@type": {
                        "enum": [
                            "xsd:string"
                        ],
                        "type": "string"
                    }
                },
                "type": "object"
            },
            "rdfs:label": {
                "properties": {
                    "@type": {
                        "enum": [
                            "xsd:string"
                        ],
                        "type": "string"
                    }
                },
                "type": "object"
            },
            "oslc:modifiedBy": {
                "properties": {
                    "@type": {
                        "enum": [
                            "@id"
                        ],
                        "type": "string"
                    }
                },
                "type": "object"
            },
            "oslc": {
                "enum": [
                    "http://open-services.net/ns/core#"
                ],
                "type": "string",
                "format": "uri"
            },
            "schema": {
                "enum": [
                    "http://schema.org/"
                ],
                "type": "string",
                "format": "uri"
            },
            "rdfs": {
                "enum": [
                    "http://www.w3.org/2000/01/rdf-schema#"
                ],
                "type": "string",
                "format": "uri"
            },
            "pav": {
                "enum": [
                    "http://purl.org/pav/"
                ],
                "type": "string",
                "format": "uri"
            },
            "xsd": {
                "enum": [
                    "http://www.w3.org/2001/XMLSchema#"
                ],
                "type": "string",
                "format": "uri"
            },
            "identifier": {
                "enum": [
                    ""
                ]
            },
            "alternateIdentifiers": {
                "enum": [
                    ""
                ]
            },
            "fullName": {
                "enum": [
                    ""
                ]
            },
            "firstName": {
                "enum": [
                    ""
                ]
            },
            "lastName": {
                "enum": [
                    ""
                ]
            }
        }
        prop_context = self.cedarTemplate.set_prop_context(schema_as_json)
        assert_true(prop_context == expected_prop_context)

        # testing set_required_items
        with open(os.path.join(path, "expected_required_items.json"), 'r') as orig_schema_file:
            # Load the JSON schema and close the file
            expected_required_item = json.load(orig_schema_file)
        orig_schema_file.close()
        required_item = self.cedarTemplate.set_required_item(schema_as_json)
        print(json.dumps(required_item, indent=4))
        assert_true(required_item == expected_required_item)

    def test_json_pretty_dump(self):
        tested_variable = {
            "test": "test"
        }
        output_file_path = os.path.join(os.path.dirname(__file__), "data/schema.json")
        output_file = open(output_file_path, "w")
        pretty_dump = self.cedarTemplate.json_pretty_dump(tested_variable, output_file)
        output_file.close()
        assert_true(pretty_dump is None)