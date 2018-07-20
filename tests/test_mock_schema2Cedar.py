from mock import patch
from nose.tools import assert_true, eq_
from cedar.schema2Cedar import Schema2CedarTemplate, Schema2CedarTemplateElement
import os
import json
from random import randint


class TestSchema2Cedar(object):
    @classmethod
    def setup_class(cls):
        cls.cedarTemplate = Schema2CedarTemplate()
        cls.cedarTemplateElement = Schema2CedarTemplateElement()

        cls.mock_request_patcher = patch('cedar.schema2Cedar.requests.request')
        cls.mock_json_patcher = patch('cedar.schema2Cedar.json.loads')

        cls.mock_request = cls.mock_request_patcher.start()
        cls.mock_json = cls.mock_json_patcher.start()

    @classmethod
    def teardown_class(cls):
        cls.mock_request_patcher.stop()
        cls.mock_json_patcher.stop()

    def test_convert_template(self):
        self.mock_request.return_value.status_code = 200
        response = self.cedarTemplate.convert_template("tests/data/schema.json")
        assert_true(response)

    def test_convert_template_element(self):
        self.mock_request.return_value.status_code = 200
        response = self.cedarTemplateElement.convert_template_element("tests/data/schema.json")
        assert_true(response)
