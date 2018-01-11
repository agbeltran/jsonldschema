import os
from os.path import  join
import json
from jsonschema.validators import (
     Draft4Validator, RefResolver
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


"""
Validate a JSON schema given the schema file.
"""
def validate_schema_file(schema_file):
    Draft4Validator.check_schema(schema_file)
    return True

"""
Validate a JSON schema given the folder/path and file name of the schema file.
"""
def validate_schema(path, schema_file_name):
    try:
        logger.info("Validating schema %s", schema_file_name)
        with open(join(path, schema_file_name)) as schema_file:
            schema_file = json.load(schema_file)
            return validate_schema_file(schema_file)
    except Exception as e:
        logger.error(e)
        logger.info("done.")
        return False

"""
Validate a JSON instance againsts a JSON schema.
"""
def validate_instance(schemapath, schemafile, instancepath, instancefile, error_printing, store):
        instancefile_fullpath = os.path.join(instancepath, instancefile)
        instance = json.load(open(instancefile_fullpath))
        schemafile_fullpath = os.path.join(schemapath, schemafile)
        schema = json.load(open(schemafile_fullpath))
        resolver = RefResolver('file://' + schemapath + '/' + schemafile, schema, store)
        validator = Draft4Validator(schema, resolver=resolver)
        logger.info("Validating instance %s against schema %s", instancefile_fullpath, schemafile_fullpath)
        if (error_printing == 0):
            errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
            for error in errors:
                print(error.message)
        elif (error_printing == 1):
            errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)

        for error in errors:
            for suberror in sorted(error.context, key=lambda e: e.schema_path):
                print(list(suberror.schema_path), suberror.message, sep=", ")
        else:
            validator.validate(instance, schema)