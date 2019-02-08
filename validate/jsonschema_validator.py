import os
from os.path import join
import json
from jsonschema.validators import (
     Draft4Validator, RefResolver
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_schema_file(schema_file):
    """
    Validate a JSON schema given the schema file.

    :param schema_file: the string the the schema file location
    :return: True
    """
    Draft4Validator.check_schema(schema_file)
    return True


def validate_schema(path, schema_file_name):
    """
    Validate a JSON schema given the folder/path and file name of the schema file.
    :param path: the path to the schema directory
    :param schema_file_name: the name of the schema in that directory
    :return: True or False
    """
    try:
        logger.info("Validating schema %s", schema_file_name)
        with open(join(path, schema_file_name)) as schema_file:
            schema_file = json.load(schema_file)
            return validate_schema_file(schema_file)
    except Exception as e:
        logger.error(e)
        logger.info("done.")
        return False


def validate_instance(schemapath, schemafile, instancepath, instancefile, error_printing, store):
    """Validate a JSON instance against a JSON schema.

    :param schemapath: the path to the schema directory
    :param schemafile:  the name of the schema file
    :param instancepath:  the path of the instance direvotyr
    :param instancefile: the name of the instance path
    :param error_printing: the error log
    :param store: a store required by RefResolver
    :return: errors
    """

    instancefile_fullpath = os.path.join(instancepath, instancefile)
    instance_file = open(instancefile_fullpath)
    instance = json.load(instance_file)
    instance_file.close()

    schemafile_fullpath = os.path.join(schemapath, schemafile)
    schema_file = open(schemafile_fullpath)
    schema = json.load(schema_file)
    schema_file.close()

    resolver = RefResolver('file://' + schemapath + '/' + schemafile, schema, store)
    return validate_instance_against_schema(instance, resolver, schema)


def validate_instance_against_schema(instance, resolver, schema):
    """
    Simple function to validate an instance against a schema on the fly
    :param instance: the JSON instance to validate
    :type instance: dict
    :param resolver: the resolver object used by Drat4Validator
    :type resolver: RefResolver
    :param schema: the root schema to validate against
    :type schema: dict
    :return: Draft4Validator.validate
    """
    return Draft4Validator(schema, resolver=resolver).validate(instance, schema)
