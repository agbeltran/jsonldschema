import requests
import json
import os
import time
import datetime

STAGING_RESOURCE_API_ENDPOINT = "https://resource.staging.metadatacenter.org"
RESOURCE_API_ENDPOINT = "https://resource.metadatacenter.org"
TERMINOLOGY_API_ENDPOINT = "http://terminology.metadatacenter.org"
VALUE_RECOMMENDER_ENDPOINT = " http://valuerecommender.metadatacenter.org"


class CEDARClient:

    def __init__(self):
        pass

    def get_headers(self, api_key):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "apiKey " + api_key,
            "Cache-Control": "no-cache"
        }
        return headers

    def selectEndpoint(self, type):
        if type == "staging":
            return STAGING_RESOURCE_API_ENDPOINT
        elif type == "production":
            return RESOURCE_API_ENDPOINT

    def post(url, parameter, headers, directory):
        log_file = os.path.join(directory, "log.txt")
        with open(log_file, 'a') as log:
            directory_files = os.listdir(directory)
            log.write("\n**** Start upload ****\n")

            start = time.time()
            for cedar_file in directory_files:
                with open(cedar_file, 'rb') as f:
                    json_data = f.read()
                r = requests.post(url, params=parameter, data=json_data, headers=headers)  # make request

                #  log information
                request_time = time.time() - start
                log.write("\n")
                cur_time = "Current time: " + str(datetime.now()) + "\n"
                log.write(cur_time)
                response = cedar_file + "\n\t" + str(r.status_code).encode('utf-8') + ": " + r.reason + "\n\t" + \
                           str(request_time) + "\n\t" + str(r.url.encode('utf-8')) + "\n"
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
        headers = self.get_headers(api_key)
        endpoint = self.selectEndpoint(endpoint_type)
        response = requests.request("GET", endpoint+"/users", headers=headers)
        return response

    def validate_resource(self, api_key, request_url, resource):
        headers = self.get_headers(api_key)
        response = requests.request("POST", request_url, headers=headers, data=json.dumps(resource), verify=True)
        return response

    def validate_template(self, server_alias, api_key, template):
        request_url = self.selectEndpoint(server_alias) + "/command/validate?resource_type=template"
        return self.validate_resource(api_key, request_url, template)

    def validate_element(self, server_alias, api_key, element):
        request_url = self.selectEndpoint(server_alias) + "/command/validate?resource_type=element"
        return self.validate_resource(api_key, request_url, element)

    def validate_instance(self, server_address, api_key, instance):
        request_url = server_address + "/command/validate?resource_type=instance"
        return self.validate_resource(api_key, request_url, instance)

    def upload_resource(self, api_key, request_url, resource):
        headers = self.get_headers(api_key)
        response = requests.request("POST", request_url, headers=headers, data=json.dumps(resource), verify=True)
        if response.status_code == requests.codes.ok:
            message = json.loads(response.text)
            return message
        else:
            response.raise_for_status()

    """ DOM'S FUNCTIONS """

    def get_template_content(self, endpoint_type, api_key, template_id):
        """ Get the content of a template"""
        headers = self.get_headers(api_key)
        request_url = self.selectEndpoint(endpoint_type) + "/templates/https%3A%2F%2Frepo.metadatacenter.org%2Ftemplates%2F" + template_id
        response = requests.request("GET", request_url, headers=headers)
        return response

    def get_folder_content(self, endpoint_type, api_key, folder_id):
        """ Get the content of a folder """
        headers = self.get_headers(api_key)
        request_url = self.selectEndpoint(endpoint_type) + "/folders/https%3A%2F%2Frepo.metadatacenter.org%2Ffolders%2F" + folder_id
        response = requests.request("GET", request_url, headers=headers)
        return response

    def create_template(self, endpoint_type, api_key, folder_id, template_file):
        """ Upload the schema to the selected folder id """
        headers = self.get_headers(api_key)
        request_url = self.selectEndpoint(endpoint_type) + "/templates?folder_id=https%3A%2F%2Frepo.metadatacenter.org%2Ffolders%2F" + folder_id
        with open(template_file, 'r') as template:
            upload_schema = json.load(template)
        response = requests.request("POST", request_url, headers=headers, data=json.dumps(upload_schema), verify=True)
        return response

    def update_template(self, endpoint_type, api_key, template_file):
        """ Update the content of template_file into the selected template"""
        headers = self.get_headers(api_key)
        with open(template_file, 'r') as template:
            upload_schema = json.load(template)
        template_id = upload_schema['@id'].replace('https://repo.metadatacenter.org/templates/', '')
        request_url = self.selectEndpoint(endpoint_type) + "/templates/https%3A%2F%2Frepo.metadatacenter.org%2Ftemplates%2F" + template_id
        response = requests.request("PUT", request_url, headers=headers, data=json.dumps(upload_schema), verify=True)
        return response

    def upload_element(self, server_alias, api_key, schema_file, remote_folder_id):
        request_url = self.selectEndpoint(server_alias) + "/template-elements?folder_id="+ remote_folder_id
        return self.upload_resource(api_key, request_url, schema_file)