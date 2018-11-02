import os
import json
import requests
from jsonschema.validators import RefResolver
from utils.compile_schema import SchemaKey, get_name


def prepare_input(schema_1_url, schema_2_url, mapping_1, mapping_2):

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
    full_context = {}

    for schema in context['contexts']:
        context_content = requests.get(context['contexts'][schema])
        full_context[schema+'.json'] = json.loads(context_content.text)['@context']

    return full_context


def resolve_network(schema_url):
    network_schemas = {}
    schema_content = json.loads(requests.get(schema_url).text)
    resolver = RefResolver(schema_url, schema_content, store={})
    return resolve_schema_ref(schema_content, resolver, network_schemas)


def resolve_schema_ref(schema, resolver, network):

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


if __name__ == '__main__':
    mapping_dir = os.path.join(os.path.dirname(__file__), "../tests/data")
    mapping_1 = json.load(open(os.path.join(mapping_dir, "dats_mapping.json")))
    mapping_2 = json.load(open(os.path.join(mapping_dir, "miaca_mapping.json")))

    network_1_schema_url = "https://w3id.org/dats/schema/person_schema.json"
    network_2_schema_url = "https://w3id.org/mircat/miaca/schema/source_schema.json"

    output = prepare_input(network_1_schema_url, network_2_schema_url, mapping_1, mapping_2)
    print(output)

    with open(os.path.join(mapping_dir, "full_dats_miaca.json"), 'w') as output_file:
        json.dump(output, output_file, indent=4)
        output_file.close()
