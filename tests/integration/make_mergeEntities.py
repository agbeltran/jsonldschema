import json
import os
from semDiff.mergeEntities import MergeEntityFromDiff


if __name__ == '__main__':
    input_dir = os.path.join(os.path.dirname(__file__), "../fullDiffOutput/")

    """ MIACA AND MIACME """
    input_file = os.path.join(input_dir, "MIACA_VS_MIACME.json")
    with open(input_file, "r") as input_data:
        MIACA_VS_MIACME = json.loads(input_data.read())
        input_data.close()
    merged_network = MergeEntityFromDiff(MIACA_VS_MIACME)
    merged_network.validate_output()
    if len(merged_network.errors) > 0:
        print('ERRORS, saves abort')
        print(json.dumps(merged_network.errors, indent=4))
        exit()  # comment to save anyway
    merged_network.save("https://w3id.org/mircat/miaca_miacme_merge/")

    """ MIACA AND M """
    input_file = os.path.join(input_dir, "MIACA_VS_MIACME.json")
    with open(input_file, "r") as input_data:
        MIACA_VS_MIACME = json.loads(input_data.read())
        input_data.close()
    merged_network = MergeEntityFromDiff(MIACA_VS_MIACME)
    merged_network.validate_output()
    if len(merged_network.errors) > 0:
        print('ERRORS, saves abort')
        print(json.dumps(merged_network.errors, indent=4))
        exit()  # comment to save anyway
    merged_network.save("https://w3id.org/mircat/miaca_miacme_merge/")

    """ MIACME AND MIACA """
    input_file = os.path.join(input_dir, "MIACME_VS_MIACA.json")
    with open(input_file, "r") as input_data:
        MIACME_VS_MIACA = json.loads(input_data.read())
        input_data.close()
    merged_network = MergeEntityFromDiff(MIACME_VS_MIACA)
    merged_network.save("https://w3id.org/mircat/miacme_miaca_merge/")
    print(merged_network.output)

    """MIACME AND MiFlowCyt"""
    input_file = "../fullDiffOutput/MIACME_VS_MyFlowCyt.json"
    with open(input_file, "r") as input_data:
        MIACME_VS_MIACA = json.loads(input_data.read())
        input_data.close()
    merged_network = MergeEntityFromDiff(MIACME_VS_MIACA)
    merged_network.save("https://w3id.org/mircat/miaca_miflowcyt_merge/")

    """MIACME AND MiFlowCyt"""
    input_file = "../fullDiffOutput/MIACME_VS_MyFlowCyt.json"
    with open(input_file, "r") as input_data:
        MIACME_VS_MIACA = json.loads(input_data.read())
        input_data.close()
    merged_network = MergeEntityFromDiff(MIACME_VS_MIACA)
    merged_network.save("https://w3id.org/mircat/miacme_MyFlowCyt_merge/")

