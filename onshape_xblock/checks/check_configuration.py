from onshape_xblock.checks.check_standard_imports import *
from onshape_xblock.utility import quantify, u
from onshape_xblock.feedback import Feedback


class CheckConfiguration(CheckBase):
    """A configuration check

    This configuration check checks whether or not the specified Onshape part has a configuration within the bounds defined. """


    failure_message_template = "Your PartStudio has a {config_type_actual} in the configuration where it should have a {config_type_expected} configuration type."
    success_message_template = "Your part's volume of {volume} is correct! You've been awarded {points}/{max_points}!"

    map = {"BTMConfigurationParameterEnum": {"type": "List", "entry_name": "row"},
           "BTMConfigurationParameterQuantity": {"type": "Variable", "entry_name": "usage"},
           "BTMConfigurationParameterBoolean": {"type": "Checkbox", "entry_name": "features"}}

    def __init__(self,
                 desired_configuration_list=[],
                 **kwargs):
        super(CheckConfiguration, self).__init__(name="Check Configuration", **kwargs)
        self.desired_configuration_list = desired_configuration_list

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



