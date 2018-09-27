from requests import request
from xmljson import parker
from xml.etree.ElementTree import fromstring
from json import dump, load
import os
from jsonbender import bend, OptionalS, S
from validate.jsonschema_validator import validate_instance


class FlowRepoClient:
    """
    A class that provides functionnalities to catch experiments from FlowRepository, transform
    the XML into JSON and validate the instances against their schema
    """

    def __init__(self, mapping, base_schema, range_limit):
        """
        The class constructor
        :param mapping: the mapping dictionary containing the bend objects
        :param base_schema: the name of the schema to check against
        :param range_limit: the maximum number of items to check for
        """
        self.errors = {}
        configuration_file = os.path.join(os.path.dirname(__file__), "../tests/test_config.json")
        with open(configuration_file) as configuration:
            self.clientID = load(configuration)['flowrepo_userID']
        configuration.close()
        self.mapping = mapping
        self.base_schema = base_schema
        self.content_IDs = self.get_user_content_id(self.clientID)

        for i in range(range_limit):
            experience_metadata = self.grab_experiment_from_api(self.clientID, self.content_IDs[i])
            extracted_json = bend(MAPPING, experience_metadata)
            if extracted_json['organization'] == "\n   ":
                extracted_json['organization'] = {}
            validation = self.validate_instance_from_file(extracted_json,
                                                          self.content_IDs[i],
                                                          self.base_schema)
            self.errors[self.content_IDs[i]] = validation

    @staticmethod
    def grab_user_content(client_identifier):
        """
        Grab all content for a given user ID as an XML and outputs it as a JSON
        :param client_identifier: the user ID
        :return: the dictionary containing the XML
        """
        full_url = "http://flowrepository.org/list?client=" + client_identifier
        response = request("GET", full_url)
        return parker.data((fromstring(response.text)))

    def get_user_content_id(self, client_identifier):
        """
        Return all IDs found in the user content XML
        :param client_identifier: the user content ID
        :return: a list of all IDs there were identified in the variable returned by the API
        """
        ids = []
        user_data = self.grab_user_content(client_identifier)

        for experiment in user_data['public-experiments']['experiment']:
            ids.append(experiment['id'])

        return ids

    @staticmethod
    def grab_experiment_from_api(client_identifier, item_identifier):
        """
        Retrieve the experiment metadata and return it as a python object
        :param client_identifier: the client identifier (apiKey)
        :param item_identifier: the item identifier that should be retrieved
        :return: the python object obtained from the XML
        """
        full_url = "http://flowrepository.org/list/" \
                   + item_identifier \
                   + "?client=" \
                   + client_identifier
        response = request("GET", full_url)
        return parker.data((fromstring(response.text)))["public-experiments"]["experiment"]

    @staticmethod
    def validate_instance_from_file(instance, item_id, schema_name):
        """
        Method to output the extracted JSON into a file and validate it against the given schema
        :param instance: the instance to output into a file
        :param item_id: the instance ID needed to create the file name
        :param schema_name: the schema to check against
        :return errors: a list of fields that have an error for this instance
        """
        file_name = item_id + '.json'
        file_full_path = os.path.join(os.path.dirname(__file__),
                                      "../tests/data/MiFlowCyt/" + file_name)

        with open(file_full_path, 'w') as outfile:
            dump(instance, outfile)
        outfile.close()

        errors = validate_instance(
            os.path.join(os.path.dirname(__file__), "../tests/data/MiFlowCyt/"),
            schema_name,
            os.path.join(os.path.dirname(__file__), "../tests/data/MiFlowCyt/"),
            file_name,
            1,
            {})
        return errors


'''
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


def transform_json(instance, schema, mapping):
    """
    :param instance: an instance JSON which doesn't necesarilly follow the JSON schema
    :param schema: a JSON schema which will be used as base for the transformation - might not be needed
    :param mapping: a dictionary with the mapping between the original JSON fields and fields from the JSON schema
    :return: the transformed JSON following the JSON schema structure
    """
    ignored_keys = ["@id", "@type", "@context"]

    total_fields = 0
    matched_field = 0
    matched_fields = []

    for field in schema['properties']:
        if field not in ignored_keys:

            total_fields += 1
            if field in mapping:
                processing_field = mapping[field]
            else:
                processing_field = field

            if processing_field in instance:
                matched_field += 1
                matched_fields.append((field, processing_field))

    print("Matched: " + str(matched_field) + " out of " + str(total_fields))
    return matched_fields
'''

if __name__ == '__main__':

    MAPPING = {
        'date': S('experiment-dates'),
        'primaryContact': S('primary-researcher'),
        'qualityControlMeasures': S('quality-control-measures'),
        'conclusions': S('conclusion'),
        'organization': OptionalS('organizations'),
        'purpose': S('purpose'),
        'keywords': S('keywords'),
        'experimentVariables': OptionalS('experimentVariables'),
        'other': OptionalS('other')
    }

    process_instances = FlowRepoClient(MAPPING, "experiment_schema.json", 10)
    print(process_instances.errors)
