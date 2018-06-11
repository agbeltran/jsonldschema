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