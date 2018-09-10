import unittest
from SemDiff.entityDiff import EntityCoverage

DATS_data = {
    "person_schema.json": {
        "sdo": "https://schema.org/",
        "Person": "sdo:Person",
        "identifier": "sdo:identifier",
        "firstName": "sdo:givenName",
        "lastName": "sdo:familyName",
        "fullName": "sdo:name",
        "email": "sdo:email",
        "affiliations": "sdo:affiliation",
        "roles": "sdo:roleName"
    },
    "identifier_info_schema.json": {
        "sdo": "https://schema.org/",
        "Identifier": "sdo:Thing",
        "identifier": "sdo:identifier",
        "identifierSource": {
            "@id": "sdo:Property",
            "@type": "sdo:Text"
        }
    }
}

MIACA_data = {
    "source_schema.json": {
        "sdo": "https://schema.org/",
        "Source": "sdo:Person",
        "identifier": "sdo:identifier",
        "firstName": "sdo:givenName",
        "lastName": "sdo:familyName",
        "fullName": "sdo:name",
        "email": "sdo:email",
        "affiliations": "sdo:affiliation",
        "roles": "sdo:roleName"
    },
    "identifier_info_schema.json": {
        "sdo": "https://schema.org/",
        "Identifier_info": "sdo:Thing",
        "identifier": "sdo:identifier",
        "identifierSource": {
            "@id": "sdo:Property",
            "@type": "sdo:Text"
        }
    }
}

networks = [DATS_data, MIACA_data]


class EntityCoverageTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(EntityCoverageTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.semantic_comparator = EntityCoverage(networks)

    def test___process_network(self):
        processed_network = self.semantic_comparator._EntityCoverage__process_network(DATS_data)
        self.assertTrue('Identifier_info' in processed_network.keys())
        self.assertTrue(processed_network['Identifier_info'] is None)
        self.assertTrue('Person' in processed_network.keys())
        self.assertTrue(processed_network['Person'] == 'sdo:Person')

    def test___compute_coverage(self):
        DATS_network = self.semantic_comparator._EntityCoverage__process_network(DATS_data)
        MIACA_network = self.semantic_comparator._EntityCoverage__process_network(MIACA_data)
        coverage = self.semantic_comparator._EntityCoverage__compute_coverage(DATS_network,
                                                                              MIACA_network)

        self.assertTrue('Identifier_info' in coverage[0].keys())
        self.assertTrue(coverage[0]['Identifier_info'] is None)
        self.assertTrue('Person' in coverage[0].keys())
        self.assertTrue(coverage[0]['Person'] == ['Source'])
        self.assertTrue(coverage[1] == 2)
        self.assertTrue(coverage[2] == 1)
