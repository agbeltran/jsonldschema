import unittest
from utils.schema2context import create_network_context, prepare_input


class TestSchema2Context(unittest.TestCase):

    def test_create_context_network(self):
        url = "https://w3id.org/mircat/miaca/schema/miaca_schema.json"

        base = {
            "sdo": "https://schema.org",
            "obo": "http://purl.obolibrary.org/obo/"
        }

        mapping = prepare_input("https://fairsharing.github.io/mircat/miaca/schema/miaca_schema.json",
                                "MIACA", "../data/miaca_mapping.json")

        print(mapping)

        create_network_context("miaca_mapping.json", base)




