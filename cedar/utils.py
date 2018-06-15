from urllib.parse import quote


def set_context():

    return {
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "pav": "http://purl.org/pav/",
        "oslc": "http://open-services.net/ns/core#",
        "schema": "http://schema.org/",
        "bibo": "http://purl.org/ontology/bibo/",
        "schema:name": {
            "@type": "xsd:string"
        },
        "schema:description": {
            "@type": "xsd:string"
        },
        "pav:createdOn": {
            "@type": "xsd:dateTime"
        },
        "pav:createdBy": {
            "@type": "@id"
        },
        "pav:lastUpdatedOn": {
            "@type": "xsd:dateTime"
        },
        "oslc:modifiedBy": {
            "@type": "@id"
        }
    }


def set_properties_base_item():
    base_items = {
        "@type": {
            "oneOf": [
                {
                    "format": "uri",
                    "type": "string"
                },
                {
                    "uniqueItems": True,
                    "type": "array",
                    "items": {
                        "format": "uri",
                        "type": "string"
                    },
                    "minItems": 1
                }
            ]
        },
        "@id": {
            "format": "uri",
            "type": "string"
        },
        "pav:createdOn": {
            "format": "date-time",
            "type": [
                "string",
                "null"
            ]
        },
        "schema:isBasedOn": {
            "format": "uri",
            "type": "string"
        },
        "schema:name": {
            "minLength": 1,
            "type": "string"
        },
        "oslc:modifiedBy": {
            "format": "uri",
            "type": [
                "string",
                "null"
            ]
        },
        "pav:lastUpdatedOn": {
            "format": "date-time",
            "type": [
                "string",
                "null"
            ]
        },
        "pav:createdBy": {
            "format": "uri",
            "type": [
                "string",
                "null"
            ]
        },
        "schema:description": {
            "type": "string"
        }
    }

    return base_items


def set_prop_context(schema):

    prop_context = {
        "pav:createdOn":{
            "properties": {
                "@type": {
                    "enum": ["xsd:dateTime"],
                    "type": "string"
                }
            },
            "type": "object"
        },
        "pav:lastUpdatedOn":{
            'properties': {
                "@type": {
                    "enum": ["xsd:dateTime"],
                    "type": "string"
                }
            },
            "type": "object"
        },
        "pav:createdBy": {
            "properties": {
                "@type": {
                    "enum": ["@id"],
                    "type": "string"
                }
            },
            "type": "object"
        },
        "schema:isBasedOn": {
            "properties": {
                "@type": {
                    "enum": ["@id"],
                    "type": "string"
                }
            },
            "type": "object"
        },
        "schema:name": {
            "properties": {
                "@type": {
                    "enum": ["xsd:string"],
                    "type": "string"
                }
            },
            "type": "object"
        },
        "schema:description": {
            "properties": {
                "@type": {
                    "enum": ["xsd:string"],
                    "type": "string"
                }
            },
            "type": "object"
        },
        "rdfs:label": {
            "properties": {
                "@type": {
                    "enum": ["xsd:string"],
                    "type": "string"
                }
            },
            "type": "object"
        },
        "oslc:modifiedBy": {
            "properties": {
                "@type": {
                    "enum": ["@id"],
                    "type": "string"
                }
            },
            "type": "object"
        },
        "oslc": {
            "enum": ["http://open-services.net/ns/core#"],
            "type": "string",
            "format": "uri"
        },
        "schema": {
            "enum": ["http://schema.org/"],
            "type": "string",
            "format": "uri"
        },
        "rdfs": {
            "enum": ["http://www.w3.org/2000/01/rdf-schema#"],
            "type": "string",
            "format": "uri"
        },
        "pav": {
            "enum": ["http://purl.org/pav/"],
            "type": "string",
            "format": "uri"
        },
        "xsd": {
            "enum": ["http://www.w3.org/2001/XMLSchema#"],
            "type": "string",
            "format": "uri"
        }
    }

    ignored_key = ["@id", "@type", "@context"]
    for item in schema['properties']:
        if item not in ignored_key:
            prop_context[item] = {
                "enum": [""]
            }

    return prop_context


