
class Coverage:
    """
    A class that compute the overlap between two structures
    """

    jsonld_ignored_keys = ["@id", "@context", "@type"]

    @staticmethod
    def json_schema_context_coverage(schema, context):
        """  Static method to compute the coverage of a context file for a particular json-schema

        :param schema: the content of a JSON schema
        :param context: the content of a JSON-LD context associated with the schema
        :return: an array contain the overlap and the diff
        """
        overlap = []
        diff = []

        for field in schema["properties"]:
            if field not in Coverage.jsonld_ignored_keys:
                if field in context["@context"]:
                    overlap.append(field)
                else:
                    diff.append(field)
        return overlap, diff

    @staticmethod
    def json_schema_context_mapping(schema, *contexts):
        """ Static method to retrieve the mapping between a schema and multiple context files

        :param schema: the content of a JSON schema
        :param contexts: one or more JSON-LD context contexts associated with the schema
        :return: an mapping dictionary
        """
        mappings = {}

        for field in schema["properties"]:
            terms = []
            if field not in Coverage.jsonld_ignored_keys:
                for context in contexts:
                    if field in context["@context"]:
                        if "@id" in context["@context"][field]:
                            terms.append(context["@context"][field]["@id"])
                        else:
                            terms.append(context["@context"][field])
                    else:
                        terms.append("")
                if field in mappings:
                    previous_terms = mappings[field]
                    terms.append(previous_terms)
                mappings.update({field: terms})
        return mappings
