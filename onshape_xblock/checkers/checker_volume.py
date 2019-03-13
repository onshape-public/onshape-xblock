from onshape_xblock.checkers.checker_base import CheckerBase

class ConstraintVolume():
    def __init__(self, part_number):
        self.part_number=part_number

class CheckerVolume(CheckerBase):
    def __init__(self,
                failure_message="Your part's volume of {volume} is incorrect. It should be between {min_volume} and {max_volume}. {points}/{max_points}",
                 constraints=ConstraintVolume(0),
                 points=1):

        super(CheckerVolume, self).__init__(name="Check Volume",
                                            constraints=constraints,
                                            failure_message=failure_message,
                                            points=points)


