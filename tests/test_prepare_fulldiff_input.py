import unittest
import os
import requests
import json
from deepdiff import DeepDiff
from jsonschema.validators import RefResolver
from utils import prepare_fulldiff_input


class CompileSchemaTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CompileSchemaTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        mapping_dir = os.path.join(os.path.dirname(__file__), "../tests/data")
        self.mapping_1 = json.load(open(os.path.join(mapping_dir, "dats_mapping.json")))
        self.mapping_2 = json.load(open(os.path.join(mapping_dir, "miaca_mapping.json")))
        self.network_1_schema_url = "https://w3id.org/dats/schema/person_schema.json"
        self.network_2_schema_url = "https://w3id.org/mircat/miaca/schema/source_schema.json"

    def test_prepare_input(self):
        expected_output = json.loads(json.dumps(json.load(open('data/full_dats_miaca.json'))))
        data = json.loads(json.dumps(prepare_fulldiff_input.prepare_input(self.network_1_schema_url,
                                                                          self.network_2_schema_url,
                                                                          self.mapping_1,
                                                                          self.mapping_2)))
        self.assertTrue(DeepDiff(data, expected_output) == {})

    def test_load_context(self):
        expected_output = json.loads(json.dumps(json.load(open('data/full_dats_miaca.json'))))[
            0]['contexts']
        data = prepare_fulldiff_input.load_context(self.mapping_1)
        self.assertTrue(DeepDiff(data, expected_output) == {})

    def test_resolve_network(self):
        expected_output = json.loads(json.dumps(json.load(open('data/full_dats_miaca.json'))))[
            0]['schemas']
        data = prepare_fulldiff_input.resolve_network(self.network_1_schema_url)

        self.assertTrue(DeepDiff(data, expected_output) == {})

    def test_resolve_schema_ref(self):
        expected_output = json.loads(json.dumps(json.load(open('data/full_dats_miaca.json'))))[
            0]['schemas']
        network_schemas = {}
        schema_content = json.loads(requests.get(self.network_1_schema_url).text)
        resolver = RefResolver(self.network_1_schema_url, schema_content, store={})
        data = prepare_fulldiff_input.resolve_schema_ref(schema_content, resolver, network_schemas)
        self.assertTrue(DeepDiff(data, expected_output) == {})
