import requests
import json

STAGING_RESOURCE_API_ENDPOINT = "https://resource.staging.metadatacenter.org"
RESOURCE_API_ENDPOINT = "https://resource.metadatacenter.org"
TERMINOLOGY_API_ENDPOINT = "http://terminology.metadatacenter.org"
VALUE_RECOMMENDER_ENDPOINT = " http://valuerecommender.metadatacenter.org"

class CEDARClient():
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

    def get_users(self, endpoint_type, api_key):
        headers = self.get_headers(api_key)
        endpoint = self.selectEndpoint(endpoint_type)
        response = requests.request("GET", endpoint+"/users", headers=headers)
        return response

    def validate_resource(self, api_key, request_url, resource):
        headers = self.get_headers(api_key)
        response = requests.request("POST", request_url, headers=headers, data=json.dumps(resource), verify=True)
        if response.status_code == requests.codes.ok:
            message = json.loads(response.text)
            return message
        else:
            response.raise_for_status()

    def validate_template(self, server_alias, api_key, template):
        request_url = self.selectEndpoint(server_alias) + "/command/validate?resource_type=template"
        return self.validate_resource(api_key, request_url, template)

    def validate_element(self, server_alias, api_key, element):
        request_url = self.selectEndpoint(server_alias) + "/command/validate?resource_type=element"
        return self.validate_resource(api_key, request_url, element)

    def validate_instance(self, server_address, api_key, instance):
        request_url = server_address + "/command/validate?resource_type=instance"
        return self.validate_resource(api_key, request_url, instance)



def paging(url, params, data, method):
    page = 0
    pagesize = 1000
    maxcount = None
    # set a default dict for parameters
    if params == None:
        params = {}
    while maxcount == None or page < maxcount:
        params['page'] = page
        params['pageSize'] = pagesize

        print('retrieving page', page, 'of', maxcount, 'from', url)

        if method == 'GET':
            print("GETing", url)
            r = requests.get(url, params=params, data=data)
        elif method == 'PUT':
            print("PUTing", url)
            r = requests.put(url, params=params, data=data)
        elif method == 'POST':
            print("POSTing", url)
            r = requests.post(url, params=params, data=data)

        if r.status_code != requests.codes.ok:
            print(r)
            raise RuntimeError("Non-200 status code")

        maxcount = int(r.json()['metadata']['pagination']['totalPages'])

        for data in r.json()['result']['data']:
            yield data

        page += 1
