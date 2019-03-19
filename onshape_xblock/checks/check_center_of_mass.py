from onshape_xblock.checks.check_standard_imports import *
from onshape_xblock.utility import quantify, u
from onshape_xblock.feedback import Feedback


class CheckCenterOfMass(CheckBase):
    """A center of mass check

    This center of mass check determines if the specified part has a center of mass within a tolerance of a certain location in space."""

    failure_message_template = "Your part's center of mass, {{guess_centroid}} is incorrect. It should be within {{target_centroid}} with a tolerance of +/-{{tolerance}}. {{points}}/{{max_points}}"
    success_message_template = "Your center of mass is correct. {{points}}/{{max_points}}!"

    def __init__(self,
                 target_centroid = [0,0,0],
                 tolerance=0.001,
                 part_number=0,
                 **kwargs):
        super(CheckCenterOfMass, self).__init__(name="Check Center of Mass",
                                          **kwargs)
        self.target_centroid = target_centroid
        self.tolerance = tolerance
        self.part_number = part_number

    def execute_check(self):
        part_id = self.get_part_id(self.part_number)
        tolerance = quantify(self.tolerance, default_units=u.m)
        mass_properties = self.get_mass_properties(part_id)
        target_centroid = [quantify(x, default_units=u.m) for x in self.target_centroid]
        guess_centroid = [quantify(x, default_units=u.m) for x in
                          mass_properties.bodies["-all-"].centroid[0:3]]
        c = []
        for x, target in zip(guess_centroid, target_centroid):
            c.append(x < target + tolerance)
            c.append(x > target - tolerance)
        passed = all(c)

        self.feedback = Feedback(
            passed=passed,
            target_centroid=str(",".join([str(x) for x in target_centroid])),
            guess_centroid=str(",".join([str(x) for x in guess_centroid])),
            tolerance=tolerance,
            max_points=self.points,
            points=self.points if passed else 0)



