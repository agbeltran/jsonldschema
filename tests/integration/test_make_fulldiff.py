import json
import os
from semDiff.fullDiff import FullDiffGenerator


output_base_path = os.path.join(os.path.dirname(__file__), "../fullDiffOutput/")


def make_diff(network1, network2):
    print("-----------------------------")
    print("Comparing %s VS %s, please wait" % (network1["name"], network2["name"]))
    overlaps = FullDiffGenerator(network1, network2)
    print("Result:", json.dumps(overlaps.json))

    filename = network1["name"] + "_VS_" + network2["name"] + ".json"

    with open(os.path.join(output_base_path, filename), "w") as outputFile:
        outputFile.write(json.dumps(overlaps.json, indent=4))
        outputFile.close()


if __name__ == '__main__':

    MIACME_schema_url = "https://w3id.org/mircat/miacme/schema/miacme_schema.json"
    MIACA_schema_url = "https://w3id.org/mircat/miaca/schema/miaca_schema.json"
    MyFlowCyt_schema_url = "https://w3id.org/mircat/miflowcyt/schema/miflowcyt_schema.json"
    regex = {
        "/schema": "/context/obo",
        "_schema.json": "_obo_context.jsonld"
    }

    MIACME_network = {
        "name": "MIACME",
        "regex": regex,
        "url": MIACME_schema_url
    }
    MIACA_network = {
        "name": "MIACA",
        "regex": regex,
        "url": MIACA_schema_url
    }
    MyFlowCyt_network = {
        "name": "MyFlowCyt",
        "regex": regex,
        "url": MyFlowCyt_schema_url
    }

    make_diff(MIACA_network, MIACA_network)
    make_diff(MIACA_network, MIACME_network)
    make_diff(MIACME_network, MIACA_network)
    make_diff(MIACME_network, MIACME_network)
    make_diff(MIACA_network, MyFlowCyt_network)
    make_diff(MyFlowCyt_network, MIACA_network)
    make_diff(MIACME_network, MyFlowCyt_network)
    make_diff(MyFlowCyt_network, MIACME_network)
    make_diff(MyFlowCyt_network, MyFlowCyt_network)
