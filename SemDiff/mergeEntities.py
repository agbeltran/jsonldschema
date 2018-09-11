import copy


class EntityMerge:
    """
    A class that merge two schemas based on their semantic annotations
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

                # if the field is already in schema1 - syntactic equivalence
                #if field in schema1["properties"]:

                    # if this field has a semantic value for both schemas - semantic equivalence
                    #if (field in context2['@context'].keys() and
                    #        field in context1['@context'].keys()):

                        #if those semantic values are different
                        #if context1["@context"][field] != context2["@context"][field]:
                        #    pass
                        # else they are the same, schema1 has priority, so do nothing !

                    # if this field only has a semantic value for schema2
                    #if (field in context2['@context'].keys() and
                    #        field not in context1['@context'].keys()):
                    #    print("Process ??")

                # the field name is not in schema1
                #else:

                    # if the field has a semantic value in the second context
                    if field in context2["@context"].keys():
                        field_semantic_twin = False

                        for sem_field in context1["@context"]:

                            # there's already a field in the first context with the same semantic
                            # value
                            if context1["@context"][sem_field] == context2["@context"][field]:
                                print("PROCESS?")
                                ### make sure that the merged schema/context include this field
                                field_semantic_twin = True

                        # there is no field in the first context with the same semantic value
                        if field_semantic_twin is not True:
                            self.output_context = context2["@context"][field]
                            self.output_schema["properties"][field] = schema2["properties"][
                                field]

                    # the field doesn't have a semantic value in the second context
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
