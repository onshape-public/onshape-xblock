"""This is a wrapper on the xblock fields that establishes onshape fields. Those fields are used to generate the
studio_view edit form. They describe the intended structure of the data within the class."""

from xblock.fields import Boolean, Float, Integer, Scope, String, Dict, List, JSONField
from onshape_xblock.utility import quantify

class Quantity(JSONField):
    """
    A field that contains a float.

    The value, as loaded or enforced, can be None, '' (which will be treated as
    None), a Python float, or a value that will parse as an float, ie.,
    something for which float(value) does not throw an error.

    """
    MUTABLE = False

    def from_json(self, value):
        if value is None or value == '':
            return None
        return quantify(value)

    enforce_type = from_json