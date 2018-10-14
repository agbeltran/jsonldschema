from semDiff.fullDiff import FullSemDiff
import json
import os

path = os.path.join(os.path.dirname(__file__), "./data")
with open(os.path.join(path, "dats.json"), 'r') as dats_file:
    # Load the JSON schema and close the file
    network1 = json.load(dats_file)
    dats_file.close()

path = os.path.join(os.path.dirname(__file__), "./data")
with open(os.path.join(path, "miaca.json"), 'r') as miaca_file:
    # Load the JSON schema and close the file
    network2 = json.load(miaca_file)
    miaca_file.close()

networks_contexts = [network1["contexts"], network2["contexts"]]
full_diff = FullSemDiff(networks_contexts, network1["schemas"], network2["schemas"])

output = {
    "network1": network1,
    "network2": network2,
    "overlaps": full_diff.twins
}

file_name = network1["name"] + '_VS_' + network2["name"] + '_overlaps.json'
file_full_path = os.path.join(os.path.dirname(__file__), 'fullDiffOutput/' + file_name)

with open(file_full_path, 'w') as outfile:
    json.dump(output, outfile)
outfile.close()
