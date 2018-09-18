from collections import OrderedDict


def create_context_template(schema, semantic_types, name):
    contexts = OrderedDict()

    jsonld_ignored_keys = ["@id", "@context", "@type"]

    for semantic_type in semantic_types:
        contexts[semantic_type] = OrderedDict()
        contexts[semantic_type]["@context"] = OrderedDict()
        contexts[semantic_type]["@context"][semantic_type] = semantic_types[semantic_type]
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
