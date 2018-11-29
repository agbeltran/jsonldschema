import unittest
from mock import patch, mock_open
from utils.schema2context import create_context_template, \
    process_schema_name, \
    create_context_template_from_url, \
    create_network_context

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
        new_context = create_context_template(person_schema,
                                              base,
                                              process_schema_name(schema_name))
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
        self.assertTrue(process_schema_name(schema_name) == "IdentifierInfo")

    def test_create_context_template_from_url(self):
        url = "https://w3id.org/dats/schema/person_schema.json"

        self.mock_request_patcher = patch('utils.schema2context.requests.get')
        self.mock_request = self.mock_request_patcher.start()
        self.mock_request.return_value.status_code = 200

        self.mock_json_load_patcher = patch('utils.schema2context.json.loads')
        self.mock_json_load = self.mock_json_load_patcher.start()
        self.mock_json_load.return_value = {
            "id": url,
            "properties": {}
        }

        context = create_context_template_from_url(url, base)

        self.assertTrue('sdo' in context.keys())
        self.assertTrue('obo' in context.keys())
        self.assertTrue('@context' in context['sdo'].keys()
                        and '@context' in context['obo'].keys())
        self.assertTrue('Person' in context['sdo']["@context"].keys()
                        and 'Person' in context['obo']["@context"].keys())

        self.mock_request.return_value.status_code = 400
        context_error_1 = create_context_template_from_url(url, base)
        self.assertTrue(isinstance(context_error_1, Exception))
        self.mock_request_patcher.stop()

        context_error_2 = create_context_template_from_url("123", base)
        self.assertTrue(isinstance(context_error_2, Exception))
        self.mock_json_load_patcher.stop()

    def test_create_network_context(self):

        expected_output = {
            "application_schema": {
                "sdo": {
                    "@context": {
                        "sdo": "https://schema.org",
                        "Person": "sdo:",
                        "@language": "en"
                    }
                },
                "obo": {
                    "@context": {
                        "obo": "http://purl.obolibrary.org/obo/",
                        "Person": "obo:",
                        "@language": "en"
                    }
                }
            },
            "array_schema": {
                "sdo": {
                    "@context": {
                        "sdo": "https://schema.org",
                        "Person": "sdo:",
                        "@language": "en"
                    }
                },
                "obo": {
                    "@context": {
                        "obo": "http://purl.obolibrary.org/obo/",
                        "Person": "obo:",
                        "@language": "en"
                    }
                }
            },
            "miaca_schema": {
                "sdo": {
                    "@context": {
                        "sdo": "https://schema.org",
                        "Person": "sdo:",
                        "@language": "en"
                    }
                },
                "obo": {
                    "@context": {
                        "obo": "http://purl.obolibrary.org/obo/",
                        "Person": "obo:",
                        "@language": "en"
                    }
                }
            },
            "project_schema": {
                "sdo": {
                    "@context": {
                        "sdo": "https://schema.org",
                        "Person": "sdo:",
                        "@language": "en"
                    }
                },
                "obo": {
                    "@context": {
                        "obo": "http://purl.obolibrary.org/obo/",
                        "Person": "obo:",
                        "@language": "en"
                    }
                }
            },
            "source_schema": {
                "sdo": {
                    "@context": {
                        "sdo": "https://schema.org",
                        "Person": "sdo:",
                        "@language": "en"
                    }
                },
                "obo": {
                    "@context": {
                        "obo": "http://purl.obolibrary.org/obo/",
                        "Person": "obo:",
                        "@language": "en"
                    }
                }
            }
        }

        self.mock_request_patcher = patch('utils.schema2context.requests.get')
        self.mock_request = self.mock_request_patcher.start()
        self.mock_request.return_value.status_code = 200

        self.mock_makedir_patcher = patch('os.makedirs')
        self.mock_makedir = self.mock_makedir_patcher.start()
        self.mock_makedir.return_value = True

        with patch('builtins.open', new_callable=mock_open()):
            self.mock_json_load_patcher = patch('utils.schema2context.json.loads')
            self.mock_json_load = self.mock_json_load_patcher.start()
            self.mock_json_load.return_value = {
                "id": "https://w3id.org/dats/schema/person_schema.json",
                "networkName": "MIACA",
                "schemas": {
                    "application_schema":
                        "https://w3id.org/mircat/miaca/schema/application_schema.json",
                    "array_schema":
                        "https://w3id.org/mircat/miaca/schema/array_schema.json",
                    "miaca_schema":
                        "https://fairsharing.github.io/mircat/miaca/schema/miaca_schema.json",
                    "project_schema":
                        "https://fairsharing.github.io/mircat/miaca/schema/project_schema.json",
                    "source_schema":
                        "https://fairsharing.github.io/mircat/miaca/schema/source_schema.json"
                },
                "properties": {}
            }

            contexts = create_network_context("miaca_schemas_mapping.json", base)
            self.mock_request_patcher.stop()
            self.mock_makedir_patcher.stop()
            self.mock_json_load_patcher.stop()
            self.assertTrue(contexts == expected_output)
