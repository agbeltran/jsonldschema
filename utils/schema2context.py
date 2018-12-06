from collections import OrderedDict
import requests
import json
import os
from utils.prepare_fulldiff_input import resolve_network


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
        contexts[semantic_type]["@context"][name] = semantic_type + ":"
        contexts[semantic_type]["@context"]["@language"] = "en"

        for field in schema["properties"]:
            if field not in jsonld_ignored_keys:
                contexts[semantic_type]['@context'][field] = semantic_type + ":"

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


def create_context_template_from_url(schema_url, semantic_types):
    """ Create a context template from the given URL
    :param schema_url: the schema URL
    :type schema_url: basestring
    :param semantic_types: a dictionary with {"ontologyName":"ontologyBaseURL"}
    :type semantic_types: dict
    :return: a dictionary with a context variable for easy ontology
    """
    try:
        response = requests.get(schema_url)
        if response.status_code == 200:
            schema = json.loads(response.text)
            schema_name = process_schema_name(schema['id'].split("/")[-1])
            return create_context_template(schema, semantic_types, schema_name)
        else:
            return Exception("No schema could be found at given URL", schema_url)
    except requests.exceptions.MissingSchema:
        return Exception("No schema could be found at given URL", schema_url)


def create_network_context(network_file, semantic_types):
    """ Generates the context files for each schema in the given network
    and write these files to the disk
    :param network_file: a file containing a mapping dict {"schemaName": "schemaURL"}
    :type network_file: str
    :param semantic_types: a mapping dict of ontologies {"ontologyName": "Ontology URL"}
    :type semantic_types: dict
    :return: the resolved contexts
    """

    contexts = {}

    # this needs to be changed
    data_dir = os.path.join(os.path.dirname(__file__), "./../tests/data")

    # create the main output directory
    output_top_dir = os.path.join(os.path.dirname(__file__), "./generated_context")
    if not os.path.exists(output_top_dir):
        os.makedirs(output_top_dir)

    # open the mapping file
    with open(os.path.join(data_dir, network_file)) as mapping_file:
        mapping = json.load(mapping_file)
        mapping_file.close()

    # create a sub directory base on the network name found in mapping
    output_sub_dir = os.path.join(os.path.dirname(__file__),
                                  "./generated_context/" + mapping['networkName'])
    if not os.path.exists(output_sub_dir):
        os.makedirs(output_sub_dir)

    # create subsub directory for each ontology
    for ontology_name in semantic_types:
        local_output_dir = os.path.join(os.path.dirname(__file__),
                                        "./generated_context/" +
                                        mapping['networkName'] +
                                        "/" +
                                        ontology_name)
        if not os.path.exists(local_output_dir):
            os.makedirs(local_output_dir)

    # For each schema
    for schema_name in mapping['schemas']:

        contexts[schema_name] = {}

        schema_url = mapping['schemas'][schema_name]
        local_context = create_context_template_from_url(schema_url, semantic_types)

        for context_type in local_context:
            contexts[schema_name][context_type] = local_context[context_type]
            context_file_name = schema_name.split('_',1)[0]
            context_file_name += "_"+context_type
            context_file_name += "_context.jsonld"
            local_output_file = os.path.join(os.path.dirname(__file__),
                                             "./generated_context/" +
                                             mapping['networkName'] +
                                             "/" +
                                             context_type +
                                             "/" +
                                             context_file_name)
            with open(local_output_file, "w") as output_file:
                output_file.write(json.dumps(local_context[context_type], indent=4))

    return contexts


def prepare_input(schema_url, network_name, file_name):
    """ Enable to resolve all references from a given schema and create the output
    for create_network_context
    :param schema_url: url of the schema
    :type schema_url: basestring
    :param network_name: the name of the network
    :type network_name: basestring
    :param file_name: the name of the file where the mapping data should be saved
    :type file_name: str
    :return: a TextIOWrapper with the location of the mapping file
    """
    output = {
        "networkName": network_name,
        "schemas": {}
    }
    network = resolve_network(schema_url)

    for schema in network.keys():
        output['schemas'][schema] = network[schema]['id']

    with open(file_name, "w") as mapping_file:
        mapping_file.write(json.dumps(output, indent=4))
        mapping_file.close()

    return [output, file_name]
