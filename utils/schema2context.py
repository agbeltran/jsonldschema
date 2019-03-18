from collections import OrderedDict
from urllib.parse import urlparse, quote_plus
from copy import deepcopy
import requests
import json
import re
import os
from utils.prepare_fulldiff_input import resolve_network


def get_json_from_url(json_url):
    """ Gets the content of a json file from its URL - it can be a schema or a context file,
    or any other json file.

    :param json_url: a URL for a json file (e.g. a schema or a context file)
    :return: a dictionary with the json content
    """
    try:
        response = requests.get(json_url)
        if response.status_code == 200:
            json_dict = json.loads(response.text)
            return json_dict
        else:
            raise Exception("No json could be found at given URL", json_url)
    except Exception as e:
        raise e


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
    :type schema_url: str
    :param semantic_types: a dictionary with {"ontologyName":"ontologyBaseURL"}
    :type semantic_types: dict
    :return: a dictionary with a context variable for easy ontology
    """
    try:
        schema = get_json_from_url(schema_url)
        schema_name = process_schema_name(schema['id'].split("/")[-1])
        return create_context_template(schema, semantic_types, schema_name)
    except requests.exceptions.MissingSchema:
        return Exception("No schema could be found at given URL", schema_url)
    except Exception as e:
        return Exception("No schema could be found at given URL", schema_url, e)


def create_network_context(mapping, semantic_types):
    """ Generates the context files for each schema in the given network

    :param mapping: a file containing a mapping dict {"schemaName": "schemaURL"}
    :type mapping: dict
    :param semantic_types: a mapping dict of ontologies {"ontologyName": "Ontology URL"}
    :type semantic_types: dict
    :return: the resolved contexts
    """

    contexts = {}
    # For each schema
    for schema_name in mapping['schemas']:
        contexts[schema_name] = {}
        schema_url = mapping['schemas'][schema_name]
        local_context = create_context_template_from_url(schema_url, semantic_types)
        for context_type in local_context:
            contexts[schema_name][context_type] = local_context[context_type]
    return contexts


def create_and_save_contexts(mapping, semantic_types, write_to_file):
    """ Generates the context files for each schema in the given network
    and write these files to the disk

    :param mapping: a file containing a mapping dict {"schemaName": "schemaURL"}
    :type mapping: dict
    :param semantic_types: a mapping dict of ontologies {"ontologyName": "Ontology URL"}
    :type semantic_types: dict
    :param write_to_file: the directory absolute path to output the variables
    :type write_to_file: str
    :return: the resolved contexts
    """
    contexts = {}
    try:
        if not os.path.exists(write_to_file):
            os.makedirs(write_to_file)

        # create a sub directory base on the network name found in mapping
        output_sub_dir = os.path.join(os.path.dirname(__file__),
                                      write_to_file + '/' + mapping['networkName'])
        if not os.path.exists(output_sub_dir):
            os.makedirs(output_sub_dir)

        # create subsub directory for each prefix
        for ontology_prefix in semantic_types:
            local_output_dir = os.path.join(os.path.dirname(__file__),
                                            write_to_file + '/' +
                                            mapping['networkName'] +
                                            "/" +
                                            ontology_prefix)
            if not os.path.exists(local_output_dir):
                os.makedirs(local_output_dir)

        # For each schema
        for schema_name in mapping['schemas']:
            contexts[schema_name] = {}

            schema_url = mapping['schemas'][schema_name]
            local_context = create_context_template_from_url(schema_url, semantic_types)

            for context_type in local_context:
                contexts[schema_name][context_type] = local_context[context_type]
                context_file_name = schema_name.replace("_schema.json",
                                                        "_" + context_type + "_context.jsonld")
                local_output_file = os.path.join(os.path.dirname(__file__),
                                                 write_to_file + '/' +
                                                 mapping['networkName'] +
                                                 "/" +
                                                 context_type +
                                                 "/" +
                                                 context_file_name)
                with open(local_output_file, "w") as output_file:
                    output_file.write(json.dumps(local_context[context_type], indent=4))

    except Exception as e:
        raise Exception("Please provide a valid path to your directory", e)

    return contexts


def prepare_input(schema_url, network_name):
    """ Enable to resolve all references from a given schema and create the output
    for create_network_context

    :param schema_url: url of the schema
    :type schema_url: str
    :param network_name: the name of the network
    :type network_name: str
    :return: a TextIOWrapper with the location of the mapping file
    """
    output = {
        "networkName": network_name,
        "schemas": {}
    }
    try:
        network = resolve_network(schema_url)

        for schema in network.keys():
            output['schemas'][schema] = network[schema]['id']

        return output
    except Exception as e:
        raise Exception("Error with schema ", schema_url, "Exception:", e)


def generate_contexts_from_regex(schema_url, regex_input):
    """ Creates the context URL for the given schema url based
    on given regex

    :param schema_url: a schema URL
    :type schema_url: str
    :param regex_input: keys are the regex to locate and value the replace value
    :type regex_input: dict
    :return: a context URL
    """
    try:
        context_url = schema_url

        for regex in regex_input.keys():
            context_url = re.sub(regex, regex_input[regex], context_url)

        return context_url
    except Exception:
        raise Exception("There is a problem with your input")


def generate_context_mapping(schema_url, regex_input):
    """ Resolves all schemas from given schema URL and creates the context mapping

    :param schema_url: a schema URL
    :type schema_url: str
    :param regex_input: keys are the regex to locate and value the replace value
    :type regex_input: dict
    :return: a context mapping
    """
    try:
        resolved_network = resolve_network(schema_url)
        context_mapping = {}

        for schema in resolved_network.keys():
            context_mapping[schema] = generate_contexts_from_regex(resolved_network[schema]["id"],
                                                                   regex_input)

        return context_mapping, resolved_network
    except Exception as e:
        raise e


def generate_labels_from_contexts(contexts, labels):
    """  Generate labels from given context using OLS

    :param contexts: a dictionary containing contexts associated to schema names
    :type contexts: dict
    :param labels: pre-existing labels to avoid triggering twice the same query
    :type labels: dict
    :return: labels
    """

    ignored_keys = ["@language"]

    # For each schema
    for schemaName in contexts:
        local_context = deepcopy(contexts[schemaName])
        local_context = local_context["@context"] \
            if ("@context" in local_context) else local_context

        # For each team in that schema
        for term in local_context:
            base_request_url = "https://www.ebi.ac.uk/ols/api/ontologies/"

            # If the term is not to be ignored
            if term not in ignored_keys:

                # if the terms exists (is not none or blank) and hasn't already been processed
                if local_context[term] and local_context[term] not in labels.keys():

                    # if we have a direct URL
                    if urlparse(deepcopy(local_context[term])).scheme in ['http', 'https']:
                        term_url = local_context[term]

                    # if we have an identifier
                    else:
                        url_param = deepcopy(local_context[term]).split(":")

                        # the identifier is an EDAM term
                        if url_param[0] == "edam":
                            base_request_url = "https://www.ebi.ac.uk/ols/api/ontologies/" \
                                               "edam/terms/"

                        # the identifier is not an EDAM term
                        else:
                            url_sub_params = url_param[1].split("_")[0]
                            base_request_url += url_sub_params + "/terms/"
                        term_url = local_context[url_param[0]] + url_param[1]

                    # Double quote plus the URL or OLS won't work (??)
                    term_safe_url = quote_plus(quote_plus(term_url))
                    local_request_url = base_request_url + term_safe_url
                    resp = requests.get(local_request_url)

                    if resp.status_code == 200:
                        if "label" in json.loads(resp.text).keys():
                            labels[local_context[term]] = json.loads(resp.text)["label"]
                        else:
                            labels[local_context[term]] = None

                    else:
                        labels[local_context[term]] = None

    return labels


def generate_context_mapping_dict(schema_url, regex_input, network_name):
    """ Generates the mapping dictionary used by full diff

    :param schema_url: the url of the main schema
    :type schema_url: str
    :param regex_input: a set of regex to indicate how to transform schemas URL to contexts URL
    :type regex_input: dict
    :param network_name: the name of the current network
    :type network_name: str
    :return: the mapping dictionary of schemas and contexts
    """
    raw_mapping = generate_context_mapping(schema_url, regex_input)
    output = {
        "networkName": network_name,
        "contexts": raw_mapping[0],
        "schemas": {}
    }

    for schema in raw_mapping[1]:
        output['schemas'][schema] = raw_mapping[1][schema]['id']

    labels = {}
    errors = []
    for schema_key in raw_mapping[0]:
        context_url = raw_mapping[0][schema_key]
        try:
            context = get_json_from_url(context_url)
        except Exception as e:
            errors.append(e)
            continue
        labels = generate_labels_from_contexts({schema_key: context}, labels)

    output['labels'] = labels

    return output, errors
