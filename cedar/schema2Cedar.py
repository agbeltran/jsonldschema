import json
import os
import logging
from jinja2 import Template
from urllib.parse import quote, urlparse
import datetime
import cedar.client
import requests


loaded_specs = {}


class Schema2CedarBase:
    """ The base converter class, should not be called ! """

    def __new__(cls, api_key, folder_id, user_id):
        if cls is Schema2CedarBase:
            raise TypeError("base class may not be instantiated")
        else:
            cls.production_api_key = api_key
            cls.folder_id = folder_id
            cls.user_id = user_id
        return object.__new__(cls)

    @staticmethod
    def json_pretty_dump(json_object, output_file):
        return json.dump(json_object, output_file, sort_keys=False, indent=4, separators=(',', ': '))

    @staticmethod
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

    @staticmethod
    def set_properties_base_item():
        return {
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

    @staticmethod
    def set_prop_context(schema):

        prop_context = {
            "pav:createdOn": {
                "properties": {
                    "@type": {
                        "enum": ["xsd:dateTime"],
                        "type": "string"
                    }
                },
                "type": "object"
            },
            "pav:lastUpdatedOn": {
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

    @staticmethod
    def set_required_item(schema):
        ignored_key = ["@id", "@type", "@context"]
        properties = {}

        for propertyKey in schema['properties']:
            if propertyKey not in ignored_key \
                    and '$ref' not in schema['properties'][propertyKey] \
                    and (('items' in schema['properties'][propertyKey]
                          and '$ref' not in schema['properties'][propertyKey]['items'])
                         or 'items' not in schema['properties'][propertyKey]):

                if "description" in schema['properties'][propertyKey]:
                    description = schema['properties'][propertyKey]['description']

                else:
                    description = propertyKey

                if 'required' in schema and propertyKey in schema['required']:
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
                    "title": propertyKey + " field schema generated by MIRCAT",
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

    @staticmethod
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

    @staticmethod
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

        if "@type" in schema and 'enum' in schema["@type"]:
            enum = []
            for item in schema["@type"]['enum']:
                url = 'http://data.bioontology.org/ontologies/OBI/classes/' + quote(item, safe="")
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

    @staticmethod
    def set_stripped_properties(schema):
        ignored_key = ["@id", "@type", "@context"]
        properties = {}

        for propertyKey in schema['properties']:
            if propertyKey not in ignored_key:
                properties[propertyKey] = schema['properties'][propertyKey]

        return properties


class Schema2CedarTemplate(Schema2CedarBase):
    """ Schema 2 Template Converter, this is the one you want to use """

    cedar_template = Template('''
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
        {% for itemKey, itemVal in REQ.items() %}
            ,"{{itemKey}}": {{itemVal | tojson}}
        {% endfor %}
        {% for itemKey, itemVal in SUB_SPECS.items() %}
            ,"{{itemKey}}": {{itemVal | tojson}}
        {% endfor %}             
    }
}
''')

    def convert_template(self, input_json_schema):
        cedar_type = "https://schema.metadatacenter.org/core/Template"

        # Set the current date
        now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S-0700')

        # Set the user url
        user_url = "https://metadatacenter.org/users/" + self.user_id

        # Set the sub-specifications from $ref if needed, enabling templateElement nesting
        sub_spec_container = {}
        sub_spec = Schema2CedarTemplateElement(self.production_api_key,
                                               self.folder_id,
                                               self.user_id)\
            .find_sub_specs(input_json_schema, sub_spec_container)

        return self.cedar_template.render(input_json_schema,
                                          TEMPLATE_CONTEXT=self.set_context(),
                                          TEMPLATE_TYPE=cedar_type,
                                          PROP_CONTEXT=self.set_prop_context(input_json_schema),
                                          NOW=now,
                                          REQ=self.set_required_item(input_json_schema),
                                          PROP_ITEMS=self.set_properties_base_item(),
                                          USER_URL=user_url,
                                          TEMP_PROP=self.set_stripped_properties(input_json_schema),
                                          SUB_SPECS=sub_spec)


class Schema2CedarTemplateElement(Schema2CedarBase):
    """Schema to TemplateElement converter, should not be called directly"""

    cedar_template_element = Template('''
    {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "@id": null,
        "@context": {{TEMPLATE_CONTEXT | tojson}},
        "@type": "{{TEMPLATE_TYPE}}",
        "type": "object",
        "title": "{{title}} element schema", 
        "description": "{{description}} ",
        "schema:name": "{{FIELD_KEY}}",
        "schema:description": "{{description}}",
        "schema:schemaVersion": "1.4.0",
        "bibo:status":"bibo:draft",
        "pav:version":"0.1",
        "pav:createdOn": "{{NOW}}",
        "pav:lastUpdatedOn": "{{NOW}}",
        "pav:createdBy": "{{USER_URL}}",
        "oslc:modifiedBy": "{{USER_URL}}",
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
            }
        },
        {% set requiredList = required %}
        "required":[
            "@context",
            "@id"
            {% for item in requiredList %}
                ,"{{item}}"
            {% endfor %}
        ],
        "properties": {
            {% for itemKey, itemVal in PROP_CONTEXT.items() %}    
                "{{itemKey}}": {{itemVal | tojson}} {% if not loop.last %},{% endif %}
            {% endfor %},
            {% for itemKey, itemVal in TEMP_PROP.items() %}
                {% if '$ref' in itemVal %}
                    {% if itemKey in SUB_SPECS %} "{{itemKey}}": {{SUB_SPECS[itemKey] | tojson}}                     
                    {% endif %}
                {% elif 'items' in itemVal and '$ref' in itemVal['items'] %}
                    {% if itemKey in SUB_SPECS %} "{{itemKey}}": {{SUB_SPECS[itemKey] | tojson}}                     
                    {% endif %}    
                {% else %}               
                    "{{itemKey}}": {
                        "@context": {{ITEM_CONTEXT | tojson}},
                        "title": "{{itemKey}} field schema generated by {{MIRCAT}}",
                        "schema:description": "{{itemKey}}",  
                        "additionalProperties": false,
                        "oslc:modifiedBy": "{{USER_URL}}",
                        "pav:createdOn": "{{NOW}}",
                        "_ui": {
                            "inputType": "textfield"
                        },
                        "description": 
                            {% if itemVal.description %} "{{itemVal.description}}" 
                            {%else %} "{{item}} autogenerated by {{MIRCAT}}" 
                            {% endif %},
                        "pav:lastUpdatedOn": "{{NOW}}",
                        "required": [
                            "@value"
                        ],
                        "@type": "https://schema.metadatacenter.org/core/TemplateField",
                        "_valueConstraints": {
                            {% if itemVal['_valueConstraints'] is defined and itemVal['_valueConstraints']['defaultValue'] is defined %}
                                "defaultValue": "{{itemVal['_valueConstraints']['defaultValue']}}",
                            {% endif %}
                            "requiredValue":
                                {% if (requiredList is defined) and (itemKey in requiredList) %} true 
                                {% else %} false 
                                {% endif%}
                        },
                        "pav:createdBy": "{{USER_URL}}",
                        "schema:name": "{{itemKey}}",
                        "@id": null,
                        "schema:schemaVersion": "1.4.0",
                        "type": "object",
                        "$schema": "http://json-schema.org/draft-04/schema#",
                        "properties": {
                            "@type": {
                                "oneOf": [
                                    {
                                      "format": "uri",
                                      "type": "string"
                                    },
                                    {
                                        "uniqueItems": true,
                                        "minItems": 1,
                                        "type": "array",
                                        "items": {
                                            "format": "uri",
                                            "type": "string"
                                        }
                                    }
                                ]
                            },
                            "@value": {
                                "type": [
                                    "string",
                                    "null"
                                ]
                            },
                            "rdfs:label": {
                                "type": [
                                    "string",
                                    "null"
                                ]
                            }
                        }
                    }
                {% endif %}                                                               
                {% if not loop.last %},{% endif %}
            {% endfor %}
        },
         "additionalProperties": {% if additionalProperties %} {{additionalProperties}} {% else %} false {% endif%}
    }
    ''')

    def convert_template_element(self, input_json_schema, **kwargs):
        cedar_type = "https://schema.metadatacenter.org/core/TemplateElement"

        try:
            # Set the current date
            now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S-0700')

            # Set the user url
            user_url = "https://metadatacenter.org/users/" + self.user_id

            # Set root['@context']
            context = self.set_context()

            # Set root['properties']['@context']
            property_context = self.set_template_element_property_minimals(self.set_sub_context(input_json_schema),
                                                                           input_json_schema['properties'])

            # Set root['properties']['item_name']['@context']
            item_context = dict(context)
            item_context.pop("bibo")

            # Set the sub-specifications from $ref if needed, enabling templateElement nesting
            sub_spec_container = {}
            sub_spec = self.find_sub_specs(input_json_schema, sub_spec_container)

            # Get the optional parameter for schema:name (useful when nesting)
            field_key = kwargs.get('fieldKey', None)
            if field_key is None:
                field_key = input_json_schema['title']

            # Return the Jinja2 template
            return self.cedar_template_element.render(input_json_schema,
                                                      TEMPLATE_TYPE=cedar_type,
                                                      TEMPLATE_CONTEXT=context,
                                                      NOW=now,
                                                      USER_URL=user_url,
                                                      MIRCAT="mircat-tools for python 3",
                                                      PROP_CONTEXT=property_context,
                                                      ITEM_CONTEXT=item_context,
                                                      TEMP_PROP=self.set_stripped_properties(input_json_schema),
                                                      SUB_SPECS=sub_spec,
                                                      FIELD_KEY=field_key)

        except IOError:
            logging.error("Error opening schema file")

    def find_sub_specs(self, schema, sub_spec_container):
        ignored_key = ["@id", "@type", "@context"]
        data_dir = os.path.join(os.path.dirname(__file__), "../tests/data")
        client = cedar.client.CEDARClient()
        headers = client.get_headers(self.production_api_key)
        request_url = client.selectEndpoint('production') \
                      + "/template-elements?folder_id=https%3A%2F%2Frepo.metadatacenter.org%2Ffolders%2F" \
                      + self.folder_id

        # For each field in the properties array
        for itemKey, itemVal in schema['properties'].items():

            # if the field is not to be ignored
            if itemKey not in ignored_key:

                # set the schema_path to load to None
                schema_as_json = None
                multiple_items = False

                if '$ref' in itemVal:
                    schema_as_json = self.load_sub_spec(itemVal['$ref'], schema, itemKey)

                elif 'items' in itemVal and '$ref' in itemVal['items']:
                    schema_as_json = self.load_sub_spec(itemVal['items']['$ref'], schema, itemKey)
                    multiple_items = True

                elif ('items' in itemVal and ('anyOf' in itemVal['items'] or 'oneOf' in itemVal['items'])) \
                        or ('anyOf' in itemVal) \
                        or ('oneOf' in itemVal):

                    # REFINING HERE -> DELETE ALL ITEMS FROM SERVER !! (or change algo to validate all templates first.
                    print(schema)
                    raise ValueError("'anyOf' and 'oneOf' are not supported by CEDAR (schema affected: )")

                # if the schema_path is set
                if schema_as_json is not None:

                    if itemKey not in loaded_specs.keys():

                        temp_spec = json.loads(self.convert_template_element(schema_as_json, fieldKey=itemKey))

                        # NEED SOME REFINING HERE -> VALIDATE BEFORE POST !!!
                        response = requests.request("POST",
                                                    request_url,
                                                    headers=headers,
                                                    data=json.dumps(temp_spec),
                                                    verify=True)
                        temp_spec["@id"] = json.loads(response.text)["@id"]
                        if multiple_items:
                            sub_spec = {'items': temp_spec, "type": "array", "minItems": 1}
                        else:
                            sub_spec = temp_spec

                        loaded_specs[itemKey] = sub_spec

                    else:
                        sub_spec = loaded_specs[itemKey]

                    sub_spec_container[itemKey] = sub_spec

        return sub_spec_container

    def load_sub_spec(self, path_to_load, parent_schema, field_key):
        string_to_json = None
        url_to_load = None

        # Path to load is a URL
        if urlparse(path_to_load).scheme != "":
            url_to_load = path_to_load

        # Path to load isn't a URL
        else:
            if 'id' in parent_schema:
                url_to_load = parent_schema['id'].rsplit('/', 1)[0]+"/"+path_to_load
            else:
                with open(path_to_load, 'r') as orig_schema_file:
                    # Load the JSON schema and close the file
                    string_to_json = json.load(orig_schema_file)
                orig_schema_file.close()

        if url_to_load:
            if field_key not in loaded_specs.keys():
                string_from_url = requests.request("GET", url_to_load)
                string_to_json = json.loads(string_from_url.text)

        return string_to_json

