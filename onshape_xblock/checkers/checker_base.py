class CheckerBase(object):
    def __init__(self, name="The checker name", constraints="A constraints object", failure_message="A mesage in case of failure", points=1):
        """Initialize the definition of the check"""
        self.points = points
        self.name = name
        self.constraints = constraints
        self.failure_message = failure_message