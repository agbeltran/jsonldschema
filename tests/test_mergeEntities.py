import unittest
import os
import json
from semDiff.mergeEntities import EntityMerge, MergeEntityFromDiff

schema_1 = {
    "id": "https://w3id.org/dats/schema/person_schema.json",
    "$schema": "http://json-schema.org/draft-04/schema",
    "title": "DATS person schema",
    "description": "A human being",
    "type": "object",
    "properties": {
        "@context": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "object"
                }
            ]
        },
        "@id": {"type": "string", "format": "uri"},
        "@type": {"type": "string", "enum": ["Person"]},
        "identifier": {
            "description": "Primary identifier for the person.",
            "$ref": "identifier_info_schema.json#"
        },
        "alternateIdentifiers": {
            "description": "Alternate identifiers for the person.",
            "type": "array",
            "items": {
                "$ref": "alternate_identifier_info_schema.json#"
            }
        },
        "fullName": {
            "description": "The first name, any middle names, and surname of a person.",
            "type": "string"
        },
        "firstName": {
            "description": "The given name of the person.",
            "type": "string"
        },
        "lastName": {
            "description": "The person's family name.",
            "type": "string"
        }
    },
    "additionalProperties": False
}
context_1 = {
    "@context": {
        "sdo": "https://schema.org/",
        "Person": "sdo:Person",
        "identifier": {
            "@id": "sdo:identifier",
            "@type": "sdo:Text"
        },
        "firstName": "sdo:givenName",
        "lastName": "sdo:familyName",
        "fullName": "sdo:name",
        "email": "sdo:email",
        "affiliations": "sdo:affiliation",
        "roles": "sdo:roleName"
    }
}

schema_2 = {
    "id": "https://w3id.org/dats/schema/person_schema.json",
    "$schema": "http://json-schema.org/draft-04/schema",
    "title": "DATS person schema",
    "description": "A human being",
    "type": "object",
    "properties": {
        "@context": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "object"
                }
            ]
        },
        "@id": {"type": "string", "format": "uri"},
        "@type": {"type": "string", "format": "uri"},
        "identifier": {
            "description": "Primary identifier for the person.",
            "$ref": "identifier_info_schema.json#"
        },
        "familyName": {
            "description": "The person's family name.",
            "type": "string"
        }
    },
    "additionalProperties": False
}
context_2 = {
    "@context": {
        "sdo": "https://schema.org/",
        "Person": "sdo:Person",
        "identifier": {
            "@id": "sdo:identifier",
            "@type": "sdo:Text"
        },
        "familyName": "sdo:familyName",
        "email": "sdo:email",
        "affiliations": "sdo:affiliation",
        "roles": "sdo:roleName"
    }
}


class EntityMergeTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(EntityMergeTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.merge = EntityMerge(schema_2, context_2, schema_1, context_1)

    def test___init__(self):

        # Verify that all fields in schema_2 are the same in the final output schema
        for field in schema_2["properties"]:
            self.assertTrue(self.merge.output_schema["properties"][field] == schema_2[
                "properties"][field])

        # Verify that all fields in context_2 are the same in the final output context
        for field in context_2["@context"]:
            self.assertTrue(self.merge.output_context["@context"][field] == context_2[
                "@context"][field])

        # Verify that fields from schema_1 that aren't common with schema_2 are also in the
        # final output
        self.assertTrue("alternateIdentifiers" in self.merge.output_schema["properties"].keys())
        self.assertTrue("fullName" in self.merge.output_schema["properties"].keys())
        self.assertTrue("firstName" in self.merge.output_schema["properties"].keys())

        # Verify that fields from context_1 that aren't common with context_2 are also in the
        # final output
        self.assertTrue("alternateIdentifiers" not in self.merge.output_context[
            "@context"].keys())
        self.assertTrue("fullName" in self.merge.output_context["@context"].keys())
        self.assertTrue("firstName" in self.merge.output_context["@context"].keys())


class MergeEntityFromDiffTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(MergeEntityFromDiffTestCase, self).__init__(*args, **kwargs)

        input_file = os.path.join(
            os.path.dirname(__file__), './fullDiffOutput/overlap_example.json')
        with open(input_file, 'r') as input_data:
            self.overlaps = json.loads(input_data.read())
            input_data.close()

    def test__init_(self):

        expected_out_file = os.path.join(os.path.dirname(__file__),
                                         './fullDiffOutput/merges/example_merge.json')
        with open(expected_out_file, "r") as outputFile:
            expected_output = json.loads(outputFile.read())

        merger = MergeEntityFromDiff(self.overlaps)
        print(json.dumps(merger.output, indent=4))
        self.assertTrue(merger.output == expected_output)

"""
class MergeGeneratorTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(MergeGeneratorTestCase, self).__init__(*args, **kwargs)

        with open('fullDiffOutput/network1.json', 'r') as networkFile:
            network1 = json.load(networkFile)
            networkFile.close()

        with open('fullDiffOutput/network2.json', 'r') as networkFile:
            network2 = json.load(networkFile)
            networkFile.close()

        self.prepared_input = [
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

    def test_test1(self):
        from semDiff.fullDiff import FullSemDiffMultiple

        overlaps = FullSemDiffMultiple(self.prepared_input)
        merging = {
            "network1": overlaps.networks[0],
            "network2": overlaps.networks[1],
            "overlaps": overlaps.output[0][0],
        }
        if len(overlaps.ready_for_merge) > 0:
            merging["fields_to_merge"] = overlaps.ready_for_merge[0]

        with open("fullDiffOutput/overlap_example.json", "w") as outputFile:
            outputFile.write(json.dumps(merging, indent=4))

        merge = MergeEntityFromDiff(merging)
        with open("fullDiffOutput/merges/example_merge.json", "w") as outputFile:
            outputFile.write(json.dumps(merge.output, indent=4))
"""
