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
    validator = Draft4Validator(schema, resolver=resolver)
    logger.info("Validating instance %s against schema %s",
                instancefile_fullpath, schemafile_fullpath)
    if error_printing == 0:
        errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
        for error in errors:
            print(error.message)
    elif error_printing == 1:
        errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)

    for error in errors:
        for suberror in sorted(error.context, key=lambda e: e.schema_path):
            print(list(suberror.schema_path), suberror.message)
    else:
        validator.validate(instance, schema)
    schema_file.close()
    return errors
