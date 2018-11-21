from nose.tools import assert_true
import os
import mock
import jsonbender
from validate.miflowcyt_validate import FlowRepoClient

map_file = os.path.join(os.path.dirname(__file__),
                        "../tests/data/MiFlowCyt/experiment_mapping.json")
base_schema = "experiment_schema.json"
range_limit = 1


class TestFlowRepoClient(object):

    @classmethod
    def setup_class(cls):
        cls.client = FlowRepoClient(map_file, base_schema, "this is a fake ID")
        cls.mock_request_patcher = mock.patch('validate.miflowcyt_validate.requests.request')
        cls.mock_request = cls.mock_request_patcher.start()

        cls.mock_xmljson_patcher = mock.patch('validate.miflowcyt_validate.xmljson.parker.data')
        cls.mock_xmljson = cls.mock_xmljson_patcher.start()

        cls.mock_etree_patcher = mock.patch('validate.miflowcyt_validate.elemTree.fromstring')
        cls.mock_etree = cls.mock_etree_patcher.start()

    @classmethod
    def teardown_class(cls):
        cls.mock_request_patcher.stop()
        cls.mock_xmljson_patcher.stop()
        cls.mock_etree_patcher.stop()

    def test_get_mapping(self):
        mapping = self.client.get_mapping(map_file)
        assert_true(isinstance(mapping['date'], jsonbender.selectors.OptionalS))
        assert_true(isinstance(mapping['keywords'], jsonbender.selectors.OptionalS))
        assert_true(isinstance(mapping['other'], jsonbender.selectors.OptionalS))
        assert_true(isinstance(mapping['primaryContact'], jsonbender.selectors.S))
        assert_true(isinstance(mapping['organization'], jsonbender.selectors.S))
        assert_true(isinstance(mapping['purpose'], jsonbender.selectors.OptionalS))
        assert_true(isinstance(mapping['qualityControlMeasures'], jsonbender.selectors.OptionalS))
        assert_true(isinstance(mapping['conclusions'], jsonbender.selectors.K))
        assert_true(isinstance(mapping['experimentVariables'], jsonbender.selectors.OptionalS))

        map_file_error = os.path.join(os.path.dirname(__file__),
                                      "../tests/data/MiFlowCyt/_mapping.json")
        error = self.client.get_mapping(map_file_error)
        assert_true(isinstance(error, Exception))

    def test_grab_user_content(self):
        self.mock_request.return_value.status_code = 200
        response = self.client.grab_user_content(self.client.clientID)
        assert_true(response.status_code == 200)

    def test_get_user_content_id(self):
        self.mock_request.return_value.status_code = 200
        self.mock_xmljson.return_value = {
            "public-experiments": {
                "experiment": [
                    {"id": "123"},
                    {"id": "456"}
                ]
            }
        }
        ids = self.client.get_user_content_id(self.client.clientID)
        assert_true('123' in ids)
        assert_true('456' in ids)

    def test_grab_experiment_from_api(self):
        self.mock_request.return_value.status_code = 200
        item_metadata = self.client.grab_experiment_from_api(self.client.clientID, "123")
        assert_true(item_metadata.status_code == 200)

    def test_validate_instance_from_file(self):
        validation = self.client.validate_instance_from_file({"test": "test"}, "test",
                                                             "test.test")
        assert_true(isinstance(validation, Exception))

    def test_make_validation(self):
        self.mock_request.return_value.status_code = 401
        validation = self.client.make_validation(1)
        assert_true(isinstance(validation, Exception))
