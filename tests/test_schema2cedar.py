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
        cls.mock_json_patcher.stop()

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
