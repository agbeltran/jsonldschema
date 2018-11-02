import copy
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
