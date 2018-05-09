


"""
Compare two dictionaries d1 and d2, ignoring the list of keys given as ignore_keys
"""
def equal_dicts(d1, d2, ignore_keys):
    ignored = set(ignore_keys)
    for k1, v1 in iter(d1.items()):
        if k1 not in ignored and (k1 not in d2 or d2[k1] != v1):
            return False
    for k2, v2 in iter(d2.items()):
        if k2 not in ignored and k2 not in d1:
            return False
    return True


"""
Return the difference between two dictionaries d1 and d2, ignoring the list of keys given as parameter ignore_keys
"""
def diff_dicts(d1, d2, ignore_keys):
    ignored = set(ignore_keys)
    diff = set()
    for k1, v1 in iter(d1.items()):
        if k1 not in ignored and (k1 not in d2 or d2[k1] != v1):
            diff.add(k1)
    for k2, v2 in iter(d2.items()):
        if k2 not in ignored and k2 not in d1:
            diff.add(k2)
    return diff
