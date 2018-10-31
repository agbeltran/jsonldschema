import unittest
from utils import compile_schema
import json
from collections import OrderedDict
from deepdiff import DeepDiff


class CompileSchemaTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CompileSchemaTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.schema_URL = "https://w3id.org/dats/schema/study_schema.json#"

    def test_resolve_reference(self):
        expected_output = {
            'additionalProperties': False,
            '$schema': 'http://json-schema.org/draft-04/schema',
            'type': 'object',
            'description': 'Process to acquire data on a sample and attempt to draw conclusions about the population the sample has been selected from, executing a plan and design.',
            'title': 'DATS study schema',
            'required': ['name'],
            'properties': {
                'name': {'type': 'string', 'description': 'The name of the activity, usually one sentece or short description of the study.'},
                'usesReagent': {'type': 'array', 'description': 'The materials that are used as reagents (but not subjects) of the study.', 'items': {'$ref': 'material_schema.json#'}},
                '@context': {'anyOf': [{'type': 'string'}, {'type': 'object'}, {'type': 'array'}], 'description': 'The JSON-LD context'},
                'alternateIdentifiers': {'type': 'array', 'description': 'Alternate identifiers for the activity.', 'items': {'$ref': 'alternate_identifier_info_schema.json#'}},
                'output': {'type': 'array', 'description': 'The entities resulting from applying the activity.', 'items': {'anyOf': [{'$ref': 'dataset_schema.json#'}, {'$ref': 'material_schema.json#'}]}},
                'duration': {'type': 'string', 'description': 'The time during which the activity takes place.'}, '@type': {'type': 'string', 'enum': ['Study'], 'description': 'The JSON-LD type'}, '@id': {'type': 'string', 'format': 'uri', 'description': 'The JSON-LD identifier'},
                'input': {'type': 'array', 'description': 'The entities used as input.', 'items': {'anyOf': [{'$ref': 'dataset_schema.json#'}, {'$ref': 'material_schema.json#'}]}},
                'description': {'type': 'string', 'description': 'A textual narrative comprised of one or more statements describing the study.'},
                'isAboutBiologicalEntity': {'type': 'array', 'description': 'The biological entities relevant to the study, ideally from a controlled vocabulary/ontology such as Gene Ontology.', 'items': {'$ref': 'biological_entity_schema.json#'}},
                'schedulesDataAcquisition': {'type': 'array', 'minItems': 1, 'description': 'The kind of techniques and response variables used during a study for acquiring data.', 'items': {'$ref': 'data_acquisition_schema.json#'}},
                'studyGroups': {'type': 'array', 'description': 'The different study groups associated with a study.', 'items': {'$ref': 'study_group_schema.json#'}},
                'endDate': {'$ref': 'date_info_schema.json#', 'description': 'A timestamp to record the end point of the activity.'}, 'types': {'type': 'array', 'description': 'The types of study (e.g. intervention or observation or meta-analysis or clinical trials, or behavioural study, or the study design).', 'items': {'$ref': 'annotation_schema.json#'}},
                'identifier': {'$ref': 'identifier_info_schema.json#'},
                'location': {'$ref': 'place_schema.json#', 'description': 'The location where the activity takes place.'},
                'dates': {'type': 'array', 'description': 'Relevant dates for the datasets, a date must be added, e.g. creation date or last modification date should be added.', 'items': {'$ref': 'date_info_schema.json#'}},
                'relatedIdentifiers': {'type': 'array', 'description': 'Related identifiers for the activity.', 'items': {'$ref': 'related_identifier_info_schema.json#'}},
                'performedBy': {'type': 'array', 'description': 'The person(s) or organisation(s) responsible for executing the process.', 'items': {'anyOf': [{'$ref': 'person_schema.json#'}, {'$ref': 'organization_schema.json#'}]}},
                'extraProperties': {'type': 'array', 'description': 'Extra properties that do not fit in the previous specified attributes. ', 'items': {'$ref': 'category_values_pair_schema.json#'}},
                'keywords': {'type': 'array', 'description': 'Tags associated with the activity, which will help in its discovery.', 'items': {'$ref': 'annotation_schema.json#'}},
                'selectionCriteria': {'type': 'array', 'description': 'The attributes and values that the material should meet in order to be part of the group.', 'items': {'anyOf': [{'$ref': 'annotation_schema.json#'}, {'$ref': 'category_values_pair_schema.json#'}]}},
                'schedulesActivity': {'type': 'array', 'description': 'The activities scheduled by the study.', 'items': {'anyOf': [{'$ref': 'activity_schema.json#'}, {'$ref': 'data_acquisition_schema.json#'}, {'$ref': 'data_analysis_schema.json#'}]}},
                'startDate': {'$ref': 'date_info_schema.json#', 'description': 'A timestamp to record the starting point of the activity.'}
            },
            'id': 'https://w3id.org/dats/schema/study_schema.json'}

        ref_resolved = compile_schema.resolve_reference(self.schema_URL)
        self.assertTrue(ref_resolved == expected_output)

        ref_2_resolved = compile_schema.resolve_reference("fakeURL")
        self.assertTrue(isinstance(ref_2_resolved, type))
        # TODO: test for exception, not type

    def test_get_name(self):
        expected_output = "study_schema.json"
        schema_name = compile_schema.get_name(self.schema_URL)
        self.assertTrue(schema_name == expected_output)

    def test_resolve_schema_references(self):

        expected_output = json.load(open('data/compile_test.json'))

        processed_schemas = {}
        schema_url = 'https://w3id.org/dats/schema/person_schema.json#'
        processed_schemas[compile_schema.get_name(schema_url)] = '#'
        data = compile_schema.resolve_schema_references(compile_schema.resolve_reference(schema_url),
                                                        processed_schemas,
                                                        schema_url)

        output_value = json.loads(json.dumps(data))
        output_expected = json.loads(json.dumps(expected_output))
        self.assertTrue(DeepDiff(output_value, output_expected) == {})
