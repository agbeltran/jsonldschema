from mock import patch
from nose.tools import assert_true, eq_
from cedar.client import CEDARClient
import os
import json
from random import randint


class TestClient(object):

    def __init__(self, *args, **kwargs):
        super(TestClient, self).__init__(*args, **kwargs)
        self._data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.template_path_no_id = os.path.join(self._data_dir, "example_template_no_id.json")
        self.template_path_with_id = os.path.join(self._data_dir, "example_template_with_id.json")
        self.production_api_key = str(randint(1, 100))
        self.staging_api_key = str(randint(1, 100))
        self.template_id = str(randint(1, 100))
        self.folder_id = str(randint(1, 100))

    @classmethod
    def setup_class(cls):
        cls.client = CEDARClient()
        cls.mock_request_patcher = patch('cedar.client.requests.request')
        cls.mock_request = cls.mock_request_patcher.start()

    @classmethod
    def teardown_class(cls):
        cls.mock_request_patcher.stop()

    def test_get_users(self):
        self.mock_request.return_value.status_code = 200
        response = self.client.get_users("production", self.production_api_key)
        eq_(response.status_code, 200)

    def test_get_users_staging(self):
        self.mock_request.return_value.status_code = 200
        response = self.client.get_users("staging", self.staging_api_key)
        eq_(response.status_code, 200)

    def test_get_template_content(self):
        self.mock_request.return_value.status_code = 200
        response = self.client.get_template_content("production", self.production_api_key, self.template_id)
        eq_(response.status_code, 200)

    def test_create_template(self):
        self.mock_request.return_value.status_code = 201
        with open(self.template_path_no_id, 'r') as orig_schema_file:
            # Load the JSON schema and close the file
            schema_as_json = json.load(orig_schema_file)
        orig_schema_file.close()
        response = self.client.create_template('production',
                                               self.production_api_key,
                                               self.folder_id,
                                               json.dumps(schema_as_json))
        eq_(response.status_code, 201)

    def test_update_template(self):
        self.mock_request.return_value.status_code = 200
        response = self.client.update_template("production", self.production_api_key, self.template_path_with_id)
        eq_(response.status_code, 200)

    def test_validate_template(self):
        self.mock_request.return_value["validates"] = True
        self.mock_request.return_value["warnings"] = []
        self.mock_request.return_value["errors"] = []
        with open(self.template_path_with_id, 'r') as template_content:
            template = json.load(template_content)
        response = self.client.validate_template("production", self.production_api_key, template)

        assert_true(response["validates"])
        eq_(len(response["warning"]), 0)
        eq_(len(response["errors"]), 0)

    def test_get_folder_content(self):
        self.mock_request.return_value.status_code = 200
        response = self.client.get_folder_content('production', self.production_api_key, self.folder_id)
        eq_(response.status_code, 200)

    def test_delete_folder(self):
        self.mock_request.return_value.status_code = 204
        response = self.client.delete_folder('production', self.production_api_key, self.folder_id)
        eq_(response.status_code, 204)

    def test_create_folder(self):
        self.mock_request.return_value.status_code = 201
        response = self.client.create_folder("production", self.production_api_key, self.folder_id, "folderName", "folderDescription")
        eq_(response.status_code, 201)