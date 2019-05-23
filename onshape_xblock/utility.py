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

def res_to_dict(res):
    """Convert the standard http response to a dict of the body"""
    return json.loads(res.data)

def merge_d(filler, template):
    """Merge a "filler" dictionary into a "template" dictionary. Two guarantees: the template keys are never overwritten
    (but values can be, and keys can be added) and all filler values are pushed in. Respects the 'type' keyword as
    signifying an ordered dictionary.

    Examples
    ========
    >>> from onshape_xblock.utility import merge_d
    >>> filler = {"key1": "value1", "key2": "value2", "key3": {"key4": "value4", "key5": ["value6", "value7"]}}
    >>> template = {"key1": "result1", "key2": "result2", "key3": {"key4": "result4", "key5": ["result6", "result7"]}}
    """
    new = {}
    if isinstance(filler, dict):
        for k,v in filler.items():
            if k not in template:
                template[k] = v
            else:
                template[k] = merge_d(filler, template)
    else:
        return template







