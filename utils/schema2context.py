from collections import OrderedDict


def create_context_template(schema, semantic_types, name):
    """ Create the context template

    :param schema: the schema for which to build the context
    :param semantic_types: the schema base type
    :param name: the schema name
    :return: a dictionary representing the schema context
    """
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
    """ Extract the name out of a schema composite name by remove unnecessary strings

    :param name: a schema name
    :return: a string representing the processed schema
    """
    new_raw_name = name.replace("_schema.json", '').replace('.json', '')
    name_array = new_raw_name.split('_')
    output_name = ""

    for name_part in name_array:
        output_name += name_part.capitalize()

    return output_name
