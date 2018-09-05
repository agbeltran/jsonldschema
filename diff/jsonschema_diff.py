
def equal_dicts(d1, d2, ignore_keys):
    """
    Compare two dictionaries d1 and d2, ignoring the list of keys given as ignore_keys
    """
    ignored = set(ignore_keys)
    for k1, v1 in iter(d1.items()):
        if k1 not in ignored and (k1 not in d2 or d2[k1] != v1):
            return False
    for k2, v2 in iter(d2.items()):
        if k2 not in ignored and k2 not in d1:
            return False
    return True


def diff_dicts(d1, d2, ignore_keys):
    """
    Return the difference between two dictionaries d1 and d2, ignoring the list of keys given as
    parameter ignore_keys
    """
    ignored = set(ignore_keys)
    diff = set()
    for k1, v1 in iter(d1.items()):
        if k1 not in ignored and (k1 not in d2 or d2[k1] != v1):
            diff.add(k1)
    for k2, v2 in iter(d2.items()):
        if k2 not in ignored and k2 not in d1:
            diff.add(k2)
    return diff


def compare_dicts(source_template, valid_template, lvl):
    """
    Display the difference between a source to validate (source_template) and a valid template
    (valid_template)
    """
    for key in source_template:

        if key not in valid_template:
            if lvl == 0:
                print('=======================')

        if (key in valid_template) and (source_template[key] != valid_template[key]):
            if lvl == 0:
                print('=======================')

            if type(valid_template[key]) is dict:
                print("\t" * lvl + " issue with field " + key + " (object)")
                compare_dicts(source_template[key], valid_template[key], lvl + 1)

            elif type(valid_template[key]) is str:
                print("\t" * lvl + " difference of value in " + key)
                print("\t" + "\t" * lvl + " --- " + source_template[key] +
                      " VS " + valid_template[key] + " --- ")

            else:
                print("\t" * lvl + " difference of value in " + key)
                print(source_template[key])
                print("VS")
                print(valid_template[key])

    # Verify all keys in the valid template are present in the source template
    for key in valid_template:
        if key not in source_template:
            if lvl == 0:
                print('=======================')
            print("\t" * lvl + key + " is absent from SOURCE template")
            print(valid_template[key])
