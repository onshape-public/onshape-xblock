from onshape_xblock.check_imports import *


class CheckMass(CheckBase):
    """A Mass Check

    This mass check checks whether or not the specified Onshape part has a volume in between the min and max specified. """

    failure_message_template = "Your part's mass of {mass} is incorrect. It should be between {{min_mass}} and {{max_mass}}. {{points}}/{{max_points}}"

    def __init__(self,
                 min_mass=0*u.kg,
                 max_mass=1*u.kg,
                 part_number=0,
                 **kwargs):
        super(CheckMass, self).__init__(name="Check Mass",
                                          **kwargs)
        self.min_mass = quantify(min_mass, default_units=u.kg)
        self.max_mass = quantify(max_mass, default_units=u.kg)
        self.part_number = part_number
        self.mass = None

    def execute_check(self):
        part_id = self.get_part_id(self.part_number)
        mass_properties = self.get_mass_properties(part_id)
        self.mass = quantify(mass_properties.bodies["-all-"].mass[0], default_units=u.kg)
        self.passed = (self.min_mass < self.mass < self.max_mass)



