import os
from collections import namedtuple
from copy import deepcopy
import json
import webbrowser
from semDiff import compareNetwork, compareEntities
from json2html import json2html


class FullSemDiff:
    """
    A class that computes the coverage at entity level and extracts 'semantic synonyms'
    (named twins in the code) between two network. It will then compute the coverage at
    attribute level between 'semantic synonyms'.
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
            if twins is not None and entity_name.lower() + "_schema.json" in network_1.keys():
                entity_schema = network_1[entity_name.lower() + "_schema.json"]
                entity_context = {"@context": contexts[0][entity_name.lower() + "_schema.json"]}

                # For each twin
                for twin in twins:
                    if twin.lower() + "_schema.json" in network_2.keys():
                        self.half_twins += 1
                        twin_schema = network_2[twin.lower() + "_schema.json"]
                        twin_context = {"@context": contexts[1][twin.lower() + "_schema.json"]}
                        local_twin = twin_tuple(entity_name, twin)

                        # compare the entities
                        attribute_diff = compareEntities.EntityCoverage(entity_schema,
                                                                        entity_context,
                                                                        twin_schema,
                                                                        twin_context)
                        # create the tuple
                        attribute_coverage = twin_coverage(local_twin,
                                                           attribute_diff.full_coverage)

                        # adds it to output
                        self.twins.append(attribute_coverage)


class FullSemDiffMultiple:
    """
    A class that computes the coverage at entity level and extracts
    'semantic synonyms' (named twins in the code) between multiple
    networks. It will then compute the coverage at attribute level between 'semantic synonyms'.
    """

    def __init__(self, networks):

        self.networks = deepcopy(networks)
        self.contexts = []
        self.output = []

        for network in self.networks:
            self.contexts.append(network["contexts"])

        self.compute_overlap()

    def compute_overlap(self, start_position=0):
        local_overlap = []
        for i in range(start_position + 1, len(self.networks)):
            contexts = [self.networks[start_position]["contexts"], self.networks[i]["contexts"]]
            coverage = FullSemDiff(contexts,
                                   self.networks[start_position]["schemas"],
                                   self.networks[i]["schemas"])
            local_overlap.append(coverage.twins)

        if len(local_overlap) > 0:
            self.output.append(local_overlap)

        if start_position < len(self.networks):
            self.compute_overlap(start_position + 1)


class HTMLGenerator:

    def __init__(self, diff):
        """ Output overlaps as an HTML file
        :param diff: a FullSemDiffMultiple object
        :type diff: FullSemDiffMultiple
        """

        self.output_dir = os.path.join(os.path.dirname(__file__), "html")
        self.diff = diff
        self.htmlCode = "<HTML>"
        for overlap in self.diff.output:
            self.htmlCode += json2html.convert(json=overlap)
            self.htmlCode += "<HR>"
        self.htmlCode += "</HTML>"

    def generate_html(self):
        file_name = os.path.join(self.output_dir, "test.html")
        with open(file_name, "w") as html_file:
            html_file.write(self.htmlCode)
            html_file.close()
        webbrowser.get('firefox').open_new_tab(file_name)

    def convert_to_html(self):
        for overlap in self.diff.output:
            print(overlap)


if __name__ == '__main__':
    with open("../tests/data/fullDiff_input_example.json") as input_file:
        data = json.load(input_file)
        input_file.close()

    report = HTMLGenerator(FullSemDiffMultiple(data['networks']))
    report.generate_html()
    report.convert_to_html()
