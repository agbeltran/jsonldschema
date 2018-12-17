import json
import os
from mock import patch
from falcon import testing

from api_client.client import (
    create_client,
    ClientBase,
    NetworkCompilerClient
)
from api_client.utility import StorageEngine


class APIClientTestCase(testing.TestCase):
    def setUp(self):
        super(APIClientTestCase, self).setUp()
        self.app = create_client()


class APIAppTest(APIClientTestCase):

    def test_base(self):
        with self.assertRaises(Exception) as context:
            db = StorageEngine()
            ClientBase(db)
            self.assertTrue("base class may not be instantiated"
                            in context.exception)

    def test_get_request_body(self):
        with self.assertRaises(Exception) as context:
            db = StorageEngine()
            test = NetworkCompilerClient(db)

            class MyCustomTest:
                pass

            test.get_request_body(MyCustomTest())

            self.assertTrue("Missing thing"
                            in context.exception)

    def test_resolve_network(self):
        mock_api_patcher = patch("api_client.utility.resolve_schema_references")
        mock_api = mock_api_patcher.start()
        mock_api.return_value = {u'message': u'Hello world!'}

        doc = {u'message': u'Hello world!'}
        api_input = {"schema_url": "https://w3id.org/dats/schema/access_schema.json"}

        result = self.simulate_get('/resolve_network', body=json.dumps(api_input))

        self.assertEqual(result.json, doc)
        mock_api_patcher.stop()

    def test_create_context(self):
        mock_api_patcher = patch("api_client.utility.resolve_network")
        mock_api = mock_api_patcher.start()
        mock_api.return_value = {
            "test.json": {
                "id": "http://example.com/test.json",
                "properties": {
                    "test1": "test1",
                    "test2": "test2"
                }
            }
        }

        expected_output = {
            "obo": {
                "http://example.com/test": {
                    "@context": {
                        "obo": "http://purl.obolibrary.org/obo/",
                        "http://example.com/test": "obo:",
                        "@language": "en",
                        "test1": "obo:",
                        "test2": "obo:"
                    }
                }
            },
            "sdo": {
                "http://example.com/test": {
                    "@context": {
                        "sdo": "http://schema.org",
                        "http://example.com/test": "sdo:",
                        "@language": "en",
                        "test1": "sdo:",
                        "test2": "sdo:"
                    }
                }
            }
        }

        error = {u'title': u'Query error, no vocabulary was provided '}

        api_input = {
            "schema_url": "https://w3id.org/dats/schema/access_schema.json",
            "vocab":  {
                "obo": "http://purl.obolibrary.org/obo/",
                "sdo": "http://schema.org"
            }
        }

        api_error_input = {
            "schema_url": "https://w3id.org/dats/schema/access_schema.json",
        }

        result = self.simulate_get('/create_context', body=json.dumps(api_input))
        result_error = self.simulate_get('/create_context', body=json.dumps(api_error_input))

        self.assertEqual(result.json, expected_output)
        self.assertEqual(result_error.json, error)
        mock_api_patcher.stop()

    def test_full_sem_diff(self):
        path = os.path.join(os.path.dirname(__file__), "./data")
        with open(os.path.join(path, "dats.json"), 'r') as dats_file:
            # Load the JSON schema and close the file
            network1 = json.load(dats_file)
            dats_file.close()

        path = os.path.join(os.path.dirname(__file__), "./data")
        with open(os.path.join(path, "miaca.json"), 'r') as miaca_file:
            # Load the JSON schema and close the file
            network2 = json.load(miaca_file)
            miaca_file.close()
        test_input = {
            "network_1": network1["schemas"],
            "network_2": network2["schemas"],
            "mapping": [network1["contexts"], network2["contexts"]]
        }

        result = self.simulate_get('/semDiff', body=json.dumps(test_input))
        self.assertEqual(result.json[0][0], [
               "Person",
               "Source"
        ])
        self.assertEqual(result.json[0][1]['coverage'], [
                "57.14",
                [
                    "4",
                    "7"
                ]
        ])

        ignored_fields = [
                "alternateIdentifiers",
                "relatedIdentifiers",
                "middleInitial",
                "extraProperties"
        ]

        for field in ignored_fields:
            self.assertTrue(field in result.json[0][1]['ignored fields'])

    def test_schema_validator(self):

        mock_request_patcher = patch("api_client.utility.requests.get")
        mock_request = mock_request_patcher.start()

        class MockedRequest:

            def __init__(self):
                path = os.path.join(os.path.dirname(__file__), "./data")
                with open(os.path.join(path, "access_schema.json"), 'r') as input_file:
                    # Load the JSON schema and close the file
                    self.text = json.dumps(json.load(input_file))
                    input_file.close()

        mock_request.return_value = MockedRequest()

        schema_url = "https://w3id.org/dats/schema/access_schema.json"
        result = self.simulate_get('/validate/schema', body=json.dumps(schema_url))
        self.assertEqual(result.json, "You schema is valid")
        mock_request_patcher.stop()

        schema_url_error = "https://w3id.org/dats/schema/access_sche"
        result2 = self.simulate_get('/validate/schema', body=json.dumps(schema_url_error))
        self.assertEqual(result2.json, "Problem loading the schema " + schema_url_error)

    def test_instance_validator(self):
        user_input = {
            "schema_url": "https://w3id.org/dats/schema/activity_schema.json",
            "instance_url": "https://w3id.org/mircat/miflowcyt/schema/sample_schema.json"
        }

        class MockedRequest:

            def __init__(self, return_value, status_code):
                self.text = json.dumps(return_value)
                self.status_code = status_code

        # Testing with correct input
        side_effect = [
            MockedRequest({"abc": "def"}, 200),
            MockedRequest({"cde": "123"}, 200)
        ]
        mock_request_patcher = patch("api_client.utility.requests.get", side_effect=side_effect)
        mock_request_patcher.start()
        result = self.simulate_get('/validate/instance', body=json.dumps(user_input))
        self.assertTrue(result.json == "Your json is valid")
        mock_request_patcher.stop()

        # Testing with 400 error on first set
        side_effect_error = [
            MockedRequest({"abc": "def"}, 400),
            MockedRequest({"cde": "123"}, 200)
        ]
        mock_request_patcher = patch("api_client.utility.requests.get",
                                     side_effect=side_effect_error)
        mock_request_patcher.start()
        result_error = self.simulate_get('/validate/instance', body=json.dumps(user_input))
        self.assertTrue(result_error.json == {'title': 'verifiy your URL ',
                                              'description':
                                                  'https://w3id.org/'
                                                  'dats/schema/activity_schema.json'})
        mock_request_patcher.stop()

        # Testing with 400 error on second set
        side_effect_error_2 = [
            MockedRequest({"abc": "def"}, 200),
            MockedRequest({"cde": "123"}, 400)
        ]
        mock_request_patcher = patch("api_client.utility.requests.get",
                                     side_effect=side_effect_error_2)
        mock_request_patcher.start()
        result_error = self.simulate_get('/validate/instance', body=json.dumps(user_input))
        self.assertTrue(result_error.json == {'title': 'verifiy your URL ',
                                              'description':
                                                  'https://w3id.org/'
                                                  'mircat/miflowcyt/schema/sample_schema.json'})
        mock_request_patcher.stop()

        # Testing with malformed json
        side_effect_error_3 = [
            MockedRequest("abc", 200),
            MockedRequest({"cde": "123"}, 200)
        ]
        mock_request_patcher = patch("api_client.utility.requests.get",
                                     side_effect=side_effect_error_3)
        mock_request_patcher.start()
        result_error = self.simulate_get('/validate/instance', body=json.dumps(user_input))
        self.assertTrue(result_error.json == {'title':
                                              'Malformed JSON, '
                                              'please verify your schema and your instance'})
        mock_request_patcher.stop()

        # Testing malformed user input
        user_input_malformed = {
            "schema_url": "abc",
            "instance_url": "sdef"
        }
        result_error = self.simulate_get('/validate/instance',
                                         body=json.dumps(user_input_malformed))
        self.assertTrue(result_error.json == {'title':
                                              'Problem loading your schema or your instance: ',
                                              'description':
                                                  "Invalid URL 'abc':"
                                                  " No schema supplied. "
                                                  "Perhaps you meant http://abc?"})

    def test_network_validator(self):
        schema_url = "https://w3id.org/dats/schema/person_schema.json"

        mock_api_patcher = patch("api_client.utility.fast_resolver")
        mock_api = mock_api_patcher.start()

        path = os.path.join(os.path.dirname(__file__), "./data")
        with open(os.path.join(path, "dats.json"), 'r') as input_file:
            # Load the JSON schema and close the file
            mock_api.return_value = json.load(input_file)['schemas']
            input_file.close()

        result = self.simulate_get("/validate/network", body=json.dumps(schema_url))
        self.assertTrue(result.json == {'person_schema.json': 'This schema is valid',
                                        'identifier_info_schema': 'This schema is valid'})
        mock_api_patcher.stop()
