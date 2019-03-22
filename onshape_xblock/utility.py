import urlparse
import os
import json
import pint
from jsonpickle import encode, decode


u = pint.UnitRegistry()

def quantify(s, default_units=u.m, tolerance=None):
    """Take a string and turn it into a pint quantity. If the string doesn't have an associated unit, use the one
    specified in default_units. Error specifies a relative tolerance for the measurement. 0.1 means an tolerance of +/-10%."""
    if isinstance(s, u.Quantity):
        return s
    q = u(str(s))
    if not isinstance(q, u.Quantity):
        q = q*u.dimensionless
    if isinstance(q, float) or q.units == u.dimensionless and default_units:
        q = q*default_units
    if tolerance:
        q = q.plus_minus(float(tolerance), relative=True)
    return q


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

def parse_url():
    raise NotImplemented

def res_to_dict(res):
    """Convert the standard http response to a dict of the body"""
    return json.loads(res.data)

