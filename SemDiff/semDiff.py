import copy
from urllib.parse import urlparse
from collections import namedtuple


class SemanticComparator:
    """
     A class that compute the overlap between two JSON schemas semantic values taken from context
     files. This operation is not commutative. Thus, to find out if the schema/context pairs are
     equivalent, we need to run both semDiff(s_a, c_a, s_b, c_b) and semDiff(s_b, c_b, s_a, c_a)
     :param schema_a: the content of the first schema
     :param context_a: the context content bound to the first schema
     :param schema_b: the content of the second schema
     :param context_b: the context content bound to the second schema
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
        """
        A private method that associate each field in a schema to it's semantic value in the
        context and reverse the result
        :param schema_input:
        :return sorted_values: a dictionary of semantic values and their corresponding field
        :return ignored_fields: a list of fields that were ignored due to having no semantic value
        in the context file
        """
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

                # if the field is absent from the context file, ignore it as it has no semantic
                # definition
                else:
                    ignored_fields.append(field)

        return sorted_values, ignored_fields

    @staticmethod
    def __process_field(field_name, field_value, context, comparator):
        """
        Private method that catches a given field semantic value from the given context and adds it
        to the output
        :param field_name: the name of the given field
        :param field_value: the value of the given field
        :param context: the context from which to retrieve the semantic value
        :param comparator: the output of __build_context_dict()
        :return comparator: a dictionary of semantic values and corresponding fields from the given
        schema and context
        """

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
        """
        Private method that compares the fields from the two schemas based on their semantic values
        :param context1: the final output of __build_context_dict() for the first schema
        :param context2: the final output of __build_context_dict() for the second schema
        :return local_overlap_value: a namedtuple containing relative and absolute coverage
        :return overlap_output: a dictionary that associate fields in schema 1 with their semantic
        twins in schema 2
        """

        Overlap = namedtuple('Overlap', ['first_field', 'second_field'])
        OverlapValue = namedtuple('OverlapValue', ['relative_coverage', 'absolute_coverage'])

        overlap_number = 0
        overlap_output = []
        processed_field = 0

        for field in context1:
            processed_field += 1
            if field in context2:
                overlap_number += len(context1[field])

                for first_field_val in context1[field]:
                    for second_field_val in context2[field]:
                        local_overlap = Overlap(first_field_val, second_field_val)
                        overlap_output.append(local_overlap)

        absolute_coverage = namedtuple('AbsoluteCoverage', ['overlap_number', 'total_fields'])
        AbsoluteCoverage = absolute_coverage(str(overlap_number), str(processed_field))
        local_overlap_value = OverlapValue(str(round((overlap_number * 100) / len(context1), 2)),
                                           AbsoluteCoverage)

        return local_overlap_value, overlap_output
