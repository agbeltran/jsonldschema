import copy


class EntityMerge:
    """
    A class that merge two schemas
    """

    def __init__(self, schema1, context1, schema2, context2):
        """
        Constructor
        :param schema1: dictionary of the first schema
        :param context1: dictionary of the first context as {"@context":{}}
        :param schema2: dictionary of the second schema
        :param context2: dictionary of the second context as {"@context":{}}
        """

        # Initiate output as a copy of the first schema and its context
        self.output_schema = copy.deepcopy(schema1)
        self.output_context = copy.deepcopy(context1)

        # the keys to ignore
        ignored_keys = ["@type", "@context", "@id"]

        # Iterate over the second schema
        for field in schema2["properties"]:

            # Ignore some specific keys
            if field not in ignored_keys:

                # if the field is in the second context
                if field in context2['@context'].keys():

                    # if it is also in the first context
                    if field in context1['@context'].keys():

                        # if the field doesn't have the same semantic value in both context
                        if context1['@context'][field] != context2['@context'][field]:
                            self.output_schema["properties"][field] = schema2["properties"][field]
                            self.output_context["@context"][field] = context2['@context'][field]

                    # if it's not in the first context
                    else:
                        self.output_schema["properties"][field] = schema2["properties"][field]
                        self.output_context["@context"][field] = context2['@context'][field]

                # if the field isn't in the second context, just add it to the schema
                else:
                    self.output_schema["properties"][field] = schema2["properties"][field]


if __name__ == '__main__':
    schema_1 = {
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
    }
    context_1 = {
        "@context": {
            "sdo": "https://schema.org/",
            "Person": "sdo:Person",
            "identifier": {
                "@id": "sdo:identifier",
                "@type": "sdo:Text"
            },
            "firstName": "sdo:givenName",
            "lastName": "sdo:familyName",
            "fullName": "sdo:name",
            "email": "sdo:email",
            "affiliations": "sdo:affiliation",
            "roles": "sdo:roleName"
        }
    }

    schema_2 = {
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
    }
    context_2 = {
        "@context": {
            "sdo": "https://schema.org/",
            "Person": "sdo:Person",
            "identifier": {
                "@id": "sdo:identifier",
                "@type": "sdo:Text"
            },
            "firstName": "sdo:givenName",
            "familyName": "sdo:familyName",
            "fullName": "sdo:name",
            "email": "sdo:email",
            "affiliations": "sdo:affiliation",
            "roles": "sdo:roleName"
        }
    }

    merge = EntityMerge(schema_2, context_2, schema_1, context_1)

    print("output schema:")
    print(merge.output_schema)
    print("output context:")
    print(merge.output_context)