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
    and validate the JSON instances against their JSON schema.
    The transformation from XML to JSON relies on the
    JSONBender library (https://github.com/Onyo/jsonbender).
    """

    def __init__(self, mapping, client_id, number_of_items):
        """ The class constructor

        :param mapping: the mapping dictionary containing the jsonbender objects
            (see https://github.com/Onyo/jsonbender)
        :type mapping: file
        :param client_id: identifier of the client
        :type client_id: str

        """
        self.errors = {}
        self.instances = []
        self.main_context_url = ""
        self.clientID = client_id
        self.item_number = number_of_items
        self.bender_mapping_file = mapping

        self.mapping_url = "https://fairsharing.github.io/mircat/miflowcyt/" \
                           "schema_context_mapping.json"
        self.base_schema = "experiment_schema.json"
        self.schema_url = "https://w3id.org/mircat/miflowcyt/schema/" + self.base_schema

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

            if "public-experiments" in user_data.keys() \
                    and "experiment" in user_data["public-experiments"].keys():
                for experiment in user_data['public-experiments']['experiment']:
                    ids.append(experiment['id'])

            return ids

    def grab_experiment_from_api(self, item_identifier):
        """ Retrieve the experimental metadata and return it as XML document object

        :param item_identifier: the item identifier that should be retrieved
        :return: the XML document object
        """
        full_url = "http://flowrepository.org/list/" \
                   + item_identifier \
                   + "?client=" \
                   + self.clientID
        response = requests.request("GET", full_url)
        if response.status_code == 404 or response.status_code == 400:
            return Exception("Item %s could not be found" % item_identifier)
        return response.text

    def get_all_experiments(self, max_number, accessible_ids):
        """ Grab all experiments from the API for the given number

        :param max_number: the number of item to retrieve
        :type max_number: int
        :param accessible_ids: the ids that this use can fetch
        :type accessible_ids: list
        :return: the experiments XMLs
        """

        contents = {}

        if max_number < len(accessible_ids):
            for i in range(max_number):
                current_content = self.grab_experiment_from_api(accessible_ids[i])
                contents[accessible_ids[i]] = current_content

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
        """
        Transform the myflowcyt JSON into a JSON-LD by injecting @context and @type keywords
        :return: a JSON-LD of the myflowcyt JSON
        """

        instances, errors = self.make_validation()

        context_mapping = json.loads(requests.get(self.mapping_url).text)["contexts"]
        self.main_context_url = context_mapping[self.base_schema]

        for instance_name in instances:
            instance = instances[instance_name]

            for field in instance:
                prop = field + "_schema.json"
                if prop in context_mapping.keys():
                    if type(instance[field]) == list:
                        for item in instance[field]:
                            item["@context"] = context_mapping[prop]
                            item["@type"] = field.capitalize()
                    elif type(instance[field]) == dict:
                        instance[field]["@context"] = context_mapping[prop]
                        instance[field]["@type"] = field.capitalize()

            instance["@context"] = self.main_context_url
            instance["@type"] = "Experiment"

        return instances

    def preprocess_content(self, content):
        """
        Preprocess the XML into a JSON that is compliant with the schema.
        :param content: str containing the XML
        :type content: str
        :return: a JSON schema cleaned from residual artifacts
        """
        mapping = self.get_mapping(self.bender_mapping_file)
        experience_metadata = xmljson.parker.data((elemTree.fromstring(
            content)))["public-experiments"]["experiment"]
        extracted_json = jsonbender.bend(mapping, experience_metadata)

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
                extracted_json['other']['related-publications'] = \
                    extracted_json['related-publications']['publication']

        if 'related-publications' in extracted_json.keys():
            extracted_json.pop('related-publications')

        for field in extracted_json.keys():
            if extracted_json[field] is None:
                extracted_json[field] = ""
            if field == "primaryContact":
                extracted_json["primary_contact"] = extracted_json["primaryContact"]
                del extracted_json["primaryContact"]

        return extracted_json

    def make_validation(self):
        """ Method to run the mapping for the given number of items

        :return: a dictionary containing the list of errors for all processed items
        """
        valid = {}
        invalid = {}

        user_accessible_ids = self.get_user_content_id()
        # print(user_accessible_ids)

        if isinstance(user_accessible_ids, Exception):
            return Exception("Error with client ID " + self.clientID)

        else:
            schema = json.loads(requests.get(self.schema_url).text)
            resolver = RefResolver(self.schema_url, schema, {})
            validator = Draft4Validator(schema, resolver=resolver)
            content = self.get_all_experiments(self.item_number, user_accessible_ids)

            for raw_experiment in content:
                experiment = self.preprocess_content(content[raw_experiment])
                try:
                    validation = validator.validate(experiment)
                    if validation is None:
                        valid[raw_experiment] = experiment
                    else:
                        invalid[raw_experiment] = validation
                except Exception as e:
                    invalid[raw_experiment] = "Unexpected error: " + str(e)
        return valid, invalid
