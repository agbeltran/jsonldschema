import unittest
import os
import json
import xmljson
import jsonbender
import xml.etree.ElementTree as elemTree
from copy import deepcopy

from validate import miflowcyt_validate


map_file = os.path.join(os.path.dirname(__file__),
                        "../data/MiFlowCyt/experiment_mapping.json")
base_schema = "experiment_schema.json"
range_limit = 1


class FlowRepoClientTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FlowRepoClientTestCase, self).__init__(*args, **kwargs)

        configfile_path = os.path.join(os.path.dirname(__file__), "../test_config.json")
        if not (os.path.exists(configfile_path)):
            configfile_path = os.path.join(os.path.dirname(__file__), "../test_config.json.sample")
        with open(configfile_path) as config_data_file:
            config_json = json.load(config_data_file)
            self.validate_config(config_json)
            config_data_file.close()

        self._data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.api_key = config_json["flowrepo_userID"]

    def validate_config(self, config_data):
        try:
            self.assertTrue(config_data['flowrepo_userID'])
        except (KeyError, AssertionError):
            print("Please set your Flow Repository user ID key in the test_config.json "
                  "file before running tests")
            quit(0)

    def setUp(self):
        self.client = miflowcyt_validate.FlowRepoClient(map_file, base_schema, self.api_key)
        self.mappingKeys = {
            "date", "primaryContact", "qualityControlMeasures",
            "conclusions", "organization", "purpose",
            "keywords", "experimentVariables", "other"
        }
        self.user_ids = [
             'FR-FCM-ZZZ3', 'FR-FCM-ZZZ4', 'FR-FCM-ZZZA', 'FR-FCM-ZZZE', 'FR-FCM-ZZZF',
             'FR-FCM-ZZZG', 'FR-FCM-ZZZH', 'FR-FCM-ZZZK', 'FR-FCM-ZZZU', 'FR-FCM-ZZZV',
             'FR-FCM-ZZYZ', 'FR-FCM-ZZYY', 'FR-FCM-ZZY2', 'FR-FCM-ZZY3', 'FR-FCM-ZZY6'
        ]

    def test_grab_user_content(self):
        user_content = self.client.grab_user_content(self.api_key)
        self.assertTrue(user_content.status_code == 200)

    def test_get_user_content_id(self):
        user_content = self.client.get_user_content_id(self.api_key)
        for _id in self.user_ids:
            self.assertTrue(_id in user_content)

    def test_get_mapping(self):
        mapping = self.client.get_mapping(map_file)
        for mapKey in self.mappingKeys:
            self.assertTrue(mapKey in mapping.keys())

    def test_grab_experiment_from_api(self):
        experiment = self.client.grab_experiment_from_api(self.api_key, 'FR-FCM-ZZZ3')
        self.assertTrue(experiment.status_code == 200)

    def test_validate_instance_from_file(self):

        experiment_xml = self.client.grab_experiment_from_api(self.api_key, 'FR-FCM-ZZY6')
        experience_metadata = xmljson.parker.data((elemTree.fromstring(
            experiment_xml.text)))["public-experiments"]["experiment"]

        extracted_json = jsonbender.bend(self.client.get_mapping(map_file), experience_metadata)

        extracted_json['keywords'] = extracted_json['keywords']['keyword']
        extracted_json['organization'] = extracted_json['organization']['organization']
        extracted_json['other'] = {}
        extracted_json['other']['related-publications'] = deepcopy(
            extracted_json['related-publications']['publication'])
        del extracted_json['related-publications']

        validation = self.client.validate_instance_from_file(extracted_json,
                                                             'FR-FCM-ZZY6',
                                                             base_schema)
        self.assertTrue(validation == [])

    def test_make_validation(self):
        error_validation = self.client.make_validation(50)
        errors = error_validation[0]

        print("----------------------------------------------")

        print("VALID IDS")
        print(json.dumps(error_validation[1], indent=4))

        print("INVALID IDS")
        print(json.dumps(error_validation[2], indent=4))

        """
        for itemKey in errors:
            print(itemKey, errors[itemKey])
            self.assertTrue(errors[itemKey] == [])
        """

