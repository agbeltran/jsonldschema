import copy
from urllib.parse import urlparse
from collections import namedtuple


class SemanticComparator:
    """
     A class that compute the overlap between two JSON schemas semantic values taken from context files
    """

    def __init__(self, schema_a, context_a, schema_b, context_b):
        self.input1 = {
            "schema": schema_a,
            "context": context_a
        }
        self.input2 = {
            "schema": schema_b,
            "context": context_b
        }

        self.comparator1 = self.__build_context_dict(self.input1)
        self.comparator2 = self.__build_context_dict(self.input2)
        self.overlaps = self.__compute_context_coverage(self.comparator1[0], self.comparator2[0])

        self.full_coverage = {
            "coverage": self.overlaps[0],
            "overlapping fields": self.overlaps[1],
            "ignored fields": self.comparator1[1]
        }

    def __build_context_dict(self, schema_input):
        sorted_values = {}
        ignored_keys = ["@id", "@context", "@type"]
        schema = copy.deepcopy(schema_input)
        ignored_fields = []

        # for each field in the schema
        for field in schema['schema']['properties']:

            # Ignoring useless keys
            if field not in ignored_keys:

                # If the field can be found in the context, process it
                if field in schema["context"]["@context"].keys():

                    # This is the raw semantic value of the field, it might need some processing
                    raw_semantic_value = schema["context"]["@context"][field]

                    # If the field raw semantic value is a string
                    if isinstance(raw_semantic_value, str):
                        sorted_values = self.__process_field(field,
                                                             raw_semantic_value,
                                                             schema["context"]["@context"],
                                                             sorted_values)

                    # if the field raw semantic value is not a string
                    else:
                        sorted_values = self.__process_field(field,
                                                             raw_semantic_value['@id'],
                                                             schema["context"]["@context"],
                                                             sorted_values)

                # if the field is absent from the context file, ignore it as it has no semantic definition
                else:
                    ignored_fields.append(field)

        return sorted_values, ignored_fields

    @staticmethod
    def __process_field(field_name, field_value, context, comparator):

        base_url = urlparse(field_value).scheme

        # if the raw value is already an URL, it does not need processing
        if base_url in ('http', 'https'):
            if field_value not in comparator:
                comparator[field_value] = [field_name]
            else:
                comparator[field_value].append(field_name)

        # replacing semantic base to form an absolute IRI
        else:
            processed_semantic_value = field_value.replace(base_url + ":", context[base_url])
            if processed_semantic_value not in comparator:
                comparator[processed_semantic_value] = [field_name]
            else:
                comparator[processed_semantic_value].append(field_name)

        return comparator

    @staticmethod
    def __compute_context_coverage(context1, context2):

        Overlap = namedtuple('Overlap', ['first_field', 'second_field'])
        OverlapValue = namedtuple('OverlapValue', ['relative_coverage', 'absolute_coverage'])

        overlap_number = 0
        overlap_output = []
        processed_field = 0

        for field in context1:
            processed_field+=1
            if field in context2:
                overlap_number += len(context1[field])

                for first_field_val in context1[field]:
                    for second_field_val in context2[field]:
                        local_overlap = Overlap(first_field_val, second_field_val)
                        overlap_output.append(local_overlap)

        absolute_coverage = namedtuple('AbsoluteCoverage', ['overlap_number', 'total_fields'])
        AbsoluteCoverage = absolute_coverage(str(overlap_number), str(processed_field))
        local_overlap_value = OverlapValue(str(round((overlap_number * 100) / len(context1), 2)), AbsoluteCoverage)

        return local_overlap_value, overlap_output
