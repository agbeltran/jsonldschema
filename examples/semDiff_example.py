# In order to compare two set of schemas, you can use different classes depending
# on whether your networks are resolved or not


# First case scenario, your networks are not resolved
# You will need to provide a dictionary of regex term/switch that will help
# translate the schemas IDs into contexts IDs
def compare_unresolved_network():

    # import the corresponding class
    from semDiff.fullDiff import FullDiffGenerator
    import json

    # set your main schemas URL
    MIACME_schema_url = "https://w3id.org/mircat/miacme/schema/miacme_schema.json"
    MyFlowCyt_schema_url = "https://w3id.org/mircat/miflowcyt/schema/miflowcyt_schema.json"

    # set the regex dictionary
    regex = {
        "/schema": "/context/obo",
        "_schema.json": "_obo_context.jsonld"
    }

    # Prepare the two networks
    MIACME_network = {
        "name": "MIACME",
        "regex": regex,
        "url": MIACME_schema_url
    }
    MyFlowCyt_network = {
        "name": "MyFlowCyt",
        "regex": regex,
        "url": MyFlowCyt_schema_url
    }

    # Run the comparison
    overlaps = FullDiffGenerator(MIACME_network, MyFlowCyt_network)
    print(json.dumps(overlaps, indent=4))


# Second case scenario, your networks are already resolved
def compare_resolved_network(network1, network2):

    # import the corresponding class
    from semDiff.fullDiff import FullSemDiffMultiple
    import json

    # prepare the input
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

    # run the comparison
    overlaps = FullSemDiffMultiple(prepared_input)
    print(json.dumps(overlaps, indent=4))
