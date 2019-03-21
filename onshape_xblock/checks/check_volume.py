from onshape_xblock.checks.check_standard_imports import *
from onshape_xblock.utility import quantify, u

class CheckVolume(CheckBase):
    """A volume check

    This volume checks whether or not the specified Onshape part has a volume in between the min and max specified. """

    failure_message_template = "Your part's volume of {{volume}} is incorrect. It should be between {{min_volume}} and {{max_volume}}. {{points}}/{{max_points}}"
    success_message_template = "Volume check passed!"

    def __init__(self,
                 min=0*u.m**3,
                 max=1*u.m**3,
                 part_number=0,
                 **kwargs):
        super(CheckVolume, self).__init__(name="Check Volume",
                                          **kwargs)
        self.min = quantify(min, default_units=u.m**3)
        self.max = quantify(max, default_units=u.m**3)
        self.part_number = part_number
        self.volume = None

    def execute_check(self):
        part_id = self.get_part_id(self.part_number)
        mass_properties = self.get_mass_properties(part_id)
        self.volume = quantify(mass_properties.bodies["-all-"].volume[0], default_units=u.m**3)
        self.passed = (self.min < self.volume < self.max)


