import unittest
from mock import patch, mock_open
import os
import json
from utils.schema2context import (
    create_context_template,
    process_schema_name,
    create_context_template_from_url,
    create_network_context,
    prepare_input,
    create_and_save_contexts,
    generate_contexts_from_regex,
    generate_context_mapping,
    generate_labels_from_contexts,
    generate_context_mapping_dict
)


class TestSchema2Context(unittest.TestCase):

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

    schema_url = "https://w3id.org/mircat/miaca/schema/miaca_schema.json"

    regexes = {
        "/schema": "/context/obo",
        "_schema": "_obo_context",
        "json": "jsonld"
    }

    regex_error = "thisisastring"

    def __init__(self, *args, **kwargs):
        super(TestSchema2Context, self).__init__(*args, **kwargs)

    def test_create_context_template(self):
        new_context = create_context_template(self.person_schema,
                                              self.base,
                                              process_schema_name(self.schema_name))
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
        self.assertTrue(process_schema_name(self.schema_name) == "IdentifierInfo")

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

        context = create_context_template_from_url(url, self.base)

        self.assertTrue('sdo' in context.keys())
        self.assertTrue('obo' in context.keys())
        self.assertTrue('@context' in context['sdo'].keys()
                        and '@context' in context['obo'].keys())
        self.assertTrue('Person' in context['sdo']["@context"].keys()
                        and 'Person' in context['obo']["@context"].keys())

        self.mock_request.return_value.status_code = 400
        context_error_1 = create_context_template_from_url(url, self.base)
        self.assertTrue(isinstance(context_error_1, Exception))

        context_error_2 = create_context_template_from_url("123", self.base)
        self.assertTrue(isinstance(context_error_2, Exception))

        self.mock_request_patcher.stop()
        self.mock_json_load_patcher.stop()

        context_error_3 = create_context_template_from_url("123", self.base)
        self.assertTrue(context_error_3)

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
                "properties": {}
            }

            self.mock_resolver_patcher = patch('utils.schema2context.resolve_network')
            self.mock_resolver = self.mock_resolver_patcher.start()
            self.mock_resolver.return_value = {
                "application_schema": {
                    "id": "https://w3id.org/mircat/miaca/schema/application_schema.json"},
                "array_schema": {
                    "id": "https://w3id.org/mircat/miaca/schema/array_schema.json"},
                "miaca_schema": {
                    "id": "https://fairsharing.github.io/mircat/miaca/schema/miaca_schema.json"},
                "project_schema": {
                    "id": "https://fairsharing.github.io/mircat/miaca/schema/project_schema.json"},
                "source_schema": {
                    "id": "https://fairsharing.github.io/mircat/miaca/schema/source_schema.json"}
            }

            mapping = prepare_input("https://w3id.org/dats/schema/person_schema.json", "DATS")
            contexts = create_network_context(mapping, self.base)

            self.mock_request_patcher.stop()
            self.mock_makedir_patcher.stop()
            self.mock_json_load_patcher.stop()
            self.mock_resolver_patcher.stop()
            self.assertTrue(contexts == expected_output)

    def test_create_and_save_contexts(self):
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
                "properties": {}
            }

            self.mock_resolver_patcher = patch('utils.schema2context.resolve_network')
            self.mock_resolver = self.mock_resolver_patcher.start()
            self.mock_resolver.return_value = {
                "application_schema": {
                    "id": "https://w3id.org/mircat/miaca/schema/application_schema.json"},
                "array_schema": {
                    "id": "https://w3id.org/mircat/miaca/schema/array_schema.json"},
                "miaca_schema": {
                    "id": "https://fairsharing.github.io/mircat/miaca/schema/miaca_schema.json"},
                "project_schema": {
                    "id": "https://fairsharing.github.io/mircat/miaca/schema/project_schema.json"},
                "source_schema": {
                    "id": "https://fairsharing.github.io/mircat/miaca/schema/source_schema.json"}
            }

            mapping = prepare_input("https://w3id.org/dats/schema/person_schema.json", "DATS")
            output_directory = os.path.join(os.path.dirname(__file__), "../data/contexts")
            contexts = create_and_save_contexts(mapping, self.base, output_directory)

            with self.assertRaises(Exception) as context:
                create_and_save_contexts(mapping, self.base, [output_directory])
                self.assertTrue("Please provide a valid path to your directory"
                                in context.exception)

            self.mock_request_patcher.stop()
            self.mock_makedir_patcher.stop()
            self.mock_json_load_patcher.stop()
            self.mock_resolver_patcher.stop()
            self.assertTrue(contexts == expected_output)

    def test_prepare_input(self):

        self.mock_resolver_patcher = patch('utils.schema2context.resolve_network')
        self.mock_resolver = self.mock_resolver_patcher.start()
        self.mock_resolver.return_value = {
            "person_schema.json": {
                "id": "https://w3id.org/dats/schema/person_schema.json"
            },
            "identifier_info_schema.json": {
                "id": "https://w3id.org/dats/schema/identifier_info_schema.json"
            },
            "alternate_identifier_info_schema.json": {
                "id": "https://w3id.org/dats/schema/alternate_identifier_info_schema.json"
            },
            "related_identifier_info_schema.json": {
                "id": "https://w3id.org/dats/schema/related_identifier_info_schema.json"
            },
            "organization_schema.json": {
                "id": "https://w3id.org/dats/schema/organization_schema.json"
            },
            "annotation_schema.json": {
                "id": "https://w3id.org/dats/schema/annotation_schema.json"
            },
            "category_values_pair_schema.json": {
                "id": "https://w3id.org/dats/schema/category_values_pair_schema.json"
            }
        }

        network_name = "DATS"

        expected_output = {
            "networkName": "DATS",
            "schemas": {
                "person_schema.json":
                    "https://w3id.org/dats/schema/person_schema.json",
                "identifier_info_schema.json":
                    "https://w3id.org/dats/schema/identifier_info_schema.json",
                "alternate_identifier_info_schema.json":
                    "https://w3id.org/dats/schema/alternate_identifier_info_schema.json",
                "related_identifier_info_schema.json":
                    "https://w3id.org/dats/schema/related_identifier_info_schema.json",
                "organization_schema.json":
                    "https://w3id.org/dats/schema/organization_schema.json",
                "annotation_schema.json":
                    "https://w3id.org/dats/schema/annotation_schema.json",
                "category_values_pair_schema.json":
                    "https://w3id.org/dats/schema/category_values_pair_schema.json"
            }
        }
        url = "https://w3id.org/dats/schema/person_schema.json"
        mapping_variable = prepare_input(url, network_name)

        self.assertTrue(mapping_variable == expected_output)

        self.mock_resolver_patcher.stop()

        second_url = "test123"
        with self.assertRaises(Exception) as context:
            prepare_input(second_url, network_name)
            self.assertTrue("Error with one or more schemas"
                            in context.exception)

    def test_generate_contexts_from_regex(self):
        context = generate_contexts_from_regex(self.schema_url, self.regexes)
        self.assertTrue(context ==
                        "https://w3id.org/mircat/miaca/context/obo/miaca_obo_context.jsonld")

    def test_generate_contexts_from_regex_error(self):
        with self.assertRaises(Exception) as context:
            generate_contexts_from_regex(self.schema_url, self.regex_error)
            self.assertTrue("There is a problem with your input"
                            in context.exception)

    def test_generate_context_mapping(self):
        mock_resolver_patcher = patch("utils.schema2context.resolve_network")
        mock_resolver = mock_resolver_patcher.start()
        mock_resolver.return_value = {
            "miaca_schema.json": {
                "id": "https://w3id.org/mircat/miaca/schema/miaca_schema.json"
            },
            "test_schema.json": {
                "id": "https://w3id.org/mircat/miaca/schema/test_schema.json"
            }
        }
        context_mapping = generate_context_mapping(self.schema_url, self.regexes)

        expected_output = [
            {
                "miaca_schema.json": "https://w3id.org/mircat/miaca/context/obo/"
                                     "miaca_obo_context.jsonld",
                "test_schema.json": "https://w3id.org/mircat/miaca/context/obo/"
                                    "test_obo_context.jsonld"
            },
            {
                "miaca_schema.json": {
                    "id": "https://w3id.org/mircat/miaca/schema/miaca_schema.json"
                },
                "test_schema.json": {
                    "id": "https://w3id.org/mircat/miaca/schema/test_schema.json"
                }
            }
        ]

        self.assertTrue(json.dumps(context_mapping) == json.dumps(expected_output))

        with self.assertRaises(Exception) as context:
            generate_context_mapping(self.schema_url, self.regex_error)
            self.assertTrue("There is a problem with your input"
                            in context.exception)

        mock_resolver_patcher.stop()

    def test_generate_labels_from_contexts(self):

        side_effect = [
            MockedRequest(None, 200),
            MockedRequest(None, 200),
            MockedRequest(None, 400),
            MockedRequest("minimum information standard", 200),
            MockedRequest("planned process", 200),
            MockedRequest("Raw Image", 200),
            MockErrorRequest()
        ]

        mock_request_patcher = patch("utils.schema2context.requests.get", side_effect=side_effect)
        mock_request_patcher.start()

        context = {
            'miacme_schema.json': {
                "@context": {
                    'obo': 'http://purl.obolibrary.org/obo/',
                    "edam": "http://edamontology.org/",
                    '@language': 'en',
                    "400field": "obo:OBI_noID",
                    "BlankField": "",
                    "NoneField": None
                }
            }
        }

        labels = generate_labels_from_contexts(context, {})
        self.assertTrue(labels == {
            "http://purl.obolibrary.org/obo/": None,
            "http://edamontology.org/": None,
            "obo:OBI_noID": None
        })

        context_step_2 = {
            'miacme_schema.json': {
                'obo': 'http://purl.obolibrary.org/obo/',
                'Miacme': 'obo:MS_1000900',
            }
        }
        labels = generate_labels_from_contexts(context_step_2, labels)
        print(labels)
        self.assertTrue(labels['obo:MS_1000900'] == "minimum information standard")

        context_step_3 = {
            'miacme_schema.json': {
                'obo': 'http://purl.obolibrary.org/obo/',
                'investigation': 'obo:OBI_0000011',
            }
        }
        labels = generate_labels_from_contexts(context_step_3, labels)
        self.assertTrue(labels['obo:OBI_0000011'] == "planned process")

        context_step_4 = {
            'miacme_schema.json': {
                'edam': 'http://edamontology.org/',
                'image': "edam:data_3424",
            }
        }
        labels = generate_labels_from_contexts(context_step_4, labels)
        self.assertTrue(labels['edam:data_3424'] == "Raw Image")

        context_step_4 = {
            'miacme_schema.json': {
                'obo': 'http://purl.obolibrary.org/obo/',
                'errorTest': 'obo:OBI_errorTest',
            }
        }
        labels = generate_labels_from_contexts(context_step_4, labels)
        self.assertTrue(labels['obo:OBI_errorTest'] is None)

        mock_request_patcher.stop()

    def test_generate_context_mapping_dict(self):
        generate_mapping_patcher = patch("utils.schema2context.generate_context_mapping")
        generate_mapping = generate_mapping_patcher.start()
        generate_mapping.return_value = [
            {
                "miaca_schema.json": "https://w3id.org/mircat/miaca/context/"
                                     "obo/miaca_context_obo.jsonld",
            },
            {
                "miaca_schema.json": {
                    "id": "https://w3id.org/mircat/miaca/schema/miaca_schema.json",
                    "$schema": "http://json-schema.org/draft-04/schema",
                    "title": "MIACA (Minimum Information about a Cellular Assay) schema",
                    "description": "JSON-schema representing MIACA reporting guideline.",
                    "type": "object",
                    "_provenance": {
                        "url": "http://w3id.org/mircat/miaca/provenance.json"
                    },
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
                                "Miaca"
                            ]
                        },
                        "project": {
                            "description": "Conditions that have been established to  ...",
                            "$ref": "project_schema.json#"
                        }
                    }
                }
            }
        ]

        expected_output = {
            'networkName': 'MIACA',
            'contexts': {
                'miaca_schema.json':
                    'https://w3id.org/mircat/miaca/context/obo/miaca_context_obo.jsonld'
            },
            'schemas': {
                'miaca_schema.json': 'https://w3id.org/mircat/miaca/schema/miaca_schema.json'
            },
            'labels': {
                "obo:OBI_0000011": "planned process"
            }
        }

        context = {
           "@context": {
                "obo": "http://purl.obolibrary.org/obo/",
                "Miaca": "obo:MS_1000900",
                "@language": "en",
                "project": "obo:OBI_0000011"
            }
        }

        return_value = {
            "obo:OBI_0000011": "planned process"
        }

        side_effect = [
            context,
            Exception("No json could be found at given URL")
        ]

        mock_generate_labels_patcher = patch("utils.schema2context.generate_labels_from_contexts",
                                             return_value=return_value)
        mock_generate_labels_patcher.start()

        mock_get_json_from_url_patcher = patch("utils.schema2context.get_json_from_url",
                                               side_effect=side_effect)
        mock_get_json_from_url_patcher.start()

        mapping = generate_context_mapping_dict(self.schema_url, self.regexes, "MIACA")
        mock_generate_labels_patcher.stop()
        mock_get_json_from_url_patcher.stop()
        print(json.dumps(mapping[0]))

        self.assertTrue(json.dumps(mapping[0]) == json.dumps(expected_output))

        with self.assertRaises(Exception) as result:
            generate_context_mapping_dict(self.schema_url, self.regexes, "MIACA")
            self.assertTrue("No json could be found at given URL"
                            in result.exception)


class MockedRequest:

    def __init__(self, return_value, status_code):
        self.text = json.dumps({"label": return_value})
        self.status_code = status_code


class MockErrorRequest:

    def __init__(self):
        self.text = json.dumps({"123": "456"})
        self.status_code = 200
