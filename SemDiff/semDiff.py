import pprint
import copy
from urllib.parse import urlparse
from collections import namedtuple

prettyPrint = pprint.PrettyPrinter(indent=2)

personA = {
  "id": "https://w3id.org/dats/schema/person_schema.json",
  "$schema": "http://json-schema.org/draft-04/schema",
  "title": "DATS person schema",
  "description": "A human being",
  "type": "object",
  "properties": {
    "@context": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "object"
        }
      ]
    },
    "@id": {"type": "string", "format": "uri"},
    "@type": {"type": "string", "format": "uri"},
    "identifier": {
      "description": "Primary identifier for the person.",
      "$ref": "identifier_info_schema.json#"
    },
    "lastName": {
      "description": "The person's family name.",
      "type":  "string"
    }
  },
  "additionalProperties": False
}

personB = {
  "id": "https://w3id.org/dats/schema/person_schema.json",
  "$schema": "http://json-schema.org/draft-04/schema",
  "title": "DATS person schema",
  "description": "A human being",
  "type": "object",
  "properties": {
    "@context": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "object"
        }
      ]
    },
    "@id": {"type": "string", "format": "uri"},
    "@type": {"type": "string", "format": "uri"},
    "identifier": {
      "description": "Primary identifier for the person.",
      "$ref": "identifier_info_schema.json#"
    },
    "familyName": {
      "description": "The person's family name.",
      "type":  "string"
    }
  },
  "additionalProperties": False
}

personC = {
  "id": "https://w3id.org/dats/schema/person_schema.json",
  "$schema": "http://json-schema.org/draft-04/schema",
  "title": "DATS person schema",
  "description": "A human being",
  "type": "object",
  "properties": {
    "@context": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "object"
        }
      ]
    },
    "@id": { "type": "string", "format": "uri" },
    "@type": { "type": "string", "enum": [ "Person" ]},
    "identifier": {
      "description": "Primary identifier for the person.",
      "$ref": "identifier_info_schema.json#"
    },
    "alternateIdentifiers": {
      "description": "Alternate identifiers for the person.",
      "type": "array",
      "items": {
        "$ref": "alternate_identifier_info_schema.json#"
      }
    },
    "relatedIdentifiers": {
      "description": "Related identifiers for the person.",
      "type": "array",
      "items": {
        "$ref": "related_identifier_info_schema.json#"
      }
    },

    "fullName": {
      "description": "The first name, any middle names, and surname of a person.",
      "type" :  "string"
    },
    "firstName": {
      "description": "The given name of the person.",
      "type" :  "string"
    },
    "middleInitial": {
      "description": "The first letter of the person's middle name.",
      "type" :  "string"
    },
    "lastName": {
      "description": "The person's family name.",
      "type" :  "string"
    },
    "email": {
      "description": "An electronic mail address for the person.",
      "type" :  "string",
      "format": "email"
    },
    "affiliations" : {
      "description": "The organizations to which the person is associated with.",
      "type" : "array",
      "items" : {
        "$ref" : "organization_schema.json#"
      }
    },
    "roles" : {
      "description": "The roles assumed by a person, ideally from a controlled vocabulary/ontology.",
      "type" : "array",
      "items" : {
        "$ref" : "annotation_schema.json#"
      }
    },
    "extraProperties": {
      "description": "Extra properties that do not fit in the previous specified attributes. ",
      "type": "array",
      "items": {
        "$ref" : "category_values_pair_schema.json#"
      }
    }
  },
  "additionalProperties": False
}

personA_context = {
    "@context": {
        "sdo": "https://schema.org/",
        "Person": "sdo:Person",
        "identifier": {
            "@id": "sdo:identifier",
            "@type": "sdo:Text"
        },
        "firstName": "sdo:givenName",
        "lastName": "sdo:familyName",
        "fullName": "sdo:name",
        "email": "sdo:email",
        "affiliations": "sdo:affiliation",
        "roles": "sdo:roleName"
    }
}

personB_context = {
    "@context": {
        "sdo": "https://schema.org/",
        "Person": "sdo:Person",
        "identifier": {
            "@id": "sdo:identifier",
            "@type": "sdo:Text"
        },
        "firstName": "sdo:givenName",
        "familyName": "sdo:familyName",
        "fullName": "sdo:name",
        "email": "sdo:email",
        "affiliations": "sdo:affiliation",
        "roles": "sdo:roleName"
    }
}

schemasInput = {
    "schema1": {
        "schema": personC,
        "contexts": personA_context
    },
    "schema2": {
        "schema": personB,
        "contexts": personB_context
    }
}


def build_context_dict(schema_input):

    sorted_values = {}
    ignored_keys = ["@id", "@context", "@type"]
    schema = copy.deepcopy(schema_input)
    ignored_fields = []

    # for each field in the schema
    for field in schema['schema']['properties']:

        # Ignoring useless keys
        if field not in ignored_keys:

            # If the field can be found in the context, process it
            if field in schema["contexts"]["@context"].keys():

                # This is the raw semantic value of the field, it might need some processing
                raw_semantic_value = schema["contexts"]["@context"][field]

                # If the field raw semantic value is a string
                if isinstance(raw_semantic_value, str):
                    sorted_values = process_field(field,
                                                  raw_semantic_value,
                                                  schema["contexts"]["@context"],
                                                  sorted_values)

                # if the field raw semantic value is not a string
                else:
                    sorted_values = process_field(field,
                                                  raw_semantic_value['@id'],
                                                  schema["contexts"]["@context"],
                                                  sorted_values)

            # if the field is absent from the context file, ignore it as it has no semantic definition
            else:
                ignored_fields.append(field)

    return sorted_values, ignored_fields


def process_field(field_name, field_value, context, comparator):

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


def compute_context_coverage(context1, context2):

    Overlap = namedtuple('FieldOverlap', ['field_from_first_parent', 'field_from_second_parent'])

    overlap_number = 0
    overlap_output = []
    for field in context1:
        if field in context2:
            overlap_number += len(context1[field])

            for first_field_val in context1[field]:
                for second_field_val in context2[field]:
                    local_overlap = Overlap(first_field_val, second_field_val)
                    overlap_output.append(local_overlap)

    overlap_value = [str(round((overlap_number * 100) / len(context1), 2)), overlap_number]

    return overlap_value, overlap_output


def compute_coverage():
    comparator = build_context_dict(schemasInput["schema1"])[0]
    comparator2 = build_context_dict(schemasInput["schema2"])[0]

    coverage = compute_context_coverage(comparator, comparator2)
    print("----- \nCoverage: " + coverage[0][0] + "%")
    print("----- \nOverlapping fields:")
    print(coverage[1])
    print("----- \nIgnored fields:")
    print(build_context_dict(schemasInput["schema1"])[1])

    return coverage, build_context_dict(schemasInput["schema1"])[1]


if __name__ == "__main__":
    output = compute_coverage()
