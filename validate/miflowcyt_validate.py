from requests import request
from xmljson import parker
from xml.etree.ElementTree import fromstring
from json import dumps, load
import os
import pprint


def grab_user_content(client_identifier):
    full_url = "http://flowrepository.org/list?client=" + client_identifier
    response = request("GET", full_url)
    return dumps(parker.data((fromstring(response.text))))


def grab_experiment_from_api(client_identifier, item_identifier):
    """
    Retrieve the experiment metadata and return it as a python object
    :param client_identifier: the client identifier (apiKey)
    :param item_identifier: the item identifier that should be retrieved
    :return: the python object obtained from the XML
    """

    full_url = "http://flowrepository.org/list/" + item_identifier + "?client=" + client_identifier
    response = request("GET", full_url)
    return parker.data((fromstring(response.text)))["public-experiments"]["experiment"]


def load_schema(base_schema_name, network):
    """
    Load the set of schemas dependencies from the base given schema
    :param base_schema_name: the name of the schema to load
    :param network: the dictionary to add the loaded schemas
    :return network: the dictionary that contains the loaded schemas
    """

    base_path = ".././tests/data/MiFlowCyt/"
    base_schema_path = os.path.join(os.path.dirname(__file__), base_path + base_schema_name)
    with open(base_schema_path) as schema_input:
        schema_data = load(schema_input)
    schema_input.close()

    network[base_schema_name] = schema_data

    for field in schema_data["properties"]:

        # TODO: add use case for anyOf, oneOf and items
        if '$ref' in schema_data["properties"][field]:
            test = schema_data["properties"][field]["$ref"].rsplit('/', 1)[-1]
            network = load_schema(test, network)

    return network


def validate_instance(instance, schema, mapping):
    ignored_keys = ["@id", "@type", "@context"]
    #pp = pprint.PrettyPrinter(indent=2)
    #pp.pprint(instance)

    total_fields = 0
    matched_field = 0

    for field in schema['properties']:
        if field not in ignored_keys:

            total_fields += 1
            if field in mapping:
                processing_field = mapping[field]
            else:
                processing_field = field

            if processing_field in instance:
                matched_field +=1

    print("Matched: " + str(matched_field) + " out of " + str(total_fields))


if __name__ == '__main__':
    clientID = "DBasdfas89798asoj892KOS"
    itemID = "FR-FCM-ZY68"
    base_schema = "experiment_schema.json"

    mapping_dict = {
        "qualityControlMeasures": "quality-control-measures",
        "conclusions": "conclusion",
        "organization": "organizations",
        "date": "experiment-dates",
        "primaryContact": "primary-researcher"
    }

    data = grab_experiment_from_api(clientID, itemID)
    schemas = load_schema(base_schema, {})
    validate_instance(data, schemas['experiment_schema.json'], mapping_dict)
