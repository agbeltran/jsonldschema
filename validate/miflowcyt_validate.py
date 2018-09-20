from requests import request
from xmljson import parker, Parker
from xml.etree.ElementTree import fromstring
from json import dumps, load
import os


clientID = "DBasdfas89798asoj892KOS"
itemID = "FR-FCM-ZY68"
base_schema = "experiment_schema.json"


def grab_user_content(client_identifier):
    full_url = "http://flowrepository.org/list?client=" + client_identifier
    response = request("GET", full_url)
    return dumps(parker.data((fromstring(response.text))))


def grab_experiment_from_api(client_identifier, item_identifier):

    """test = os.path.join(os.path.dirname(__file__), "../"+base_schema)

    with open(test) as schema_input:
        schema_data = load(schema_input)
    schema_input.close()"""

    full_url = "http://flowrepository.org/list/" + item_identifier \
                 + "?client=" + client_identifier
    response = request("GET", full_url)
    return parker.data((fromstring(response.text)))["public-experiments"]["experiment"]

    """total_field_number = 0
    valid_field_number = 0

    for fieldName in schema_data["properties"]:
        print(fieldName)
        total_field_number += 1

        if fieldName in input_data:
            valid_field_number += 1

    print(total_field_number)
    print(valid_field_number)

    print(input_data)"""


def load_schemas(base_schema_name):

    network = {}

    base_schema_path = os.path.join(os.path.dirname(__file__), ".././tests/data/MiFlowCyt/"+base_schema_name)
    with open(base_schema_path) as schema_input:
        schema_data = load(schema_input)
    schema_input.close()

    print(schema_data)

    return 0


if __name__ == '__main__':
    data = grab_experiment_from_api(clientID, itemID)
    schemas = load_schemas(base_schema)
