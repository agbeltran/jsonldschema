import copy
import json
import os
from jsonschema.validators import Draft4Validator
from semDiff.compareEntities import EntityCoverage


class EntityMerge:
    """
    A class that merge two schemas based on their semantic annotations
    """

    def __init__(self, schema1, context1, schema2, context2):
        """ Constructor

        :param schema1: dictionary of the first schema
        :param context1: dictionary of the first context as {"@context":{}}
        :param schema2: dictionary of the second schema
        :param context2: dictionary of the second context as {"@context":{}}
        """

        # Initiate output as a copy of the first schema and its context
        self.output_schema = copy.deepcopy(schema1)
        self.output_context = copy.deepcopy(context1)
        coverage = EntityCoverage(schema1, context1, schema2, context2)

        # for each unmatched field of the second schema that have a semantic value in the second
        # context
        for field_semantic_value in coverage.unmatched_with_sem.keys():

            # field are organized in an array
            for field_name in coverage.unmatched_with_sem[field_semantic_value]:
                self.output_context["@context"][field_name] = field_semantic_value
                self.output_schema['properties'][field_name] = schema2['properties'][field_name]

        # for each unmatched field that doesn't have a semantic value
        for field_name in coverage.unmatched_without_sem:

            # if that field isn't already in the first schema
            if field_name not in schema1["properties"]:
                self.output_schema["properties"][field_name] = schema2["properties"][field_name]


