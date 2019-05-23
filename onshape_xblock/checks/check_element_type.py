from onshape_xblock.check_imports import *


class CheckElementType(CheckBase):
    """An element type check

    This element type check checks whether or not the specified Onshape element is the correct element type. """

    failure_message_template = "The element you passed in is a {{ actual_element_type }} rather than the expected {{ expected_element_type }}."
    success_message_template = "Element type check passed!"
    additional_form_properties = {
                "expected_element_type": {
                        "title": "The expected element type.",
                        "type": "string",
                        "default": "List",
                        "enum": [
                            "Partstudio",
                            "Assembly",
                            "Drawing",
                            "Blob"
                        ],
                        "uniqueItems": True
                    }
            }

    def __init__(self,
                 expected_element_type=None,
                 **kwargs):
        super(CheckElementType, self).__init__(name="Check Element Type",
                                          **kwargs)
        self.expected_element_type = expected_element_type



    def execute_check(self):
        response = self.client.elements_api.get_element_metadata(self.onshape_element.did, self.onshape_element.wvm, self.onshape_element.wvmid, self.onshape_element.eid, _preload_content=False)
        self.actual_element_type = res_to_dict(response)["type"].lower().capitalize()
        self.passed = (self.actual_element_type == self.expected_element_type)
