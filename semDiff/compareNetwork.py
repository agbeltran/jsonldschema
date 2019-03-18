from urllib.parse import urlparse
import copy


class NetworkCoverage:
    """  This class compute the coverage of entities (schemas) among two networks (set of schemas) by
    comparing the semantic base type of each schema.

    :param networks_array: an array containing the two networks to compare
    """

    def __init__(self, networks_array):
        network1 = self.__process_network(networks_array[0])
        network2 = self.__process_network(networks_array[1])
        coverage = self.__compute_coverage(network1, network2)
        self.covered_entities = coverage[0]
        self.total_entities = coverage[1]
        self.matched_entities = coverage[2]

    @staticmethod
    def __process_network(network):
        """ Private method that retrieve the base type of each entity in a given network
        for later comparison

        :param network: a dictionary of schemas and their context (the network itself)
        :return network_output: a dictionary of schemas and their base type retrieved from the
            context
        """
        network_output = {}
        for schema in network:
            schema_name = copy.deepcopy(schema).replace("_schema.json", "").capitalize()
            schema_name_in_context = copy.deepcopy(schema_name)

            if "_" in schema_name:
                schema_name_in_context = schema_name_in_context.replace("_", " ")\
                    .title().replace(" ", "")

            schema_type = None
            schema_context = network[schema]

            if schema_name_in_context in schema_context.keys():
                schema_type = schema_context[schema_name_in_context]

            schema_type_base_url = urlparse(schema_type).scheme
            if schema_type is not None and schema_type_base_url not in ('http', 'https'):
                if schema_type_base_url in schema_context.keys():
                    schema_type.replace(schema_type_base_url, schema_context[schema_type_base_url])

            network_output[schema_name] = schema_type

        return network_output

    @staticmethod
    def __compute_coverage(network_a, network_b):
        """ Private method that compute the coverage between two networks

        :param network_a: the output of __process_network for the first network
        :param network_b: the output of __process_network for the second network
        :return output: an array containing the twined entities, the number of processed entities
            and the number of twins between both networks
        """
        coverage = {}
        total_items = 0
        matched_items = 0

        network__b = copy.deepcopy(network_b)

        for schema in network_a:
            total_items += 1
            context_type = network_a[schema]
            matched = False

            subtype = "true"
            if context_type is not None \
                    and ":" in context_type \
                    and urlparse(context_type).scheme not in ["http", "https"]:
                subtype = context_type.split(":")[1]

            if context_type is not None:

                for schema2 in list(network__b.keys()):
                    context_type2 = network_b[schema2]

                    if context_type == context_type2 and subtype != "":
                        matched = True
                        del network__b[schema2]
                        if schema in coverage.keys():
                            coverage[schema].append(schema2)
                        else:
                            coverage[schema] = [schema2]

            if matched is False:
                coverage[schema] = None
            else:
                matched_items += 1

        output = [coverage, total_items, matched_items]
        return output
