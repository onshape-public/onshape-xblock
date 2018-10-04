import urlparse
import os
from path import Path
import json


def parse_url(url):
    """Parse an Onshape element url into a dictionary containing did, eid, and wvm_pair"""
    path = urlparse.urlparse(url).path.split('/')
    # Expected parameters in the path
    d_expected = {3: "wvm_type", 2: "did", 6: "eid", 4: "wvm"}
    d = {}
    for index, name in d_expected.items():
        try:
            d[name] = path[index]
        except IndexError:
            pass
    d["wvm_pair"] = (d["wvm_type"], d["wvm"])
    return d

def prepopulate_json(d, path_to_json_root):
    """ Returns a prepopulated JSON. At the very least, all metatype keys and type keys are gauranteed to be filled in
    with minimum parameters. A metatype is a key that matches a folder name within the json_root. A type is the value
    of the "type" key within the d, and should correspond to the file name of the prepopulated d for that type.
    Within a metatype, we can have either a list of objects with types, or a single object with a type. All dict objects
    must have a type."""

    #The metatypes available at the given context
    metatypes = [name for name in os.listdir(path_to_json_root) if os.path.isdir(os.path.join(path_to_json_root, name))]

    # Base case: there is no type key.
    if "type" not in d:
        return d

    # Non-destructively update the type with the necessary fields:
    try:
        # Update the prepopulated dictionary with the passed in d, so as not to overwrite user-defined behavior
        type_def_path = os.path.join(path_to_json_root, d["type"] + ".json")
        type_def = json.load(open(type_def_path, "r"))
        d = {k: v for d in [type_def, d] for k, v in d.items()}
    except IOError:
        raise UserWarning("Cannot find the type definition that should be located here:" + type_def_path)

    # Recursively enter the metatypes to build up the d:
    for metatype in metatypes:
        if metatype in d:
            child = d[metatype]
            # If the metatype is pointing to a list, prepopulate each item
            if isinstance(child, list):
                json_list = []
                for child_d in child:
                    json_list.append(prepopulate_json(child_d, os.path.join(path_to_json_root, metatype)))
                d[metatype] = json_list

            # If the metatype is pointing to a single dict, then call prepopulate_json on just the single item
            if isinstance(child, dict):
                d[metatype] = prepopulate_json(child, os.path.join(path_to_json_root, metatype))

    return d
