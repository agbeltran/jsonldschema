import copy
import json
import os
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

        for schemaName in overlaps['fields_to_merge']:
            merging_schema_name = schemaName.replace('_schema.json', '')
            merge_with_schema_name = overlaps['fields_to_merge'][schemaName][
                'merge_with'].replace('_schema.json', '')
            merged_schema_name = merge_with_schema_name + "_" \
                                                        + merging_schema_name \
                                                        + "_merged_schema.json"

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

            self.output['schemas'][merged_schema_name] = merged_schema
            self.output['contexts'][merged_schema_name] = merged_context

    def save(self, base_url):
        output_name = self.content['network1']['name'].lower() \
                      + "_" + self.content['network2']['name'].lower() \
                      + "_merge"
        output_dir = os.path.join(os.path.dirname(__file__),
                                  "../tests/fullDiffOutput/merges/" + output_name + "/")
        directory_system = [
            os.path.join(output_dir, 'schema'),
            os.path.join(output_dir, 'context')
        ]
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for directory in directory_system:
            if not os.path.exists(directory):
                os.makedirs(directory)

        for schemaName in self.output["schemas"]:
            schema = self.output["schemas"][schemaName]
            schema["id"] = base_url + "schema/" + schemaName
            schema_file_name = os.path.join(os.path.join(output_dir, 'schema/'), schemaName)
            context_name = schemaName.replace("_schema.json", '_context.jsonld')
            context_file_name = os.path.join(os.path.join(output_dir, 'context/'), context_name)

            with open(schema_file_name, "w") as schemaFile:
                schemaFile.write(json.dumps(schema, indent=4))
                schemaFile.close()

            if schemaName in self.output['contexts'].keys():
                with open(context_file_name, "w") as contextFile:
                    contextFile.write(json.dumps({
                        "@context": self.output['contexts'][schemaName]
                    }, indent=4))
                    contextFile.close()
