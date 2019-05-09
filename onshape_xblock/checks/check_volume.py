from onshape_xblock.check_imports import *


class CheckVolume(CheckBase):
    """A volume check

    This volume checks whether or not the specified Onshape part has a volume in between the min and max specified. """

    failure_message_template = "Your part's volume of {{volume}} is incorrect. It should be between {{min_volume}} and {{max_volume}}. {{points}}/{{max_points}}"
    success_message_template = "Volume check passed!"
    additional_form_properties = {
                "part_number": {
                    "default": 0,
                    "description": "a longer description, perhaps with some html?",
                    "type": "number",
                    "title": "The index of the part in the parts list"
                },
                "min_volume": {
                    "type": "string",
                    "default": "0 meter**3",
                    "title": "The minimum volume the part can have. If no units are specified, defaults to meter**3."
                },
                "max_volume": {
                    "type": "string",
                    "default": "1 meter**3",
                    "title": "The maximum volume the part can have. If no units are specified, defaults to meter**3."
                }
            }

    def __init__(self,
                 min_volume=0 * u.m ** 3,
                 max_volume=1 * u.m ** 3,
                 part_number=0,
                 **kwargs):
        super(CheckVolume, self).__init__(name="Check Volume",
                                          **kwargs)
        self.min_volume = quantify(min_volume, default_units=u.m ** 3)
        self.max_volume = quantify(max_volume, default_units=u.m ** 3)
        self.part_number = part_number
        self.volume = None


    def execute_check(self):
        part_id = self.get_part_id(self.part_number)
        mass_properties = self.get_mass_properties(part_id)
        self.volume = quantify(mass_properties.bodies["-all-"].volume[0], default_units=u.m ** 3)
        self.passed = (self.min_volume < self.volume < self.max_volume)
