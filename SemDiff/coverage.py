
class Coverage:
    """
    A class that compute the overlap between two structures
    """

    jsonld_ignored_keys = ["@id", "@context", "@type"]

    @staticmethod
    def json_schema_context_coverage(schema, context):
        "Method to compute the coverage of a context file for a particular json-schema"

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
        "Method to retrieve the mapping between a schema and multiple context files"
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
