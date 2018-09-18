import copy
from semDiff.compareEntities import EntityCoverage


class EntityMerge:
    """
    A class that merge two schemas based on their semantic annotations
    """

    def __init__(self, schema1, context1, schema2, context2):
        """
        Constructor
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




        """
        # Iterate over the second schema
        for field in schema2["properties"]:

            # Ignore some specific keys
            if field not in ignored_keys:

                # if the field is already in schema1 - syntactic equivalence
                #if field in schema1["properties"]:

                    # if this field has a semantic value for both schemas - semantic equivalence
                    #if (field in context2['@context'].keys() and
                    #        field in context1['@context'].keys()):

                        #if those semantic values are different
                        #if context1["@context"][field] != context2["@context"][field]:
                        #    pass
                        # else they are the same, schema1 has priority, so do nothing !

                    # if this field only has a semantic value for schema2
                    #if (field in context2['@context'].keys() and
                    #        field not in context1['@context'].keys()):
                    #    print("Process ??")

                # the field name is not in schema1
                #else:

                    # if the field has a semantic value in the second context
                    if field in context2["@context"].keys():
                        field_semantic_twin = False

                        for sem_field in context1["@context"]:

                            # there's already a field in the first context with the same semantic
                            # value
                            if context1["@context"][sem_field] == context2["@context"][field]:
                                print("PROCESS?")
                                ### make sure that the merged schema/context include this field
                                field_semantic_twin = True

                        # there is no field in the first context with the same semantic value
                        if field_semantic_twin is not True:
                            self.output_context = context2["@context"][field]
                            self.output_schema["properties"][field] = schema2["properties"][
                                field]

                    # the field doesn't have a semantic value in the second context
                    self.output_schema["properties"][field] = schema2["properties"][field]
        """
