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
            ID = "https://repo.metadatacenter.org/templates/c72b7362-ad7a-4120-8b4b-46db8f98ad3b"
            orig_schema_file.close()

            cedar_schema = cedar_template.render(orig_schema,
                                                 TEMPLATE_CONTEXT=cedar.utils.set_context(),
                                                 TEMPLATE_TYPE=cedar_type,
                                                 PROP_CONTEXT=cedar.utils.set_prop_context(orig_schema),
                                                 NOW="2018-05-30T06:43:49-0700",
                                                 REQ=cedar.utils.set_required_item(orig_schema),
                                                 ID=ID,
                                                 PROP_ITEMS=cedar.utils.set_properties_base_item(),
                                                 USER_URL="https://metadatacenter.org/users/e856d779-6e24-4d72-a4e6-f7ae4b6419e2")

            return cedar_schema

    except IOError:
        logging.error("Error opening schema file")


def json_pretty_dump(json_object, output_file):
    return json.dump(json_object,  output_file, sort_keys=False, indent=4, separators=(',', ': '))