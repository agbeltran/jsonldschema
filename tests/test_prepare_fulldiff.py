import json
import unittest
from nose.tools import eq_
from mock import patch
from utils import prepare_fulldiff_input


class TestCasePrepareFullDiffInput(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestCasePrepareFullDiffInput, self).__init__(*args, **kwargs)
        self.pre_process = prepare_fulldiff_input

    """
    @classmethod
    def setup_class(cls):
        cls.mock_resolver_patcher = patch('utils.prepare_fulldiff_input.RefResolver.resolve')
        cls.mock_resolver = cls.mock_resolver_patcher.start()

        cls.mock_request_patcher = patch('utils.prepare_fulldiff_input.requests.get')
        cls.mock_request = cls.mock_request_patcher.start()

        cls.pre_process = prepare_fulldiff_input
    """

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
            "@context":  {
                'test': "sdo:test"
            }
        }

        class RequestMockResponse:
            text = json.dumps(context)

        expected_output = {'test_schema.json': {'test': 'sdo:test'}}
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

        schema_url = "justatest.com"
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
