from onshape_xblock.check_imports import *


class CheckElementType(CheckBase):
    """An element type check

    This element type check checks whether or not the specified Onshape element is the correct element type. """

    instance_type_key = "feature_type"
    feature_list_target_default = [{instance_type_key: "newSketch"}, {instance_type_key: "extrude"}]
    additional_form_properties = {
        "instance_list_type_target": {
            "type": "array",
            "title": "Target instance list definition",
            "items": {
                "type": "object",
                "title": "Instance",
                "properties": {
                    instance_type_key: {
                        "title": "The feature type (ex. boolean, extrude, etc...)",
                        "description": "note that a sketch has a feature type of 'newSketch'",
                        "type": "string",
                        "default": "extrude"
                    }
                }
            }
        }
    }

    def __init__(self,
                 expected_element_type=None,
                 **kwargs):
        super(CheckElementType, self).__init__(name="Check Element Type",
                                          **kwargs)
        self.expected_element_type = expected_element_type



    def execute_check(self):
        self.actual_element_type = self.get_element_type()
        self.passed = (self.actual_element_type == self.expected_element_type)