def set_required_item(schema):
    ignored_key = ["@id", "@type", "@context"]
    properties = {}

    for propertyKey in schema['properties']:
        if propertyKey not in ignored_key:
            if "description" in schema['properties'][propertyKey]:
                description = schema['properties'][propertyKey]['description']
            else:
                description = propertyKey

            if propertyKey in schema['required']:
                required = True
            else:
                required = False

            properties[propertyKey] = {
                "$schema": "http://json-schema.org/draft-04/schema#",
                "@id": "",
                "@type": "https://schema.metadatacenter.org/core/TemplateField",
                "@context": {
                    "xsd": "http://www.w3.org/2001/XMLSchema#",
                    "pav": "http://purl.org/pav/",
                    "oslc": "http://open-services.net/ns/core#",
                    "schema": "http://schema.org/",
                    "schema:name": {"@type": "xsd:string"},
                    "schema:description": {"@type": "xsd:string"},
                    "pav:createdOn": {"@type": "xsd:dateTime"},
                    "pav:createdBy": {"@type": "@id"},
                    "pav:lastUpdatedOn": {"@type": "xsd:dateTime"},
                    "oslc:modifiedBy": {"@type": "@id"}
                },
                "type": "object",
                "title": propertyKey+" field schema generated by MIRCAT",
                "description": description,
                "_ui": {"inputType": "textfield"},
                "_valueConstraints": {
                    "requiredValue": required,
                    "multipleChoice": False,
                },
                "schema:name": propertyKey,
                "pav:createdOn": "2018-06-07T03:07:47-0700",
                "pav:createdBy": "https://metadatacenter.org/users/e856d779-6e24-4d72-a4e6-f7ae4b6419e2",
                "pav:lastUpdatedOn": "2018-06-07T03:07:47-0700",
                "oslc:modifiedBy": "https://metadatacenter.org/users/e856d779-6e24-4d72-a4e6-f7ae4b6419e2",
                "schema:schemaVersion": "1.4.0",
                "additionalProperties": False,
                "schema:description": description,
                "required": ["@value"],
                "properties": {
                    "@type": {
                        "oneOf": [
                            {
                                "format": "uri",
                                "type": "string"
                            },
                            {
                                "items": {
                                    "format": "uri",
                                    "type": "string"
                                },
                                "minItems": 1,
                                "type": "array",
                                "uniqueItems": True
                            }
                        ]
                    },
                    "rdfs:label": {
                        "type": [
                            "string",
                            "null"
                        ]
                    },
                    "@value": {
                        "type": [
                            "string",
                            "null"
                        ]
                    },
                }
            }

    return properties


def set_sub_context(schema):
    ignored_key = ["@id", "@type", "@context"]
    sub_context = {'properties': {}}

    for propertyKey in schema['properties']:
        if propertyKey not in ignored_key:
            if 'enum' in schema['properties'][propertyKey]:
                sub_context['properties'][propertyKey] = {"enum": schema['properties'][propertyKey]["enum"]}
            else:
                sub_context['properties'][propertyKey] = {"enum": [""]}

    sub_context["additionalProperties"] = False
    sub_context["type"] = "object"

    if "required" in schema:
        sub_context["required"] = []
        for item in schema["required"]:
            sub_context["required"].append(item)

    return sub_context


def set_template_element_property_minimals(sub_context, schema):
    properties = {
        "@context": sub_context,
        "@type": {
            "oneOf": [
                {
                    "format": "uri",
                    "type": "string"
                },
                {
                    "uniqueItems": True,
                    "minItems": 1,
                    "type": "array",
                    "items": {
                        "format": "uri",
                        "type": "string"
                    }
                }
            ]
        },
        "@id": {
            "format": "uri",
            "type": "string"
        }
    }

    if 'enum' in schema["@type"]:
        enum = []
        for item in schema["@type"]['enum']:
            url = 'http://data.bioontology.org/ontologies/OBI/classes/'+quote(item, safe="")
            enum.append(url)
        properties["@type"]["oneOf"] = [
            {
                "format": "uri",
                "type": "string",
                "enum": enum
            },
            {
                "uniqueItems": True,
                "minItems": 1,
                "type": "array",
                "items": {
                    "format": "uri",
                    "type": "string",
                    "enum": enum
                }
            }
        ]

    return properties


def set_stripped_properties(schema):
    ignored_key = ["@id", "@type", "@context"]
    properties = {}

    for propertyKey in schema['properties']:
        if propertyKey not in ignored_key:
            properties[propertyKey] = schema['properties'][propertyKey]

    return properties
