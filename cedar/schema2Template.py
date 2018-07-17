import json
import os
import cedar.utils
import cedar.client
import logging
from jinja2 import Template
import datetime
from cedar.schema2TemplateElement import set_sub_specs

configfile_path = os.path.join(os.path.dirname(__file__), "../tests/test_config.json")
if not (os.path.exists(configfile_path)):
    print("Please, create the config file.")
with open(configfile_path) as config_data_file:
    config_json = json.load(config_data_file)
config_data_file.close()

_data_dir = os.path.join(os.path.dirname(__file__), "data")
production_api_key = config_json["production_key"]
folder_id = config_json["folder_id"]
user_id = config_json["user_id"]


cedar_template = Template ('''
{% set props = ["@context", "@type", "@id" ] %}
{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "@id": null,
    "@context": {{ TEMPLATE_CONTEXT | tojson }},
    "@type": "{{ TEMPLATE_TYPE }}",
    "type": "object",
    "title": "{{ title }} element schema", 
    "description": "{{ description }} ",
    "schema:name": "{{title}}",
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
            {% for item in TEMP_PROP %}
                "{{item}}" {% if not loop.last %},{% endif %}      
            {% endfor %} 
        ],
        "propertyLabels": {
            {% for item in TEMP_PROP %}   
                "{{item}}" : "{{item}}"{% if not loop.last %},{% endif %} 
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
        }
        {% if REQ %},{% endif %}
        {% for itemKey, itemVal in REQ.items() %}
            ,"{{itemKey}}": {{itemVal | tojson}}
        {% endfor %}
        {% for itemKey, itemVal in SUB_SPECS.items() %}
            ,"{{itemKey}}": {{itemVal | tojson}}
        {% endfor %}             
    }
}
''')


def convert_template(schema_filename):
    cedar_type = "https://schema.metadatacenter.org/core/Template"

    try:
        with open(schema_filename, 'r') as orig_schema_file:

            input_json_schema = json.load(orig_schema_file)
            orig_schema_file.close()

            # Set the current date
            now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S-0700')

            # Set the user url
            user_url = "https://metadatacenter.org/users/" + config_json["user_id"]

            # Set the sub-specifications from $ref if needed, enabling templateElement nesting
            sub_spec_container = {}
            sub_spec = set_sub_specs(input_json_schema['properties'], sub_spec_container)

            cedar_schema = cedar_template.render(input_json_schema,
                                                 TEMPLATE_CONTEXT=cedar.utils.set_context(),
                                                 TEMPLATE_TYPE=cedar_type,
                                                 PROP_CONTEXT=cedar.utils.set_prop_context(input_json_schema),
                                                 NOW=now,
                                                 REQ=cedar.utils.set_required_item(input_json_schema),
                                                 PROP_ITEMS=cedar.utils.set_properties_base_item(),
                                                 USER_URL=user_url,
                                                 TEMP_PROP=cedar.utils.set_stripped_properties(input_json_schema),
                                                 SUB_SPECS=sub_spec)

            return cedar_schema

    except IOError:
        logging.error("Error opening schema file")


def json_pretty_dump(json_object, output_file):
    return json.dump(json_object,  output_file, sort_keys=False, indent=4, separators=(',', ': '))


if __name__ == "__main__":
    input_schema = "../tests/data/schema.json"
    input_filename = os.path.join(input_schema)  # path to the schema we want to convert
    output_schema = convert_template(input_filename)
    response = cedar.client.CEDARClient().validate_template("production", production_api_key, json.loads(output_schema))

    # save the converted file
    output_schema_file = open(os.path.join("../tests/data/schema_out.json"), "w")
    json_pretty_dump(json.loads(output_schema), output_schema_file)
    output_schema_file.close()

    response = cedar.client.CEDARClient().create_template("production",
                                                          production_api_key,
                                                          folder_id,
                                                          os.path.join("../tests/data/schema_out.json"))
