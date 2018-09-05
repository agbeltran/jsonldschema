def create_context(schema, semantic_types, name):
    contexts = {}

    for semantic_type in semantic_types:
        contexts[semantic_type] = {}
        for field in schema:
            contexts[semantic_type][field] = semantic_type+':'
        contexts[semantic_type][name] = semantic_type+':'

    return contexts


def process_schema_name(name):
    new_raw_name = name.replace("_schema.json", '')
    name_array = new_raw_name.split('_')
    output_name = ""

    for name_part in name_array:
        output_name += name_part.capitalize()

    return output_name


if __name__ == '__main__':

    person_schema = {
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
            "lastName": {
                "description": "The person's family name.",
                "type": "string"
            }
        },
        "additionalProperties": False
    }
    schema_name = process_schema_name('person_schema.json')
    base = ['sdo', 'obo']
    new_context = create_context(person_schema, base, schema_name)
    print(new_context)
