import requests
import json
from copy import deepcopy as copy
from jsonschema.validators import RefResolver
import collections

ignored_keys = ["@id", "@type", "@context"]
iterables = ['anyOf', 'oneOf', 'allOf']


def resolve_reference(schema_url):
    """
    Load and decode the schema from a given URL
    :param schema_url: the URL to the schema
    :return: an exception or a decoded json schema as a dictionary
    """
    response = requests.request('GET', schema_url)
    if response.status_code != 200:
        return Exception(schema_url + ' could not be loaded')
    else:
        try:
            return json.loads(response.text)
        except Exception:
            return Exception


def locate_references(schema, references, parent):
    """
    Tries to locate nested $ref
    :param schema: a decoded schema as a dictionary
    :param references: all the references that have already been loaded to avoid endless
    :param parent: the string location of the parent (eg: '#/properties/field1')
    recursivity
    :return:
    """
    base_url = False

    if 'id' in schema.keys():
        base_url = copy(schema['id']).rsplit('/', 1)[0] + '/'

    if base_url:
        print('Processing '+schema['title'])
        for meta_field in schema:

            # locate properties and definitions
            if meta_field == 'properties' or meta_field == 'definitions':

                # for each field in the properties and definitions arrays
                for fieldName in schema[meta_field]:

                    # exclude ignored keys
                    if fieldName not in ignored_keys:
                        field_val = schema[meta_field][fieldName]

                        # locate root $ref
                        if '$ref' in field_val:

                            # this object is already in the schema, make an inner reference
                            if field_val['$ref'] not in references.keys():

                                # if the $ref is not already an inner reference
                                if field_val['$ref'][0] != '#':

                                    # Copy the sub schema name
                                    sub_schema_name = copy(field_val['$ref'])

                                    # Create the referencing location name
                                    new_parent = parent + meta_field + '/' + fieldName

                                    # loads the schema, resolves it and replaces the reference
                                    sub_schema = resolve_reference(base_url + sub_schema_name)
                                    sub_schema = locate_references(sub_schema, references, new_parent)
                                    schema[meta_field][fieldName] = sub_schema

                                    # indicate that this schema has been loaded and its location
                                    #  in the current tree
                                    references[sub_schema_name] = new_parent
                            else:
                                schema[meta_field][fieldName]['$ref'] = references[field_val['$ref']]

                        else:

                            if 'items' in field_val:
                                if '$ref' in field_val['items']:
                                    if field_val["items"]['$ref'] not in references.keys():
                                        print(field_val["items"]["$ref"])
                                    else:
                                        schema[meta_field][fieldName]["items"]['$ref'] = \
                                            references[field_val['$ref']]
        return schema

    else:
        return Exception('No ID to load resolve URL')


def get_name(schema_url):
    name = schema_url.split("/")[-1].replace("#", '')
    return name


def compile_network(schema_url):
    """
    if type(data) != Exception:
        loaded_schemas[get_name(schema_url)] = '#'
        data = locate_references(data, loaded_schemas, '#/')

        with open('../tests/data/compile_test.json', 'w') as output_file:
            json.dump(data, output_file, indent=4)

    else:
        print(data)
        """
    loaded_schemas = {}
    data = resolve_reference(schema_url)
    resolver = RefResolver(schema_url, data)

    def _do_resolve(node):
        if isinstance(node, collections.Mapping) and '$ref' in node:
            with resolver.resolving(node['$ref']) as resolved:
                return resolved
        elif isinstance(node, collections.Mapping):
            for k, v in node.items():
                node[k] = _do_resolve(v)
        elif isinstance(node, (list, tuple)):
            for i in range(len(node)):
                node[i] = _do_resolve(node[i])
        return node

    with open('../tests/data/compile_test.json', 'w') as output_file:
        json.dump(_do_resolve(data), output_file, indent=4)


def resolve_schema_references(schema, loaded_schemas, schema_url=None, refs=None):
    """
    Resolves and replaces json-schema $refs with the appropriate dict.

    Recursively walks the given schema dict, converting every instance
    of $ref in a 'properties' structure with a resolved dict.

    This modifies the input schema and also returns it.

    Arguments:
        schema:
            the schema dict
        loaded_schemas:
            a recursive dictionary that stores the path of already loaded schemas to prevent
            circularity issues
        refs:
            a dict of <string, dict> which forms a store of referenced schemata
        schema_url
            the URL of the schema

    Returns:
        schema
    """

    refs = refs or {}
    if schema_url:
        return _resolve_schema_references(schema,
                                          RefResolver(schema_url, schema, store=refs),
                                          loaded_schemas,
                                          '#')
    else:
        return _resolve_schema_references(schema,
                                          RefResolver("", schema, store=refs),
                                          loaded_schemas,
                                          '#')


def _resolve_schema_references(schema, resolver, loaded_schemas, object_path):
    """

    :param schema:
    :param resolver:
    :param loaded_schemas:
    :param object_path: a string containing the path of the current level inside the document
    :return:
    """

    if SchemaKey.ref in schema:

        if schema['$ref'][0] != '#':
            reference_path = schema.pop(SchemaKey.ref, None)
            resolved = resolver.resolve(reference_path)[1]

            if get_name(resolved['id']) not in loaded_schemas:
                print(get_name(resolved['id']))
                loaded_schemas[get_name(resolved['id'])] = object_path
                schema.update(resolved)
                return _resolve_schema_references(schema, resolver, loaded_schemas, object_path)

            else:
                res = {"$ref": loaded_schemas[get_name(resolved['id'])]}
                schema.update(res)

    if SchemaKey.properties in schema:
        for k, val in schema[SchemaKey.properties].items():
            current_path = object_path + '/properties/'+k
            schema[SchemaKey.properties][k] = _resolve_schema_references(val,
                                                                         resolver,
                                                                         loaded_schemas,
                                                                         current_path)

    if SchemaKey.definitions in schema:
        for k, val in schema[SchemaKey.definitions].items():
            current_path = object_path + '/definitions/' + k
            schema[SchemaKey.definitions][k] = _resolve_schema_references(val,
                                                                          resolver,
                                                                          loaded_schemas,
                                                                          current_path)

    for pattern in SchemaKey.sub_patterns:
        i = 0
        if pattern in schema:
            for val in schema[pattern]:
                iterator = str(copy(i))
                current_path = object_path + '/' + pattern + '/' + iterator
                schema[pattern][i] = _resolve_schema_references(val,
                                                                resolver,
                                                                loaded_schemas,
                                                                current_path)
                i += 1

    if SchemaKey.items in schema:
        current_path = object_path + '/items'
        schema[SchemaKey.items] = _resolve_schema_references(schema[SchemaKey.items],
                                                             resolver,
                                                             loaded_schemas,
                                                             current_path)

    return schema


class SchemaKey:
    ref = "$ref"
    items = "items"
    properties = "properties"
    definitions = 'definitions'
    pattern_properties = "patternProperties"
    sub_patterns = ['anyOf', 'oneOf', 'allOf']


if __name__ == '__main__':
    processed_schemas = {}
    schemaURL = 'https://w3id.org/dats/schema/study_schema.json#'
    schema_name = get_name(schemaURL)

    processed_schemas[get_name(schemaURL)] = '#'

    data = resolve_schema_references(resolve_reference(schemaURL), processed_schemas, schemaURL)

    with open('../tests/data/compile_test.json', 'w') as output_file:
        json.dump(data, output_file, indent=4)



