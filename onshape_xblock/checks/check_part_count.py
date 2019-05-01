from onshape_xblock.check_imports import *

class CheckPartCount(CheckBase):
    """A volume check

    This volume checks whether or not the specified Onshape part has a volume in between the min and max specified. """

    failure_message_template = "Your part's volume of {volume} is incorrect. It should be between {min_volume} and {max_volume}. {points}/{max_points}"
    success_message_template = "Your part's volume of {volume} is correct! You've been awarded {points}/{max_points}!"

    def __init__(self,
                 min=0*u.m,
                 max=1*u.m,
                 part_number=0,
                 **kwargs):
        super(CheckPartCount, self).__init__(name="Check Volume",
                                          **kwargs)
        self.min = quantify(min, default_units=u.m**3)
        self.max = quantify(max, default_units=u.m**3)
        self.part_number = part_number

    def execute_check(self):
        part_id = self.get_part_id(self.part_number)
        mass_properties = self.get_mass_properties(part_id)
        volume = quantify(mass_properties.bodies["-all-"].volume[0], default_units=u.m**3)
        self.feedback = Feedback()
        self.feedback.volume = quantify(mass_properties.bodies["-all-"].volume[0], default_units=u.m**3)
        self.feedback.passed = (self.min < volume < self.max)
        self.feedback.min_volume = self.min
        self.feedback.max_volume = self.max
        self.feedback.points = self.points if self.feedback.passed else 0
        self.feedback.max_points = self.points



