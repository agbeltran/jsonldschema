from SemDiff import EntityDiff, semDiff

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

    networks = [DATS_contexts, MIACA_contexts]
    EntityCoverage = EntityDiff.EntityCoverage(networks)

    for entity_name in EntityCoverage.covered_entities:
        twins = EntityCoverage.covered_entities[entity_name]
        if twins is not None:
            entity_schema = DATS_schemas[entity_name.lower()+"_schema.json"]
            entity_context = {"@context": DATS_contexts[entity_name.lower()+"_schema.json"]}
            for twin in twins:
                twin_schema = MIACA_schemas[twin.lower()+"_schema.json"]
                twin_context = {"@context":MIACA_contexts[twin.lower()+"_schema.json"]}
                print(entity_name + " and " + twin + " have the same semantic type")
                SemanticDiff = semDiff.SemanticComparator(entity_schema, entity_context,
                                                          twin_schema, twin_context)
                print(SemanticDiff.full_coverage)

