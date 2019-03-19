
from onshape_xblock.checks.check_base import CheckBase

class CheckTest(CheckBase):
    def __init__(self, test_param="optional"):
        self.test_param=test_param
        super(CheckTest, self).__init__()

