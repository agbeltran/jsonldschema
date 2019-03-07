# In order to merge to set of schemas, you first need to get the output of the semantic
# diff comparators. You can then pass that result as an input to the merge class.


def merge_sets():
    # import the corresponding class
    import json
    from semDiff.fullDiff import FullSemDiffMultiple
    from semDiff.mergeEntities import MergeEntityFromDiff

    # Load your inputs
    with open('../tests/fullDiffOutput/network1.json', 'r') as networkFile:
        network1 = json.load(networkFile)
        networkFile.close()
    with open('../tests/fullDiffOutput/network2.json', 'r') as networkFile:
        network2 = json.load(networkFile)
        networkFile.close()

    # Prepare the input fot semantic diff
    prepared_input = [
        {
            "name": network1['name'],
            "schemas": network1['schemas'],
            "contexts": network1['contexts']
        },
        {
            "name": network2['name'],
            "schemas": network2['schemas'],
            "contexts": network2['contexts']
        }
    ]

    # Run the diff
    overlaps = FullSemDiffMultiple(prepared_input)

    # Prepare the merging input
    merging = {
        "network1": overlaps.networks[0],
        "network2": overlaps.networks[1],
        "overlaps": overlaps.output[0][0],
        "fields_to_merge": overlaps.ready_for_merge[0]
    }

    merged_schema = MergeEntityFromDiff(merging)  # Merge
    merged_schema.save('https://example.com/')  # Save the new schema set to the disk
