import unittest
import os
from utils.schema2context import create_network_context, prepare_input, create_and_save_contexts, generate_context_mapping_dict


class TestSchema2Context(unittest.TestCase):

    input = dict({
        "MIACME": {
            "schema_url": "https://w3id.org/mircat/miacme/schema/miacme_schema.json"
        },
        "MIACA": {
            "schema_url": "https://w3id.org/mircat/miaca/schema/miaca_schema.json"
        },
        "MIFlowCyt": {
            "schema_url": "https://w3id.org/mircat/miflowcyt/schema/miflowcyt_schema.json"
        }
    })

    base = {
        "sdo": "https://schema.org",
        "obo": "http://purl.obolibrary.org/obo/"
    }

    regexes = {
        "/schema": "/context/obo",
        "_schema": "_obo_context"
    }

    def test_create_context_network(self):
        for key in self.input:
            mapping = prepare_input(self.input[key]["schema_url"], key)
            create_network_context(mapping, self.base)

    def test_create_and_save_contexts(self):
        for key in self.input:
            mapping = prepare_input(self.input[key]["schema_url"], key)
            output_directory = os.path.join(os.path.dirname(__file__), "../data/contexts")
            context = create_and_save_contexts(mapping, self.base, output_directory)
            print(context)

    def test_generate_mapping_dict(self):
        for key in self.input:
            mapping = generate_context_mapping_dict(self.input[key]["schema_url"], self.regexes, key)
            print(mapping)

