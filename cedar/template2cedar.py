import json
import logging
import cedar.utils
from jinja2 import Template

#TODO get required attributes from required
#TODO Set _ui input type based on field expected type


cedar_template = Template('''
{% set props = ["@context", "@type", "@id" ] %}
{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "@id": "{{ID}}",
    "@context": {{ TEMPLATE_CONTEXT | tojson }},
    "@type": "{{ TEMPLATE_TYPE }}",
    "type": "object",
    "title": "{{ title }} element schema", 
    "description": "{{ description }} ",
    "schema:name": "{{ id }}",
    "schema:description": "{{ description }}",
    "schema:schemaVersion": "1.4.0",
    "bibo:status":"bibo:draft",
    "pav:version":"0.1",
    "pav:createdOn": "{{ NOW  }}",
    "pav:lastUpdatedOn": "{{ NOW  }}",
    "pav:createdBy": "{{ USER_URL }}",
    "oslc:modifiedBy": "{{ USER_URL }}",
    "_ui": { 
        "order": [ 
            {% for item in properties %}
                {% if not item in props %} "{{ item }}" {% if not loop.last %},{% endif %} {% endif %}       
            {% endfor %} 
        ],
        "propertyLabels": {
            {% for item in properties %} 
                {% if not item in props %}  "{{ item }}" : "{{ item }}"{% if not loop.last %},{% endif %} {% endif %}
            {% endfor %} 
        },
        "pages": []
    },
    "required": [
        "@context",
        "@id",
        "schema:isBasedOn",
        "schema:name",
        "schema:description",
        "pav:createdOn",
        "pav:createdBy",
        "pav:lastUpdatedOn",
        "oslc:modifiedBy",
        "pav:version",
        "bibo:status"
    ],   
    "additionalProperties": {% if additionalProperties %} {{ additionalProperties }} {% else %} false {% endif%},
    "properties":{
        {% for itemKey, itemVal in PROP_ITEMS.items() %}
            "{{itemKey}}": {{itemVal | tojson}} {% if not loop.last %},{% endif %}
        {% endfor %},
        "@context":{
            "additionalProperties": false,
            "type": "object",
            "properties": {{ PROP_CONTEXT | tojson }},
            "required": [
                "xsd",
                "pav",
                "schema",
                "oslc",
                "schema:isBasedOn",
                "schema:name",
                "schema:description",
                "pav:createdOn",
                "pav:createdBy",
                "pav:lastUpdatedOn",
                "oslc:modifiedBy"
            ]    
        },
        {% for itemKey, itemVal in REQ.items() %}
        "{{itemKey}}": {{itemVal | tojson}} {% if not loop.last %},{% endif %}
        {% endfor %}    
    }
}
''')


def convert_template(schema_filename):
    cedar_type = "https://schema.metadatacenter.org/core/Template"
    try:
        with open(schema_filename, 'r') as orig_schema_file:

            orig_schema = json.load(orig_schema_file)
            REQUIRED = set_required_item(orig_schema)
            ID = "https://repo.metadatacenter.org/templates/c72b7362-ad7a-4120-8b4b-46db8f98ad3b"
            orig_schema_file.close()

            cedar_schema = cedar_template.render(orig_schema,
                                                 TEMPLATE_CONTEXT=cedar.utils.set_context(),
                                                 TEMPLATE_TYPE=cedar_type,
                                                 PROP_CONTEXT=set_prop_context(orig_schema),
                                                 NOW="2018-05-30T06:43:49-0700",
                                                 REQ=REQUIRED,
                                                 ID=ID,
                                                 PROP_ITEMS=cedar.utils.set_properties_base_item(),
                                                 USER_URL="https://metadatacenter.org/users/e856d779-6e24-4d72-a4e6-f7ae4b6419e2")

            return cedar_schema

    except IOError:
        logging.error("Error opening schema file")




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
                    "bibo": "http://purl.org/ontology/bibo/",
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





def json_pretty_dump(json_object, output_file):
    return json.dump(json_object,  output_file, sort_keys=False, indent=4, separators=(',', ': '))