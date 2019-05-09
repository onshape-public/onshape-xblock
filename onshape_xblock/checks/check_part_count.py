from onshape_xblock.check_imports import *

class CheckPartCount(CheckBase):
    """A volume check

    This volume checks whether or not the specified Onshape part has a volume in between the min and max specified. """

    failure_message_template = "Your element's part count of {{actual_part_count}} is incorrect. The element should have {{target_part_count}}."
    success_message_template = "Your element's part count of {{actual_part_count}} is correct!"
    additional_form_properties = {
        "target_part_count": {
            "type": "number",
            "title": "Target part count:",
            "default": 1
        }
    }

    def __init__(self,
                 target_part_count=1,
                 **kwargs):
        super(CheckPartCount, self).__init__(name="Check part count",
                                          **kwargs)
        self.target_part_count = target_part_count

    def execute_check(self):
        self.actual_part_count = len(self.get_parts())
        self.passed = self.actual_part_count == self.target_part_count




