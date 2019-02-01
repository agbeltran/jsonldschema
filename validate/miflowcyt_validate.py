import requests
import xmljson
import xml.etree.ElementTree as elemTree
from json import dump, load
import os
import jsonbender
import json
from collections import OrderedDict
from jsonschema.validators import RefResolver, Draft4Validator
from validate.jsonschema_validator import validate_instance


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
        self.context_url = "https://w3id.org/mircat/miflowcyt/context/obo/experiment_obo_context.jsonld"
        self.schemas = []
        self.mapping = "https://fairsharing.github.io/mircat/miflowcyt/schema_context_mapping.json"
        self.resolver = self.create_resolver()
        self.validator = Draft4Validator(self.resolver[1], resolver=self.resolver[0])

        self.user_accessible_ids = self.get_user_content_id()

    def make_validation(self, number_of_items, error_printing):
        """ Method to run the mapping for the given number of items

        :param number_of_items: the number of items to process
        :param error_printing: 0 or 1 to determine not to show or to show the errors
        :return: a dictionary containing the list of errors for all processed items
        """
        valid = []
        invalid = []
        content = self.get_all_experiments(number_of_items)

        if isinstance(self.user_accessible_ids, Exception):
            return Exception("Error with client ID " + self.clientID)

        else:
            for raw_experiment in content:
                experiment = self.preprocess_content(content[raw_experiment])
                try:
                    validation = self.validator.validate(experiment)
                    print(validation)
                except Exception as e:
                    raise e

    def get_user_content_id(self):
        """ Return all IDs found in the user content XML

        :return: a list of all IDs there were identified in the variable returned by the API
        """

        full_url = "http://flowrepository.org/list?client=" + self.clientID
        ids = []
        response = requests.request("GET", full_url)

        if response.status_code == 404:
            return Exception("Verify your client ID (" + self.clientID + ")")

        else:
            user_data = xmljson.parker.data((elemTree.fromstring(response.text)))

            for experiment in user_data['public-experiments']['experiment']:
                ids.append(experiment['id'])

            return ids

    def grab_experiment_from_api(self, item_identifier):
        """ Retrieve the experimental metadata and return it as a python object

        :param item_identifier: the item identifier that should be retrieved
        :return: the python object obtained from the XML
        """
        full_url = "http://flowrepository.org/list/" \
                   + item_identifier \
                   + "?client=" \
                   + self.clientID
        try:
            response = requests.request("GET", full_url)
            if response.status_code == 404:
                return Exception("Item %s could not be found" % item_identifier)
            return response.text
        except Exception:
            return Exception('Problem with item %s' % item_identifier)

    def get_all_experiments(self, max_number):
        contents = {}

        if max_number < len(self.user_accessible_ids):
            for i in range(max_number):
                current_content = self.grab_experiment_from_api(self.user_accessible_ids[i])
                contents[self.user_accessible_ids[i]] = current_content

        return contents

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

    def inject_context(self):
        context_mapping = json.loads(requests.get(self.mapping).text)["contexts"]
        for schema in self.schemas:

            for field_property in schema:
                prop = field_property + "_schema.json"

                if prop in context_mapping.keys():

                    if type(schema[field_property]) == list:
                        for item in schema[field_property]:
                            item["@context"] = context_mapping[prop]
                            item["@type"] = field_property.capitalize()
                    else:
                        schema[field_property]["@context"] = context_mapping[prop]
                        schema[field_property]["@type"] = field_property.capitalize()

            schema["@context"] = self.context_url
            schema["@type"] = "Experiment"

        return self.schemas

    def preprocess_content(self, content):
        experience_metadata = xmljson.parker.data((elemTree.fromstring(
            content)))["public-experiments"]["experiment"]
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
                extracted_json['other']['related-publications'] = [
                    extracted_json['related-publications']['publication']]
            else:
                extracted_json['other']['related-publications'] = extracted_json['related-publications']['publication']

        for field in extracted_json.keys():
            if extracted_json[field] is None:
                extracted_json[field] = ""
            if field == "primaryContact":
                extracted_json["primary_contact"] = extracted_json["primaryContact"]
                del extracted_json["primaryContact"]

        return extracted_json

    def create_resolver(self):
        schema = json.loads(requests.get(self.schema_url).text)
        return RefResolver(self.schema_url, schema, {}), schema
