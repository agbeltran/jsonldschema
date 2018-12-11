import unittest
from utils.schema2context import create_network_context, prepare_input


class TestSchema2Context(unittest.TestCase):

    def test_create_context_network1(self):
        url = "https://w3id.org/mircat/miaca/schema/miaca_schema.json"

        base = {
            "sdo": "https://schema.org",
            "obo": "http://purl.obolibrary.org/obo/"
        }

        mapping = prepare_input(url,
                                "MIACA", "../data/automated_miaca_mapping.json")

        create_network_context("automated_miaca_mapping.json", base)


    def test_create_context_network2(self):
        url = "https://w3id.org/mircat/miacme/schema/miacme_schema.json"

        base = {
            "sdo": "https://schema.org",
            "obo": "http://purl.obolibrary.org/obo/"
        }

        mapping = prepare_input(url,
                                "MIACME", "../data/automated_miacme_mapping.json")

        create_network_context("automated_miacme_mapping.json", base)





