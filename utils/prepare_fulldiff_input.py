import json
import requests
from jsonschema.validators import RefResolver
from utils.compile_schema import SchemaKey, get_name


def prepare_input(schema_1_url, schema_2_url, mapping_1, mapping_2):
    """ Function to help preparing the full_diff input

    :param schema_1_url: url of the first schema
    :param schema_2_url: url of the second schema
    :param mapping_1: a mapping to contexts
    :param mapping_2: a mapping to contexts
    :return: a fully prepared variable with all resolved references ready to be used by full_diff
    """

    network_1_schemas = {
        'schemas': resolve_network(schema_1_url),
        'name': mapping_1['networkName'],
        'contexts': load_context(mapping_1)
    }
    network_2_schemas = {
        'schemas': resolve_network(schema_2_url),
        'name': mapping_2['networkName'],
        'contexts': load_context(mapping_2)
    }

    return [network_1_schemas, network_2_schemas]


def load_context(context):
    """ Load the context variable from the given URL mapping

    :param context: a mapping of context URL
    :return: a context variable
    """
    full_context = {}

    for schema in context['contexts']:
        context_content = requests.get(context['contexts'][schema])
        full_context[schema+'.json'] = json.loads(context_content.text)['@context']

    return full_context


def resolve_network(schema_url):
    """ Function that triggers the resolved_schema_ref function

    :param schema_url: a schema URL
    :return: a fully resolved network
    """
    network_schemas = {}
    schema_content = json.loads(requests.get(schema_url).text)
    resolver = RefResolver(schema_url, schema_content, store={})
    return resolve_schema_ref(schema_content, resolver, network_schemas)


def resolve_schema_ref(schema, resolver, network):
    """ Recursively resolves the references in the schemas and add them to the networt

    .. warning:: use resolve network instead

    :param schema: the schema to resolve
    :param resolver: the refResolver object
    :param network: the network to add the schemas to
    :return: a fully processed network with resolved ref
    """

    if SchemaKey.ref in schema and schema['$ref'][0] != '#':
        reference_path = schema.pop(SchemaKey.ref, None)
        resolved = resolver.resolve(reference_path)[1]
        if type(resolved) != Exception:
            network[get_name(resolved['id'])] = resolved

    if SchemaKey.properties in schema:
        for k, val in schema[SchemaKey.properties].items():
            resolve_schema_ref(val, resolver, network)

    if SchemaKey.definitions in schema:
        for k, val in schema[SchemaKey.definitions].items():
            resolve_schema_ref(val, resolver, network)

    for pattern in SchemaKey.sub_patterns:
        if pattern in schema:
            for val in schema[pattern]:
                resolve_schema_ref(val, resolver, network)

    if SchemaKey.items in schema:
        resolve_schema_ref(schema[SchemaKey.items], resolver, network)

    return network
