from requests import request
from xmljson import parker
from xml.etree.ElementTree import fromstring
from json import dump, load
import os
from jsonbender import bend, OptionalS, S, K, F
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
        self.MAPPING = self.get_mapping(mapping)
        self.base_schema = base_schema
        self.content_IDs = self.get_user_content_id(self.clientID)

        for i in range(range_limit):
            experience_metadata = self.grab_experiment_from_api(self.clientID, self.content_IDs[i])
            extracted_json = bend(self.MAPPING, experience_metadata)
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

    @staticmethod
    def get_mapping(mapping_file_name):
        """
        Build the mapping dictionary based on the given mapping file
        :param mapping_file_name: the name of the mapping file
        :return mapping: the mapping of the fields
        """
        mapping = {}
        with open(mapping_file_name) as mapping_var:
            raw_mapping = load(mapping_var)
        mapping_var.close()

        # For each mapped field in the mapping file
        for mapped_item in raw_mapping:

            # if the value of the field is a string
            if isinstance(raw_mapping[mapped_item], str):
                mapping[mapped_item] = OptionalS(raw_mapping[mapped_item])

            # if the value of the field is an object
            elif isinstance(raw_mapping[mapped_item], object):

                # Raise an error if a value/option is missing
                if 'value' not in raw_mapping[mapped_item] or \
                        ('benderOption' not in raw_mapping[mapped_item]):
                    raise Exception("The mapping file is missing a value or the bender option "
                                    "for " + mapped_item)
                else:
                    if raw_mapping[mapped_item]['benderOption'] == "default":
                        mapping[mapped_item] = OptionalS(raw_mapping[mapped_item]['value'])
                    elif raw_mapping[mapped_item]['benderOption'] == "raiseErrors":
                        mapping[mapped_item] = S(raw_mapping[mapped_item]['value'])
                    elif raw_mapping[mapped_item]['benderOption'] == "simple":
                        mapping[mapped_item] = K(raw_mapping[mapped_item]['value'])
                    elif raw_mapping[mapped_item]['benderOption'] == "inject":
                        mapping[mapped_item] = F(raw_mapping[mapped_item]['value'])

        return mapping


if __name__ == '__main__':
    map_file = os.path.join(os.path.dirname(__file__),
                            "../tests/data/MiFlowCyt/experiment_mapping.json")

    process_instances = FlowRepoClient(map_file, "experiment_schema.json", 1)
    print(process_instances.errors)
