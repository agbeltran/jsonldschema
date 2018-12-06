import requests
import json
import os


class MircatClient:

    def __init__(self, client_url, port):
        self.headers = {
            "Content-Type": "application/json",
        }
        self.port = port
        self.base_URL = client_url
        self.request_base_url = self.base_URL + ":" + str(self.port)

    def create_context(self):
        extra_url = "/create_context"
        test_input = {
            "schema_url": "https://w3id.org/dats/schema/access_schema.json",
            "vocab":  {
                "obo": "http://purl.obolibrary.org/obo/",
                "sdo": "http://schema.org"
            }
        }
        response = requests.get(self.request_base_url + extra_url,
                                data=json.dumps(test_input),
                                headers=self.headers)

        return response.text

    def resolve_network(self):
        extra_url = "/resolve_network"
        test_input = {"schema_url": "https://w3id.org/dats/schema/access_schema.json"}
        response = requests.get(self.request_base_url + extra_url,
                                data=json.dumps(test_input),
                                headers=self.headers)
        return response.text

    def make_full_sem_diff(self):
        extra_url = "/semDiff"

        path = os.path.join(os.path.dirname(__file__), "../tests/data")
        with open(os.path.join(path, "dats.json"), 'r') as dats_file:
            # Load the JSON schema and close the file
            network1 = json.load(dats_file)
            dats_file.close()

        path = os.path.join(os.path.dirname(__file__), "../tests/data")
        with open(os.path.join(path, "miaca.json"), 'r') as miaca_file:
            # Load the JSON schema and close the file
            network2 = json.load(miaca_file)
            miaca_file.close()

        test_input = {
            "network_1": network1["schemas"],
            "network_2": network2["schemas"],
            "mapping": [network1["contexts"], network2["contexts"]]
        }
        response = requests.get(self.request_base_url + extra_url,
                                data=json.dumps(test_input),
                                headers=self.headers)
        return response.text

    def validate_schema(self):
        extra_url = "/validate/schema"
        schema_url = "https://w3id.org/dats/schema/access_schema.json"

        response = requests.get(self.request_base_url + extra_url,
                                data=json.dumps(schema_url),
                                headers=self.headers)

        return response.text

    def validate_instance(self):
        extra_url = "/validate/instance"

        user_input = {
            "schema_url": "https://w3id.org/dats/schema/activity_schema.json",
            "instance_url": "https://w3id.org/mircat/miflowcyt/schema/sample_schema.json"
        }

        response = requests.get(self.request_base_url + extra_url,
                                data=json.dumps(user_input),
                                headers=self.headers)

        return response.text


if __name__ == '__main__':
    client = MircatClient("http://localhost", 8001)
    # print(client.create_context())
    # print(client.resolve_network())
    # print(client.make_full_sem_diff())
    # print(client.validate_schema())
    print(client.validate_instance())
