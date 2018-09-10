from SemDiff import EntityDiff, semDiff
from collections import namedtuple


class FullSemDiff:
    """
    A class that compute the coverage at entity level and extract twins. It will then compute
    the coverage at attribute level between twins.
    """

    def __init__(self, contexts, network_1, network_2):
        """
        The class constructor
        :param contexts: an array containing the two context networks to use
        :param network_1: a dictionary containing the first set of schemas
        :param network_2: a dictionary containing the second set of schemas
        """

        self.total_entities = 0
        self.half_twins = 0
        self.twins = []

        twin_tuple = namedtuple('Twins', ['first_entity', 'second_entity'])
        twin_coverage = namedtuple('TwinCoverage', ['twins', 'overlap'])

        entity_coverage = EntityDiff.EntityCoverage(contexts)
        for entity_name in entity_coverage.covered_entities:
            self.total_entities += 1
            twins = entity_coverage.covered_entities[entity_name]
            if twins is not None:
                entity_schema = network_1[entity_name.lower() + "_schema.json"]
                entity_context = {"@context": contexts[0][entity_name.lower() + "_schema.json"]}
                for twin in twins:
                    self.half_twins += 1
                    twin_schema = network_2[twin.lower() + "_schema.json"]
                    twin_context = {"@context": contexts[1][twin.lower() + "_schema.json"]}
                    local_twin = twin_tuple(entity_name, twin)
                    attribute_diff = semDiff.SemanticComparator(entity_schema, entity_context,
                                                                twin_schema, twin_context)
                    local_twin_coverage = twin_coverage(local_twin, attribute_diff.full_coverage['coverage'][0])
                    self.twins.append(local_twin_coverage)


if __name__ == '__main__':

    DATS_contexts = {
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
    MIACA_contexts = {
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
    DATS_schemas = {
        "person_schema.json": {
            "id": "https://w3id.org/dats/schema/person_schema.json",
            "$schema": "http://json-schema.org/draft-04/schema",
            "title": "DATS person schema",
            "description": "A human being",
            "type": "object",
            "properties": {
                "@context": {
                    "anyOf": [
                        {
                            "type": "string"
                        },
                        {
                            "type": "object"
                        }
                    ]
                },
                "@id": {"type": "string", "format": "uri"},
                "@type": {"type": "string", "enum": ["Person"]},
                "identifier": {
                    "description": "Primary identifier for the person.",
                    "$ref": "identifier_info_schema.json#"
                },
                "alternateIdentifiers": {
                    "description": "Alternate identifiers for the person.",
                    "type": "array",
                    "items": {
                        "$ref": "alternate_identifier_info_schema.json#"
                    }
                },
                "fullName": {
                    "description": "The first name, any middle names, and surname of a person.",
                    "type": "string"
                },
                "firstName": {
                    "description": "The given name of the person.",
                    "type": "string"
                },
                "lastName": {
                    "description": "The person's family name.",
                    "type": "string"
                }
            },
            "additionalProperties": False
        },
        "identifier_info_schema": {
        }
    }
    MIACA_schemas = {
        "source_schema.json": {
            "id": "https://w3id.org/dats/schema/person_schema.json",
            "$schema": "http://json-schema.org/draft-04/schema",
            "title": "DATS person schema",
            "description": "A human being",
            "type": "object",
            "properties": {
                "@context": {
                    "anyOf": [
                        {
                            "type": "string"
                        },
                        {
                            "type": "object"
                        }
                    ]
                },
                "@id": {"type": "string", "format": "uri"},
                "@type": {"type": "string", "format": "uri"},
                "identifier": {
                    "description": "Primary identifier for the person.",
                    "$ref": "identifier_info_schema.json#"
                },
                "familyName": {
                    "description": "The person's family name.",
                    "type": "string"
                }
            },
            "additionalProperties": False
        },
        "identifier_info_schema.json":{

        }
    }

    networks_contexts = [DATS_contexts, MIACA_contexts]
    full_diff = FullSemDiff(networks_contexts, DATS_schemas, MIACA_schemas)
    print(full_diff.twins)