class MergeEntityFromDiff:
    """
    A class that merges network2 into network1 based on overlaps from FullDiff
    """

    def __init__(self, overlaps):
        self.overlaps = overlaps["overlaps"]
        self.output = {
            "schemas": copy.deepcopy(overlaps["network1"]['schemas']),
            "contexts": copy.deepcopy(overlaps["network1"]['contexts'])
        }
        self.content = overlaps
        self.name_mapping = {}  # {"oldName":"newName"}

        self.output_name = \
            self.content['network1']['name'].lower() + \
            "_" + self.content['network2']['name'].lower() + "_merge"
        self.output_dir = os.path.join(os.path.dirname(__file__),
                                       "../tests/fullDiffOutput/merges/" + self.output_name + "/")
        self.errors = {}

        for schemaName in overlaps['fields_to_merge']:
            merging_schema_name = schemaName.replace('_schema.json', '')
            merge_with_schema_name = overlaps['fields_to_merge'][schemaName][
                'merge_with'].replace('_schema.json', '')

            if merge_with_schema_name != merging_schema_name:
                merged_schema_name = merge_with_schema_name + "_" \
                                                            + merging_schema_name \
                                                            + "_merged_schema.json"
            else:
                merged_schema_name = merge_with_schema_name + "_merged_schema.json"

            self.name_mapping[overlaps['fields_to_merge'][schemaName][
                'merge_with']] = merged_schema_name
            self.name_mapping[schemaName] = merged_schema_name

            merged_title = overlaps["network1"]['schemas'][overlaps[
                'fields_to_merge'][schemaName]['merge_with']]['title'] + " - " + \
                overlaps["network2"]['schemas'][schemaName]['title'] + " merging"
            merged_description = "Merge between the " + overlaps["network1"]['schemas'][overlaps[
                'fields_to_merge'][schemaName]['merge_with']]['title'] + " and the " + \
                overlaps["network2"]['schemas'][schemaName]['title']

            merged_schema = copy.deepcopy(
                overlaps["network1"]['schemas'][
                    overlaps['fields_to_merge'][schemaName]['merge_with']])
            merged_context = copy.deepcopy(
                overlaps["network1"]['contexts'][overlaps[
                    'fields_to_merge'][schemaName]['merge_with']])

            del self.output['schemas'][overlaps['fields_to_merge'][schemaName]['merge_with']]
            del self.output['contexts'][overlaps['fields_to_merge'][schemaName]['merge_with']]

            # process the fields to merge
            for field in overlaps['fields_to_merge'][schemaName]['fields']:
                merged_schema['properties'][field] = overlaps['network2'][
                    'schemas'][schemaName]['properties'][field]

                merged_schema['title'] = merged_title
                merged_schema['description'] = merged_description
                merged_context[field] = overlaps['network2']['contexts'][schemaName][field]

                self.find_references(
                    overlaps['network2']['schemas'][schemaName]['properties'][field])

            self.output['schemas'][merged_schema_name] = merged_schema
            self.output['contexts'][merged_schema_name] = merged_context

        self.modify_references()

    def find_references(self, schema):
        """
        Find $ref at root, in items or in allOf, anyOf, oneOf, adds the schema/context
        to the merge and change reference names

        :param schema: ??
        :type schema: dict
        :return:
        """
        look_for = ["anyOf", "oneOf", "allOf"]

        # $ref at root
        if '$ref' in schema:
            sub_schema_name = schema['$ref'].replace("#", '')
            self.add_schema(sub_schema_name)

        # $ref in anyOf, oneOf or allOf
        for item in look_for:
            if item in schema:
                for sub_item in schema[item]:
                    if '$ref' in sub_item:
                        sub_schema_name = sub_item['$ref'].replace("#", '')
                        self.add_schema(sub_schema_name)

        # $ref in items
        if 'items' in schema:
            if '$ref' in schema['items']:
                sub_schema_name = schema['items']['$ref'].replace('#', '')
                self.add_schema(sub_schema_name)

            for item in look_for:
                if item in schema['items']:
                    for sub_item in schema['items'][item]:
                        if '$ref' in sub_item:
                            sub_schema_name = sub_item['$ref']
                            self.add_schema(sub_schema_name)

    def add_schema(self, schema_name):
        """
        Adds the schema/context to the merge
        :param schema_name:
        :return:
        """
        if schema_name in self.name_mapping:
            schema_name = self.name_mapping[schema_name]

        else:
            if schema_name is not None and schema_name not in self.output['schemas']:
                self.output['schemas'][schema_name] = \
                    self.content['network2']['schemas'][schema_name]
                if schema_name in self.content['network2']['contexts']:
                    self.output['contexts'][schema_name] = \
                        self.content['network2']['contexts'][schema_name]
                self.find_references(self.content['network2']['schemas'][schema_name])

    def modify_references(self):
        look_for = ["anyOf", "oneOf", "allOf"]
        delete_schemas = []

        for schema in self.output['schemas']:

            if schema in self.name_mapping:
                delete_schemas.append(schema)

            else:
                if 'properties' in self.output['schemas'][schema]:
                    for item in self.output['schemas'][schema]['properties']:
                        field = self.output['schemas'][schema]['properties'][item]

                        if '$ref' in field:
                            field_ref = field['$ref'].replace('#', '')
                            if field_ref in self.name_mapping:
                                self.output['schemas'][schema]['properties'][item]['$ref'] = \
                                    self.name_mapping[field_ref] + '#'

                        for reference in look_for:
                            if reference in field:
                                sub_item_iterator = 0
                                for sub_item in field[reference]:
                                    if '$ref' in sub_item:
                                        field_ref = sub_item['$ref']
                                        if field_ref in self.name_mapping:
                                            self.output['schemas'][schema]['properties'][
                                                reference][sub_item_iterator]['$ref'] = \
                                                self.name_mapping[field_ref] + "#"
                                    sub_item_iterator += 1

                        if 'items' in field:

                            if '$ref' in field['items']:
                                field_ref = field['items']['$ref'].replace('#', '')
                                if field_ref in self.name_mapping:
                                    self.output['schemas'][
                                        schema]['properties'][item]['items']['$ref'] = \
                                        self.name_mapping[field_ref] + '#'

                            for reference in look_for:
                                if reference in field['items']:
                                    sub_item_iterator = 0
                                    for sub_item in field['items'][reference]:
                                        if '$ref' in sub_item:
                                            field_ref = sub_item['$ref']
                                            if field_ref in self.name_mapping:
                                                self.output['schemas'][schema]['properties'][
                                                    reference]['items'][
                                                    sub_item_iterator]['$ref'] = \
                                                    self.name_mapping[field_ref] + "#"
                                        sub_item_iterator += 1

        for schema in delete_schemas:
            del self.output['schemas'][schema]

    def save(self, base_url):
        directory_system = [
            os.path.join(self.output_dir, 'schema'),
            os.path.join(self.output_dir, 'context')
        ]
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        for directory in directory_system:
            if not os.path.exists(directory):
                os.makedirs(directory)

        for schemaName in self.output["schemas"]:
            schema = self.output["schemas"][schemaName]
            schema["id"] = base_url + "schema/" + schemaName
            schema_file_name = os.path.join(os.path.join(self.output_dir, 'schema/'), schemaName)
            context_name = schemaName.replace("_schema.json", '_context.jsonld')
            context_file_name = \
                os.path.join(os.path.join(self.output_dir, 'context/'), context_name)

            with open(schema_file_name, "w") as schemaFile:
                schemaFile.write(json.dumps(schema, indent=4))
                schemaFile.close()

            if schemaName in self.output['contexts'].keys():
                with open(context_file_name, "w") as contextFile:
                    contextFile.write(json.dumps({
                        "@context": self.output['contexts'][schemaName]
                    }, indent=4))
                    contextFile.close()

    def validate_output(self):

        for schema in self.output['schemas']:
            try:
                Draft4Validator.check_schema(self.output['schemas'][schema])
            except Exception as e:
                if schema not in self.errors:
                    self.errors[schema] = []
                self.errors[schema].append(str(e))
