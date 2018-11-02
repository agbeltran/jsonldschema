from semDiff import compareNetwork, compareEntities
from collections import namedtuple


class FullSemDiff:
    """
    A class that computes the coverage at entity level and extracts 'semantic synonyms'
    (named twins in the code). It will then compute the coverage at attribute level
    between 'semantic synonyms'.
    """

    def __init__(self, contexts, network_1, network_2):
        """ The class constructor

        :param contexts: an array containing the two context networks to use
        :param network_1: a dictionary containing the first set of schemas
        :param network_2: a dictionary containing the second set of schemas
        """

        self.total_entities = 0
        self.half_twins = 0
        self.twins = []

        twin_tuple = namedtuple('Twins', ['first_entity', 'second_entity'])
        twin_coverage = namedtuple('TwinCoverage', ['twins', 'overlap'])

        # Compute the comparison of entities based on their semantic type
        entity_coverage = compareNetwork.NetworkCoverage(contexts)

        # for each mapped entity
        for entity_name in entity_coverage.covered_entities:
            self.total_entities += 1
            twins = entity_coverage.covered_entities[entity_name]

            # if the entity has twins
            if twins is not None:
                entity_schema = network_1[entity_name.lower() + "_schema.json"]
                entity_context = {"@context": contexts[0][entity_name.lower() + "_schema.json"]}

                # For each twin
                for twin in twins:
                    self.half_twins += 1
                    twin_schema = network_2[twin.lower() + "_schema.json"]
                    twin_context = {"@context": contexts[1][twin.lower() + "_schema.json"]}
                    local_twin = twin_tuple(entity_name, twin)

                    # compare the entities
                    attribute_diff = compareEntities.EntityCoverage(entity_schema, entity_context,
                                                                    twin_schema, twin_context)
                    # create the tuple
                    attribute_coverage = twin_coverage(local_twin,
                                                       attribute_diff.full_coverage)

                    # adds it to output
                    self.twins.append(attribute_coverage)
