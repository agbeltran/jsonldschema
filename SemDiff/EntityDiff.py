if __name__ == '__main__':

    DATS_data = {
        "person_schema.json": {
            "sdo": "https://schema.org/",
            "Person": "sdo:Person",
            "identifier": "sdo:identifier",
            "firstName": "sdo:givenName",
            "lastName": "sdo:familyName",
            "fullName": "sdo:name",
            "email": "sdo:email",
            "affiliations": "sdo:affiliation",
            "roles": "sdo:roleName"
        },
        "identifier_info_schema.json": {
            "sdo": "https://schema.org/",
            "Identifier": "sdo:Thing",
            "identifier": "sdo:identifier",
            "identifierSource": {
                "@id": "sdo:Property",
                "@type": "sdo:Text"
            }
        }
    }

    MIACA_data = {
        "person_schema.json": {
            "sdo": "https://schema.org/",
            "Person": "sdo:Person",
            "identifier": "sdo:identifier",
            "firstName": "sdo:givenName",
            "lastName": "sdo:familyName",
            "fullName": "sdo:name",
            "email": "sdo:email",
            "affiliations": "sdo:affiliation",
            "roles": "sdo:roleName"
        },
        "identifier_info_schema.json": {
            "sdo": "https://schema.org/",
            "Identifier_info": "sdo:Thing",
            "identifier": "sdo:identifier",
            "identifierSource": {
                "@id": "sdo:Property",
                "@type": "sdo:Text"
            }
        }
    }

    networks = [DATS_data, MIACA_data]

    DATS_network = {}
    MIACA_network = {}

    counter = 0
    for network in networks:
        for schema in network:
            schema_name = schema.replace("_schema.json", "").capitalize()
            schema_type = None

            if counter == 0:
                schema_context = DATS_data[schema]
            else:
                schema_context = MIACA_data[schema]

            if schema_name in schema_context.keys():
                schema_type = schema_context[schema_name]

            if counter == 0:
                DATS_network[schema_name] = schema_type
            elif counter == 1:
                MIACA_network[schema_name] = schema_type
        counter += 1

    coverage = {}

    item_total = 0
    matched_item = 0
    for item in DATS_network:
        item_total += 1
        context_type = DATS_network[item]
        matched = False
        for item2 in MIACA_network:
            context_type2 = MIACA_network[item2]
            if context_type == context_type2:
                matched = True
                if item in coverage.keys():
                    coverage[item].append(item)
                else:
                    coverage[item] = [item2]
        if matched is False:
            coverage[item] = None
        else:
            matched_item += 1

    print(coverage)
    print('Coverage:' + str((matched_item/item_total)*100) + '%')