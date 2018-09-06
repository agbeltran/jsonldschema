from collections import OrderedDict
import json

def create_context(schema, semantic_types, name):
    contexts = OrderedDict()

    jsonld_ignored_keys = ["@id", "@context", "@type"]

    for semantic_type in semantic_types:
        contexts[semantic_type] = OrderedDict()
        contexts[semantic_type]["@context"] = OrderedDict()
        contexts[semantic_type]["@context"][semantic_type] =  semantic_types[semantic_type]
        contexts[semantic_type]["@context"][name] = ""
        contexts[semantic_type]["@context"]["@language"] = "en"

        for field in schema["properties"]:
            if field not in jsonld_ignored_keys:
                contexts[semantic_type]['@context'][field] = ""

    return contexts


def process_schema_name(name):
    new_raw_name = name.replace("_schema.json", '').replace('.json', '')
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
    schema_name = process_schema_name('identifier_info_schema.json')
    base = {
        "sdo": "https://schema.org",
        "obo": "http://purl.obolibrary.org/obo/"
    }

    new_context = create_context(person_schema, base, schema_name)
    sdo_context_name = 'identifier_info_schema.json'.replace('_schema', '_sdo_context')
    obo_context_name = 'identifier_info_schema.json'.replace('_schema', '_obo_context')

    print(sdo_context_name)
    print(json.dumps(new_context['sdo']))
    print(obo_context_name)
    print(json.dumps(new_context['obo']))