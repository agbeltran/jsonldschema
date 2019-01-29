import requests
import xmljson
import xml.etree.ElementTree as elemTree
from json import dump, load
import os
import jsonbender
import json
from collections import OrderedDict
from validate.jsonschema_validator import validate_instance, validate_instance_from_url


class FlowRepoClient:
    """
    A class that provides functionality to download experiments from the
    FlowRepository (https://flowrepository.org/), transform the XML into JSON
    and validate the instances against their schema.
    The transformation from XML to JSON relies on the
    JSONBender library (https://github.com/Onyo/jsonbender).
    """

    def __init__(self, mapping, base_schema, client_id):
        """ The class constructor

        :param mapping: the mapping dictionary containing the jsonbender objects
            (see https://github.com/Onyo/jsonbender)

        """
        self.errors = {}
        self.clientID = client_id
        self.MAPPING = self.get_mapping(mapping)
        self.base_schema = base_schema
        self.schema_url = "https://w3id.org/mircat/miflowcyt/schema/experiment_schema.json"

    def make_validation(self, number_of_items):
        """ Method to run the mapping for the given number of items

        :param number_of_items: the number of items to process
        :return: a dictionary containing the list of errors for all processed items
        """
        content_ids = self.get_user_content_id(self.clientID)
        valid = []
        invalid = []

        if isinstance(content_ids, Exception):
            return Exception("Error with client ID " + self.clientID)

        else:
            try:
                for i in range(number_of_items):
                    response = self.grab_experiment_from_api(self.clientID, content_ids[i])

                    if response.status_code == 401:
                        return Exception("client " + self.clientID + " does not have access to " +
                                         content_ids[i])

                    elif response.status_code == 404:
                        return Exception("Item " + content_ids[i] + " could not be found")

                    else:
                        experience_metadata = xmljson.parker.data((elemTree.fromstring(
                            response.text)))["public-experiments"]["experiment"]
                        extracted_json = jsonbender.bend(self.MAPPING, experience_metadata)

                        if extracted_json['organization'] == "\n   ":
                            extracted_json['organization'] = []

                        if extracted_json['keywords'] == "\n   ":
                            extracted_json['keywords'] = []

                        if 'keywords' in extracted_json.keys() and \
                            type(extracted_json['keywords']) == OrderedDict and \
                                'keyword' in extracted_json['keywords'].keys():
                            if type(extracted_json['keywords']['keyword']) != list:
                                extracted_json['keywords'] = [extracted_json['keywords']['keyword']]
                            else:
                                extracted_json['keywords'] = extracted_json['keywords']['keyword']

                        if 'organization' in extracted_json.keys() and \
                            type(extracted_json['organization']) == OrderedDict and \
                                'organization' in extracted_json['organization'].keys():
                            if type(extracted_json['organization']['organization']) != list:
                                extracted_json['organization'] = [extracted_json['organization'][
                                    'organization']]
                            else:
                                extracted_json['organization'] = extracted_json['organization'][
                                    'organization']

                        if 'other' not in extracted_json.keys() \
                                or extracted_json['other'] is None:
                            extracted_json['other'] = {}

                        if 'related-publications' in extracted_json.keys() and \
                            type(extracted_json['related-publications']) == OrderedDict and \
                                'publication' in extracted_json['related-publications'].keys():
                            if type(extracted_json['related-publications']['publication']) != list:
                                extracted_json['other']['related-publications'] = [extracted_json['related-publications']['publication']]
                            else:
                                extracted_json['other']['related-publications'] = extracted_json['related-publications']['publication']

                        '''validation = self.validate_instance_from_file(extracted_json,
                                                                      content_ids[i],
                                                                      self.base_schema)'''

                        for field in extracted_json:
                            if extracted_json[field] is None:
                                extracted_json[field] = ""

                        try:
                            validation = validate_instance_from_url(self.schema_url, extracted_json)
                            print("Validated instance %s" % content_ids[i])
                            self.errors[content_ids[i]] = validation
                            if len(validation) == 0:
                                valid.append(content_ids[i])
                            else:
                                invalid.append(content_ids[i])
                        except Exception:
                            print("Problem with item %s" % content_ids[i])
                            print(json.dumps(extracted_json, indent=4))
                            invalid.append(content_ids[i])

                return self.errors, valid, invalid
            except IndexError:
                return Exception("The number of available items is inferior to the number you "
                                 "ask for")

    @staticmethod
    def grab_user_content(client_identifier):
        """ Grab all content for a given user ID as an XML and outputs it as a JSON.
        This method will grab all public experiments plus those only accessible to the user ID.

        :param client_identifier: the user ID
        :return: a dictionary containing the XML
        """
        full_url = "http://flowrepository.org/list?client=" + client_identifier
        response = requests.request("GET", full_url)
        return response

    def get_user_content_id(self, client_identifier):
        """ Return all IDs found in the user content XML

        :param client_identifier: the user content ID
        :return: a list of all IDs there were identified in the variable returned by the API
        """
        ids = []
        response = self.grab_user_content(client_identifier)

        if response.status_code == 404:
            return Exception("Verify your client ID (" + client_identifier + ")")

        else:
            user_data = xmljson.parker.data((elemTree.fromstring(response.text)))

            for experiment in user_data['public-experiments']['experiment']:
                ids.append(experiment['id'])

            return ids

    @staticmethod
    def grab_experiment_from_api(client_identifier, item_identifier):
        """ Retrieve the experimental metadata and return it as a python object

        :param client_identifier: the client identifier (apiKey)
        :param item_identifier: the item identifier that should be retrieved
        :return: the python object obtained from the XML
        """
        full_url = "http://flowrepository.org/list/" \
                   + item_identifier \
                   + "?client=" \
                   + client_identifier
        response = requests.request("GET", full_url)
        return response

    @staticmethod
    def validate_instance_from_file(instance, item_id, schema_name):
        """ Method to output the extracted JSON into a file and validate it against the given schema

        :param instance: the instance to output into a file
        :param item_id: the instance ID needed to create the file name
        :param schema_name: the schema to check against
        :return errors: a list of fields that have an error for this instance
        """

        try:
            file_name = item_id + '.json'
            file_full_path = os.path.join(os.path.dirname(__file__),
                                          "../tests/data/MiFlowCyt/" + file_name)

            with open(file_full_path, 'w') as outfile:
                dump(instance, outfile, indent=4)
            outfile.close()

            errors = validate_instance(
                os.path.join(os.path.dirname(__file__), "../tests/data/MiFlowCyt/"),
                schema_name,
                os.path.join(os.path.dirname(__file__), "../tests/data/MiFlowCyt/"),
                file_name,
                1,
                {})
            return errors
        except FileNotFoundError:
            return Exception("Please provide a valid schema")

    @staticmethod
    def get_mapping(mapping_file_name):
        """ Build the mapping dictionary based on the given mapping file

        :param mapping_file_name: the name of the mapping file
        :return mapping: the mapping of the fields
        """
        try:
            mapping = {}
            with open(mapping_file_name) as mapping_var:
                raw_mapping = load(mapping_var)
            mapping_var.close()

            # For each mapped field in the mapping file
            for mapped_item in raw_mapping:

                # if the value of the field is a string
                if isinstance(raw_mapping[mapped_item], str):
                    mapping[mapped_item] = jsonbender.OptionalS(raw_mapping[mapped_item])

                # if the value of the field is an object
                elif isinstance(raw_mapping[mapped_item], object):

                    # Raise an error if a value/option is missing
                    if 'value' not in raw_mapping[mapped_item] or \
                            ('benderOption' not in raw_mapping[mapped_item]):
                        raise Exception("The mapping file is missing a value or the bender option "
                                        "for " + mapped_item)
                    else:
                        if raw_mapping[mapped_item]['benderOption'] == "default":
                            mapping[mapped_item] = \
                                jsonbender.OptionalS(raw_mapping[mapped_item]['value'])
                        elif raw_mapping[mapped_item]['benderOption'] == "raiseErrors":
                            mapping[mapped_item] = jsonbender.S(raw_mapping[mapped_item]['value'])
                        elif raw_mapping[mapped_item]['benderOption'] == "simple":
                            mapping[mapped_item] = jsonbender.K(raw_mapping[mapped_item]['value'])
                        elif raw_mapping[mapped_item]['benderOption'] == "inject":
                            mapping[mapped_item] = jsonbender.F(raw_mapping[mapped_item]['value'])

            return mapping
        except FileNotFoundError:
            return Exception("Mapping file wasn't found")
