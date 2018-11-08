import requests
import json
import os
import time
import datetime
import urllib.parse
from utils import to_boolean


STAGING_RESOURCE_API_ENDPOINT = "https://resource.staging.metadatacenter.org"
RESOURCE_API_ENDPOINT = "https://resource.metadatacenter.org"
TERMINOLOGY_API_ENDPOINT = "http://terminology.metadatacenter.org"
VALUE_RECOMMENDER_ENDPOINT = " http://valuerecommender.metadatacenter.org"


class CEDARClient:
    """ A client for the CEDAR API """

    def __init__(self):
        pass

    @staticmethod
    def get_headers(api_key):
        """ Method to build the HTTP request header

        :param api_key: the API Key to your CEDAR account
        :return: the HTTP headers
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": "apiKey " + api_key,
            "Cache-Control": "no-cache"
        }
        return headers

    @staticmethod
    def select_endpoint(server_type):
        """ Method to select the server (prod or dev)

        :param server_type: the type of server to select
        :return: the URL corresponding to the selected server
        """
        if server_type == "staging":
            return STAGING_RESOURCE_API_ENDPOINT
        elif server_type == "production":
            return RESOURCE_API_ENDPOINT

    @staticmethod
    def post(url, parameter, headers, directory):
        """ Method to post data to the CEDAR selected server and log the process

        :param url: the URL to the selected server
        :param parameter: parameters of the HTTP request
        :param headers: the header required by the HTTP request
        :param directory: the directory where to saved the log file
        """
        log_file = os.path.join(directory, "log.txt")
        with open(log_file, 'a') as log:
            directory_files = os.listdir(directory)
            log.write("\n**** Start upload ****\n")

            start = time.time()
            for cedar_file in directory_files:
                with open(cedar_file, 'rb') as f:
                    json_data = f.read()
                r = requests.post(url, params=parameter, data=json_data, headers=headers)

                #  log information
                request_time = time.time() - start
                log.write("\n")
                cur_time = "Current time: " + str(datetime.now()) + "\n"
                log.write(cur_time)
                response = cedar_file + "\n\t" + str(r.status_code).encode('utf-8') + ": " \
                                      + r.reason + "\n\t" + str(request_time) + "\n\t" \
                                      + str(r.url.encode('utf-8')) + "\n"
                log.write(response)
                resp_headers = "Headers:     " + str(r.request.headers).encode('utf-8') + "\n\n"
                log.write(resp_headers)
                try:
                    resp_text = "Text:     " + str(r.text).encode('utf-8') + "\n\n\n"
                except UnicodeEncodeError:
                    resp_text = "text failed to encode \n\n\n"
                log.write(resp_text)
                print(cur_time + response + resp_headers + resp_text)
            end = time.time()

            elapsed = end - start
            elapsed_message = "\nElapsed time: " + str(elapsed) + "\n"
            log.write(elapsed_message)
            log.write("\n**** Finish upload ****\n")
            print(elapsed_message)

    def get_users(self, endpoint_type, api_key):
        """ Method to get all users from the server

        :param endpoint_type: url to the CEDAR selected server
        :param api_key: your CEDAR user API key
        :return: a request response
        """
        headers = self.get_headers(api_key)
        endpoint = self.select_endpoint(endpoint_type)
        response = requests.request("GET", endpoint+"/users", headers=headers)
        return response

    def validate_resource(self, api_key, request_url, resource):
        """ Method to validate a resource against the server

        :param api_key: your CEDAR user API key
        :param request_url: the URL to run the validation from
        :param resource: the resource to validate
        :return: True or False, depending if the resource validated or not, and a message
        """
        headers = self.get_headers(api_key)
        response = requests.request("POST", request_url,
                                    headers=headers, data=json.dumps(resource), verify=True)
        if response.status_code == requests.codes.ok:
            message = json.loads(response.text)
            return to_boolean(message["validates"]), message
        else:
            response.raise_for_status()

    def validate_template(self, server_alias, api_key, template):
        """ Method to validate a CEDAR template

        :param server_alias: the URL to run the validation from
        :param api_key: your CEDAR user API key
        :param template: the resource to validate as a template
        :return: a request response
        """
        request_url = self.select_endpoint(server_alias)+"/command/validate?resource_type=template"
        return self.validate_resource(api_key, request_url, template)

    def validate_element(self, server_alias, api_key, element):
        """ Method to validate a CEDAR template element

        :param server_alias: the URL to run the validation from
        :param api_key: your CEDAR user API key
        :param element: the resource to validate as a template
        :return: a request response
        """
        request_url = self.select_endpoint(server_alias)+"/command/validate?resource_type=element"
        return self.validate_resource(api_key, request_url, element)

    def validate_instance(self, server_address, api_key, instance):
        """ Method to validate a JSON instance against the corresponding resource on CEDAR

        :param server_address: the CEDAR server URL
        :param api_key: your CEDAR user API key
        :param instance: the resource to validate as an instance
        :return:  a request response
        """
        request_url = server_address + "/command/validate?resource_type=instance"
        return self.validate_resource(api_key, request_url, instance)

    def upload_resource(self, api_key, request_url, resource):
        """ Upload the given resource to the CEDAR server

        :param api_key: your CEDAR user API key
        :param request_url: the CEDAR server URL to post to
        :param resource: the resource to upload
        :return: a response text loaded as a dictionary
        """
        headers = self.get_headers(api_key)
        response = requests.request("POST", request_url, headers=headers,
                                    data=json.dumps(resource), verify=True)
        if response.status_code == requests.codes.ok:
            return json.loads(response.text)
        else:
            response.raise_for_status()

    def get_template_content(self, endpoint_type, api_key, template_id):
        """ Get the content of a CEDAR template

        :param endpoint_type: the type of server to prompt
        :param api_key: your CEDAR user API key
        :param template_id: the CEDAR target template's ID
        :return: a request response
        """
        headers = self.get_headers(api_key)
        request_url = self.select_endpoint(endpoint_type) \
            + "/templates/https%3A%2F%2Frepo.metadatacenter.org%2Ftemplates%2F" \
            + template_id
        response = requests.request("GET", request_url, headers=headers)
        return response

    def get_folder_content(self, endpoint_type, api_key, folder_id):
        """ Get the content of a folder from CEDAR

        :param endpoint_type: the type of server to prompt
        :param api_key: your CEDAR user API key
        :param folder_id: the CEDAR target folder's ID
        :return: a request response
        """
        headers = self.get_headers(api_key)
        request_url = self.select_endpoint(endpoint_type) \
            + "/folders/https%3A%2F%2Frepo.metadatacenter.org%2Ffolders%2F" + folder_id
        response = requests.request("GET", request_url, headers=headers)
        return response

    def create_template(self, endpoint_type, api_key, folder_id, template_file):
        """ Post a new schema to the selected folder id

        :param endpoint_type: the type of server to prompt
        :param api_key: your CEDAR user API key
        :param folder_id: the CEDAR target folder's ID
        :param template_file: the CEDAR target template's ID
        :return: a request response
        """
        headers = self.get_headers(api_key)
        request_url = self.select_endpoint(endpoint_type) \
            + "/templates?folder_id=https%3A%2F%2Frepo.metadatacenter.org%2Ffolders%2F" + folder_id
        upload_schema = json.loads(template_file)
        response = requests.request("POST", request_url,
                                    headers=headers, data=json.dumps(upload_schema), verify=True)
        return response

    def create_folder(self,
                      endpoint_type,
                      api_key,
                      target_folder_id,
                      new_folder_name,
                      new_folder_description):
        """ Create a folder with new_folder_name in the target_folder_id location

        :param endpoint_type: the type of server to prompt
        :param api_key: your CEDAR user API key
        :param target_folder_id: he CEDAR target folder's ID where the new folder will be created
        :param new_folder_name: the new folder name to create
        :param new_folder_description: the new folder description to create
        :return: a request response
        """
        headers = self.get_headers(api_key)
        request_url = self.select_endpoint(endpoint_type) + '/folders'
        folder_json = {
            "folderId": "https://repo.metadatacenter.org/folders/"+target_folder_id,
            "name": new_folder_name,
            "description": new_folder_description
        }
        response = requests.request("POST", request_url,
                                    headers=headers, data=json.dumps(folder_json), verify=True)
        return response

    def delete_folder(self, endpoint_type, api_key, folder_id):
        """ Delete a given folder from the server

        :param endpoint_type: the type of server to prompt
        :param api_key: your CEDAR user API key
        :param folder_id: the CEDAR target folder's ID
        :return: a request response
        """
        headers = self.get_headers(api_key)
        requests_url = self.select_endpoint(endpoint_type) \
            + "/folders/" + urllib.parse.quote_plus(folder_id)
        response = requests.request("DELETE", requests_url, headers=headers)
        return response

    def delete_elements(self, endpoint_type, api_key, folder_id):
        """ Delete the elements and templates inside a folder

        :param endpoint_type: the type of server to prompt
        :param api_key: your CEDAR user API key
        :param folder_id: the CEDAR target folder's ID
        :return: a request response
        """

        target_types = ["element", "template"]
        responses = []
        for target_type in target_types:

            headers = self.get_headers(api_key)
            endpoint = self.select_endpoint(endpoint_type)

            targets_url = str(endpoint +
                              "/folders/https%3A%2F%2Frepo.metadatacenter.org%2Ffolders%2F" +
                              folder_id +
                              "/contents?resource_types=" +
                              target_type +
                              "&version=all&publication_status=all&sort=name&limit=500")

            target_responses = requests.request("GET", targets_url, headers=headers)
            for resource in json.loads(target_responses.text)["resources"]:
                target_id = resource['@id'].split('/')[-1]
                if target_type == 'template':
                    response = self.delete_template(endpoint, api_key, target_id)
                else:
                    response = self.delete_template_element(endpoint, api_key, target_id)
                responses.append(response)
        return responses

    def delete_template(self, endpoint, api_key, template_id):
        request_url = endpoint + \
                      "/templates/https%3A%2F%2Frepo.metadatacenter.org%2Ftemplates%2F" + \
                      template_id
        headers = self.get_headers(api_key)
        response = requests.request("DELETE", request_url, headers=headers)
        return response

    def delete_template_element(self, endpoint, api_key, template_id):
        request_url = endpoint + \
                      "/template-elements/https%3A%2F%2Frepo.metadatacenter.org" + \
                      "%2Ftemplate-elements%2F" + \
                      template_id
        headers = self.get_headers(api_key)
        response = requests.request("DELETE", request_url, headers=headers)
        return response

    def create_template_element(self, endpoint_type, api_key, folder_id, template_resource):
        """ Create a new template element on the given server

        :param endpoint_type: the type of server to prompt
        :param api_key: your CEDAR user API key
        :param folder_id: the CEDAR target folder's ID
        :param template_resource: the resource to post
        :return: a request response
        """
        headers = self.get_headers(api_key)
        request_url = self.select_endpoint(endpoint_type) \
            + "/template-elements?folder_id=https%3A%2F%2Frepo.metadatacenter.org%2Ffolders%2F" \
            + folder_id
        with open(template_resource, 'r') as template:
            upload_schema = json.load(template)
        response = requests.request("POST", request_url,
                                    headers=headers,
                                    data=json.dumps(upload_schema),
                                    verify=True)
        print(response.content)
        return response

    def update_template(self, endpoint_type, api_key, template_file):
        """ Update the content of template_file into the selected template

        :param endpoint_type: "staging" or "production"
        :param api_key: your CEDAR user API key
        :param template_file: the full path to a local template JSON file
        :return: a request response
        """
        headers = self.get_headers(api_key)
        with open(template_file, 'r') as template:
            upload_schema = json.load(template)
        template_id = upload_schema['@id'].replace(
            'https://repo.metadatacenter.org/templates/', '')
        request_url = self.select_endpoint(endpoint_type) \
            + "/templates/https%3A%2F%2Frepo.metadatacenter.org%2Ftemplates%2F" + template_id
        response = requests.request("PUT", request_url,
                                    headers=headers, data=json.dumps(upload_schema), verify=True)
        return response

    def upload_element(self, server_alias, api_key, schema_file, remote_folder_id):
        """ Upload a template element to the server

        :param server_alias: the type of server to prompt
        :param api_key: your CEDAR user API key
        :param schema_file: the full path to a local template element JSON file
        :param remote_folder_id: the CEDAR target folder's ID
        :return: a request response
        """
        request_url = self.select_endpoint(server_alias) \
            + "/template-elements?folder_id=" + remote_folder_id
        return self.upload_resource(api_key, request_url, schema_file)
