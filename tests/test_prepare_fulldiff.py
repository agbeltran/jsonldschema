import json
import unittest
from nose.tools import eq_
from mock import patch
from utils import prepare_fulldiff_input


class TestCasePrepareFullDiffInput(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestCasePrepareFullDiffInput, self).__init__(*args, **kwargs)
        self.pre_process = prepare_fulldiff_input

    @classmethod
    def teardown_class(cls):
        print("BYE")
        # cls.mock_resolver_patcher.stop()

    def test_load_context(self):
        mock_request_patcher = patch('utils.prepare_fulldiff_input.requests.get')
        mock_request = mock_request_patcher.start()

        contexts_mapping = {
            "networkName": "test1",
            "contexts": {
                "test_schema": "testerURL.com",
            }
        }

        context = {
            "@context": {
                'test': "sdo:test"
            }
        }

        class RequestMockResponse:
            text = json.dumps(context)

        expected_output = {'test_schema': {'test': 'sdo:test'}}
        mock_request.return_value = RequestMockResponse
        tested_output = self.pre_process.load_context(contexts_mapping)
        eq_(tested_output, expected_output)
        mock_request_patcher.stop()

        with self.assertRaises(Exception) as context:
            self.pre_process.load_context(contexts_mapping)
            self.assertTrue('There is a problem with your url or schema'
                            in context.exception)

    def test_resolve_network(self):
        mock_resolver_patcher = patch('utils.prepare_fulldiff_input.RefResolver.resolve')
        mock_resolver = mock_resolver_patcher.start()
        mock_request_patcher = patch('utils.prepare_fulldiff_input.requests.get')
        mock_request = mock_request_patcher.start()

        schema_url = "http://justatest.com"
        schema = {
            "id": "schemas/test.json#",
            "definitions": {
                "field_1": {"$ref": "second_test.json#"}
            },
            "properties": {
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
            }
        }

        mock_resolver.return_value = ["", {
            "id": "schemas/second_test.json",
            "properties": {
                "name": {
                    "description": "test description",
                    "type": "string"
                }
            }
        }]

        expected_output = {
            "test.json": schema,
            "second_test.json": mock_resolver.return_value[1]
        }

        class RequestMockResponse:
            text = json.dumps(schema)

        mock_request.return_value = RequestMockResponse
        tested_output = self.pre_process.resolve_network(schema_url)
        eq_(tested_output, expected_output)
        mock_request_patcher.stop()

        with self.assertRaises(Exception) as context:
            self.pre_process.resolve_network(schema_url)
            self.assertTrue('There is a problem with your url or schema'
                            in context.exception)
        mock_resolver_patcher.stop()

    def test_prepare_multiple_input(self):
        mock_resolve_network_patcher = patch('utils.prepare_fulldiff_input.resolve_network')
        mock_resolve_network = mock_resolve_network_patcher.start()
        mock_resolve_network.return_value = {
            "person_schema": "https://w3id.org/dats/schema/person_schema.json"
        }

        mock_load_context_patcher = patch('utils.prepare_fulldiff_input.load_context')
        mock_load_context = mock_load_context_patcher.start()
        mock_load_context.return_value = {
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
            }
        }

        expected_output = {
            'networks': [
                {
                    'schemas': {
                        'person_schema': 'https://w3id.org/dats/schema/person_schema.json'
                    },
                    'name': 'DATS',
                    'contexts': {
                        'person_schema.json': {
                            'sdo': 'https://schema.org/',
                            'Person': 'sdo:Person',
                            'identifier': 'sdo:identifier',
                            'firstName': 'sdo:givenName',
                            'lastName': 'sdo:familyName',
                            'fullName': 'sdo:name',
                            'email': 'sdo:email',
                            'affiliations': 'sdo:affiliation',
                            'roles': 'sdo:roleName'
                        }
                    }
                },
                {
                    'schemas': {
                        'person_schema': 'https://w3id.org/dats/schema/person_schema.json'
                    },
                    'name': 'MIACA',
                    'contexts': {
                        'person_schema.json': {
                            'sdo': 'https://schema.org/',
                            'Person': 'sdo:Person',
                            'identifier': 'sdo:identifier',
                            'firstName': 'sdo:givenName',
                            'lastName': 'sdo:familyName',
                            'fullName': 'sdo:name',
                            'email': 'sdo:email',
                            'affiliations': 'sdo:affiliation',
                            'roles': 'sdo:roleName'
                        }
                    }
                },
                {
                    'schemas': {
                        'person_schema': 'https://w3id.org/dats/schema/person_schema.json'
                    },
                    'name': 'DATS',
                    'contexts': {
                        'person_schema.json': {
                            'sdo': 'https://schema.org/',
                            'Person': 'sdo:Person',
                            'identifier': 'sdo:identifier',
                            'firstName': 'sdo:givenName',
                            'lastName': 'sdo:familyName',
                            'fullName': 'sdo:name',
                            'email': 'sdo:email',
                            'affiliations': 'sdo:affiliation',
                            'roles': 'sdo:roleName'
                        }
                    }
                }
            ]
        }

        networks_map = [
            ["https://w3id.org/dats/schema/person_schema.json", "dats_mapping.json"],
            ["https://w3id.org/mircat/miaca/schema/source_schema.json", "miaca_mapping.json"],
            ["https://w3id.org/dats/schema/person_schema.json", "dats_mapping.json"]
        ]

        input_networks = {"networks": prepare_fulldiff_input.prepare_multiple_input(networks_map)}
        self.assertTrue(input_networks == expected_output)
        mock_resolve_network_patcher.stop()
        mock_load_context_patcher.stop()

        networks_map_error = [
            ["https://w3id.org/dats/schema/person_schema.json", "123"],
            ["https://w3id.org/mircat/miaca/schema/source_schema.json", 123],
        ]

        with self.assertRaises(Exception):
            prepare_fulldiff_input.prepare_multiple_input(networks_map_error)

    def test_prepare_input(self):
        mock_resolve_network_patcher = patch('utils.prepare_fulldiff_input.resolve_network')
        mock_resolve_network = mock_resolve_network_patcher.start()
        mock_resolve_network.return_value = {
            "person_schema": "https://w3id.org/dats/schema/person_schema.json"
        }

        mock_load_context_patcher = patch('utils.prepare_fulldiff_input.load_context')
        mock_load_context = mock_load_context_patcher.start()
        mock_load_context.return_value = {
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
            }
        }

        mapping = [
            {
                "networkName": "DATS",
                "contexts": {
                    "person_schema.json": "http://w3id.org/dats/context"
                                          "/sdo/person_sdo_context.jsonld"
                }
            },
            {
                "networkName": "MIACA",
                "contexts": {
                    "person_schema.json": "http://w3id.org/dats/context"
                                          "/sdo/person_sdo_context.jsonld"
                }
            }
        ]

        expected_output = [
            {
                'schemas': {
                    'person_schema': 'https://w3id.org/dats/schema/person_schema.json'
                },
                'name': 'DATS',
                'contexts': {
                    'person_schema.json': {
                        'sdo': 'https://schema.org/',
                        'Person': 'sdo:Person',
                        'identifier': 'sdo:identifier',
                        'firstName': 'sdo:givenName',
                        'lastName': 'sdo:familyName',
                        'fullName': 'sdo:name',
                        'email': 'sdo:email',
                        'affiliations': 'sdo:affiliation',
                        'roles': 'sdo:roleName'
                    }
                }
            },
            {
                'schemas': {
                    'person_schema': 'https://w3id.org/dats/schema/person_schema.json'
                },
                'name': 'MIACA',
                'contexts': {
                    'person_schema.json': {
                        'sdo': 'https://schema.org/',
                        'Person': 'sdo:Person',
                        'identifier': 'sdo:identifier',
                        'firstName': 'sdo:givenName',
                        'lastName': 'sdo:familyName',
                        'fullName': 'sdo:name',
                        'email': 'sdo:email',
                        'affiliations': 'sdo:affiliation',
                        'roles': 'sdo:roleName'
                    }
                }
            }
        ]

        input_networks = prepare_fulldiff_input.prepare_input("https://w3id.org/dats"
                                                              "/schema/person_schema.json",
                                                              "https://w3id.org/mircat/miaca"
                                                              "/schema/source_schema.json",
                                                              mapping[0],
                                                              mapping[1])
        self.assertTrue(input_networks == expected_output)

        mock_resolve_network_patcher.stop()
        mock_load_context_patcher.stop()
