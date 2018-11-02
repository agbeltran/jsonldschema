import json
import requests
from copy import deepcopy as copy
from jsonschema.validators import RefResolver
from collections import OrderedDict

ignored_keys = ["@id", "@type", "@context"]
iterables = ['anyOf', 'oneOf', 'allOf']


def resolve_reference(schema_url):
    """
    Load and decode the schema from a given URL
    :param schema_url: the URL to the schema
    :return: an exception or a decoded json schema as a dictionary
    """
    try:
        return json.loads(requests.request('GET', schema_url).text, object_pairs_hook=OrderedDict)
    except Exception:
        return Exception


def get_name(schema_url):
    """
    Extract the item name from it's URL
    :param schema_url: the URL of the schema
    :return name: the name of the schema (eg: 'item_schema.json')
    """
    name = schema_url.split("/")[-1].replace("#", '')
    return name


def resolve_schema_references(schema, loaded_schemas, schema_url=None, refs=None):
    """Resolves and replaces json-schema $refs with the appropriate dict.
    Recursively walks the given schema dict, converting every instance
    of $ref in a 'properties' structure with a resolved dict.
    This modifies the input schema and also returns it.

    :param schema: the schema dict
    :param loaded_schemas: a recursive dictionary that stores the path of
        already loaded schemas to prevent circularity issues
    :param refs: a dict of <string, dict> which forms a store of referenced schemata
    :param schema_url: the URL of the schema
    :return: schema
    """

    schema = OrderedDict(schema)
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
    Iterate over the json until it find a $ref and replace it with the loaded object or a
    reference to an already loaded object
    :param schema: the schema or portion of schema to process
    :param resolver: the RefResolver object that will realize the task of loading/updating the
    object
    :param loaded_schemas: a dictionary of a already loaded schemas (prevent recursion issues)
    :param object_path: a string containing the path of the current level inside the document
    :return schema: the updated schema
    """

    schema = OrderedDict(schema)

    if SchemaKey.ref in schema:

        if schema['$ref'][0] != '#':
            reference_path = schema.pop(SchemaKey.ref, None)
            resolved = OrderedDict(resolver.resolve(reference_path)[1])

            if get_name(resolved['id']) not in loaded_schemas:
                loaded_schemas[get_name(resolved['id'])] = object_path
                schema.update(resolved)
                schema = OrderedDict(schema)
                return OrderedDict(_resolve_schema_references(schema, resolver, loaded_schemas,
                                                              object_path))

            else:
                res = {"$ref": loaded_schemas[get_name(resolved['id'])]}
                schema.update(res)

    if SchemaKey.properties in schema:
        for k, val in OrderedDict(schema)[SchemaKey.properties].items():
            current_path = object_path + '/properties/'+k
            schema[SchemaKey.properties][k] = OrderedDict(
                                                _resolve_schema_references(val,
                                                                           resolver,
                                                                           loaded_schemas,
                                                                           current_path))

    if SchemaKey.definitions in schema:
        for k, val in OrderedDict(schema)[SchemaKey.definitions].items():
            current_path = object_path + '/definitions/' + k
            schema[SchemaKey.definitions][k] = OrderedDict(
                                                _resolve_schema_references(val,
                                                                           resolver,
                                                                           loaded_schemas,
                                                                           current_path))

    for pattern in SchemaKey.sub_patterns:
        i = 0
        if pattern in schema:
            for val in OrderedDict(schema)[pattern]:
                iterator = str(copy(i))
                current_path = object_path + '/' + pattern + '/' + iterator
                schema[pattern][i] = OrderedDict(_resolve_schema_references(val,
                                                                            resolver,
                                                                            loaded_schemas,
                                                                            current_path))
                i += 1

    if SchemaKey.items in OrderedDict(schema):
        current_path = object_path + '/items'
        schema[SchemaKey.items] = OrderedDict(_resolve_schema_references(schema[SchemaKey.items],
                                                                         resolver,
                                                                         loaded_schemas,
                                                                         current_path))

    return OrderedDict(schema)


class SchemaKey:
    ref = "$ref"
    items = "items"
    properties = "properties"
    definitions = 'definitions'
    pattern_properties = "patternProperties"
    sub_patterns = ['anyOf', 'oneOf', 'allOf']
