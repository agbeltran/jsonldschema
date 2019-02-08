from nose.tools import assert_true
import os
import mock
import jsonbender
from deepdiff import DeepDiff
from collections import OrderedDict
from validate.miflowcyt_validate import FlowRepoClient

map_file = os.path.join(os.path.dirname(__file__),
                        "../tests/data/MiFlowCyt/experiment_mapping.json")


class TestFlowRepoClient(object):

    @classmethod
    def setup_class(cls):
        cls.client = FlowRepoClient(map_file, "this is a fake ID", 2)

        cls.mock_request_patcher = mock.patch('validate.miflowcyt_validate.requests.request')
        cls.mock_request = cls.mock_request_patcher.start()

        cls.mock_xmljson_patcher = mock.patch('validate.miflowcyt_validate.xmljson.parker.data')
        cls.mock_xmljson = cls.mock_xmljson_patcher.start()

        cls.mock_etree_patcher = mock.patch('validate.miflowcyt_validate.elemTree.fromstring')
        cls.mock_etree = cls.mock_etree_patcher.start()

    """"@classmethod
    def teardown_class(cls):
        cls.mock_request_patcher.stop()
        cls.mock_xmljson_patcher.stop()
        cls.mock_etree_patcher.stop()"""

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
        ids = self.client.get_user_content_id()
        assert_true('123' in ids)
        assert_true('456' in ids)

        self.mock_request.return_value.status_code = 404
        ids = self.client.get_user_content_id()
        assert_true(isinstance(ids, Exception))

    def test_grab_experiment_from_api(self):
        self.mock_request.return_value.status_code = 200
        self.mock_request.return_value.text = "123"
        item_metadata = self.client.grab_experiment_from_api("123")
        assert_true(item_metadata == "123")

    def test_get_all_experiments(self):
        self.mock_request.return_value.status_code = 200
        self.mock_request.return_value.text = '123'
        experiment = self.client.grab_experiment_from_api("fakeItemID")
        assert_true(experiment == "123")

        self.mock_request.return_value.status_code = 404
        self.mock_request.return_value.text = '123'
        experiment_error_1 = self.client.grab_experiment_from_api("fakeItemID")
        assert_true(isinstance(experiment_error_1, Exception))

    def test_validate_instance_from_file(self):
        validation = self.client.validate_instance_from_file({"test": "test"}, "test",
                                                             "test.test")
        assert_true(isinstance(validation, Exception))

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

    def test_preprocess_content(self):
        xml_file = os.path.join(os.path.dirname(__file__),
                                "../tests/data/MiFlowCyt/experiment.xml")

        with open(xml_file, 'r') as input_data:
            data = input_data.read()
        input_data.close()

        local_client = FlowRepoClient(map_file, "FakeID", 1)
        processed_content = [local_client.preprocess_content(data)]

        expected_output = [
            {
                "date": OrderedDict({
                    "start-date": "2007-05-30",
                    "end-date": "2007-08-21"
                }),
                "qualityControlMeasures": "To standardize voltage "
                                          "settings across samples "
                                          "acquired on different days, "
                                          "single stained controls were included. "
                                          "Voltages were adjusted such that fluorescence"
                                          " intensity was identical for each antibody, "
                                          "regardless of date of acquisition. ",
                "conclusions": "conclusion",
                "organization": [
                    OrderedDict({
                        "name": "Child & Family Research Institute",
                        "address": OrderedDict({
                            "street": "938 West 28th Avenue",
                            "city": "Vancouver",
                            "zip": "V5Z 4H4",
                            "state": "BC",
                            "country": "Canada"
                        })
                    }),
                    OrderedDict({
                        "name": "University of Washington Medical Center",
                        "address": OrderedDict({
                            "street": "1959 NE Pacific Street ",
                            "city": "Seattle",
                            "zip": "98195-7650 ",
                            "state": "Washington",
                            "country": "USA"
                        })
                    })
                ],
                "purpose": "The purpose of the experiment presented "
                           "here was to test whether human B cells can "
                           "be identified through a negative-gating strategy.\n\n",
                "keywords": [
                    "Innate Immune Response",
                    "Toll-like receptors",
                    "Activation markers",
                    "B cells",
                    "MIFlowCyt"
                ],
                "experimentVariables": "",
                "other": {
                    "related-publications": [
                        OrderedDict({
                            "pubmed-id": 20131398
                        }),
                        OrderedDict({
                            "pmc-id": "PMC2878765"
                        })
                    ]
                },
                "primary_contact": OrderedDict({
                    "name": "Karin Breuer"
                })
            }
        ]
        assert_true(DeepDiff(processed_content, expected_output) == {})

    def test_inject_context(self):
        self.mock_request_patcher.stop()
        self.mock_xmljson_patcher.stop()
        self.mock_etree_patcher.stop()

        mock_validate_patcher = \
            mock.patch('validate.miflowcyt_validate.FlowRepoClient.make_validation')
        mock_validate = mock_validate_patcher.start()
        mock_validate.return_value = [
            {
                "FR-FCM-ZZZ3": {
                    "date": {
                        "start-date": "2007-05-30",
                        "end-date": "2007-08-21"
                    },
                    "qualityControlMeasures": "To standardize  ... ",
                    "conclusions": "conclusion",
                    "organization": [
                        {
                            "name": "Child & Family Research Institute",
                            "address": {
                                "street": "938 West 28th Avenue",
                                "city": "Vancouver",
                                "zip": "V5Z 4H4",
                                "state": "BC",
                                "country": "Canada"
                            }
                        },
                        {
                            "name": "University of Washington Medical Center",
                            "address": {
                                "street": "1959 NE Pacific Street ",
                                "city": "Seattle",
                                "zip": "98195-7650 ",
                                "state": "Washington",
                                "country": "USA"
                            }
                        }
                    ],
                    "purpose": "The purpose of the exp...",
                    "keywords": [
                        "Innate Immune Response",
                        "Toll-like receptors",
                        "Activation markers",
                        "B cells",
                        "MIFlowCyt"
                    ],
                    "experimentVariables": "",
                    "other": {
                        "related-publications": [
                            {
                                "pubmed-id": 20131398
                            },
                            {
                                "pmc-id": "PMC2878765"
                            }
                        ]
                    },
                    "primary_contact": {
                        "name": "Karin Breuer"
                    }
                }
            },
            ""
        ]

        expected_output = {
            "FR-FCM-ZZZ3": {
                "date": {
                    "start-date": "2007-05-30",
                    "end-date": "2007-08-21"
                },
                "qualityControlMeasures": "To standardize  ... ",
                "conclusions": "conclusion",
                "organization": [
                    {
                        "name": "Child & Family Research Institute",
                        "address": {
                            "street": "938 West 28th Avenue",
                            "city": "Vancouver",
                            "zip": "V5Z 4H4",
                            "state": "BC",
                            "country": "Canada"
                        },
                        "@context": "https://w3id.org/mircat/miflowcyt/context/"
                                    "obo/organization_obo_context.jsonld",
                        "@type": "Organization"
                    },
                    {
                        "name": "University of Washington Medical Center",
                        "address": {
                            "street": "1959 NE Pacific Street ",
                            "city": "Seattle",
                            "zip": "98195-7650 ",
                            "state": "Washington",
                            "country": "USA"
                        },
                        "@context": "https://w3id.org/mircat/miflowcyt/context/"
                                    "obo/organization_obo_context.jsonld",
                        "@type": "Organization"
                    }
                ],
                "purpose": "The purpose of the exp...",
                "keywords": [
                    "Innate Immune Response",
                    "Toll-like receptors",
                    "Activation markers",
                    "B cells",
                    "MIFlowCyt"
                ],
                "experimentVariables": "",
                "other": {
                    "related-publications": [
                        {
                            "pubmed-id": 20131398
                        },
                        {
                            "pmc-id": "PMC2878765"
                        }
                    ]
                },
                "primary_contact": {
                    "name": "Karin Breuer",
                    "@context": "https://w3id.org/mircat/miflowcyt/context/"
                                "obo/primary_contact_obo_context.jsonld",
                    "@type": "Primary_contact"
                },
                "@context": "https://w3id.org/mircat/miflowcyt/context/"
                            "obo/experiment_obo_context.jsonld",
                "@type": "Experiment"
            }
        }

        local_client = FlowRepoClient(map_file, "fakeID", 1)
        contexts = local_client.inject_context()
        assert_true(contexts == expected_output)
        mock_validate_patcher.stop()

    def test_make_validation(self):

        # Getting the XML variable that is returned by get_all_experiments
        xml_file = os.path.join(os.path.dirname(__file__),
                                "../tests/data/MiFlowCyt/experiment.xml")

        with open(xml_file, 'r') as input_data:
            data = input_data.read()
        input_data.close()

        mock_getcontent_patcher = mock.patch(
            "validate.miflowcyt_validate.FlowRepoClient.get_user_content_id")
        mock_getcontent = mock_getcontent_patcher.start()
        mock_getcontent.return_value = [
            'FR-FCM-ZZZ3', 'FR-FCM-ZZZ4', 'FR-FCM-ZZZA'
        ]

        mock_getexp_patcher = mock.patch(
            "validate.miflowcyt_validate.FlowRepoClient.get_all_experiments")
        mock_getexp = mock_getexp_patcher.start()
        mock_getexp.return_value = {'FR-FCM-ZZZ3': data}

        expected_output = {
            "FR-FCM-ZZZ3": {
                "date": {
                    "start-date": "2007-05-30",
                    "end-date": "2007-08-21"
                },
                "qualityControlMeasures": "To standardize voltage settings across samples "
                                          "acquired on different days, single stained "
                                          "controls were included. Voltages were adjusted "
                                          "such that fluorescence intensity was identical "
                                          "for each antibody, regardless of date of "
                                          "acquisition. ",
                "conclusions": "conclusion",
                "organization": [
                    {
                        "name": "Child & Family Research Institute",
                        "address": {
                            "street": "938 West 28th Avenue",
                            "city": "Vancouver",
                            "zip": "V5Z 4H4",
                            "state": "BC",
                            "country": "Canada"
                        }
                    },
                    {
                        "name": "University of Washington Medical Center",
                        "address": {
                            "street": "1959 NE Pacific Street ",
                            "city": "Seattle",
                            "zip": "98195-7650 ",
                            "state": "Washington",
                            "country": "USA"
                        }
                    }
                ],
                "purpose": "The purpose of the experiment presented here was to test"
                           " whether human B cells can be identified through a "
                           "negative-gating strategy.\n\n",
                "keywords": [
                    "Innate Immune Response",
                    "Toll-like receptors",
                    "Activation markers",
                    "B cells",
                    "MIFlowCyt"
                ],
                "experimentVariables": "",
                "other": {
                    "related-publications": [
                        {
                            "pubmed-id": 20131398
                        },
                        {
                            "pmc-id": "PMC2878765"
                        }
                    ]
                },
                "primary_contact": {
                    "name": "Karin Breuer"
                }
            }
        }

        import json

        client = FlowRepoClient(map_file, "anotherfakeID", 1)
        validation, errors = client.make_validation()
        print(json.dumps(validation, indent=4))
        assert_true(validation == expected_output)
        assert_true(errors == {})
