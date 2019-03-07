# The Miflowcyt functionality provide access to the flow repository endpoint.
# From there it gathers metadata about flow cytometry experiments as XML.
# It will then transform these XML into a JSON and inject attributes to
# obtain a final JSON-LD that can be validated against a schema

# To proceed, you must first create a variable that hold the path to a mapping file
# and your user API key from the config file
# You also need to import the FlowRepoClient class from the miflowcyt_validate file of the
# the validate module
import os
import json
from validate.miflowcyt_validate import FlowRepoClient

# Get the path to the mapping file
map_file = os.path.join(os.path.dirname(__file__),
                        "../tests/data/MiFlowCyt/experiment_mapping.json")

base_schema = "experiment_schema.json"  # Get the name of the schema

# Load your API KEY from the config.json file
configfile_path = os.path.join(os.path.dirname(__file__), "../tests/test_config.json")
with open(configfile_path) as config_data_file:
    config_json = json.load(config_data_file)
    config_data_file.close()
apiKey = config_json["flowrepo_userID"]
items = 1  # Initialize the number of instances to gather from the API

client = FlowRepoClient(map_file, apiKey, items)  # initialize the class
instances = client.inject_context()  # inject the attributes to obtain a JSON-LD
print(json.dumps(instances, indent=4))  # Enjoy
