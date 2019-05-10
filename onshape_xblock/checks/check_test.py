from onshape_xblock.check_imports import *


class CheckTest(CheckBase):

    failure_message_template = ""

    def __init__(self, test_param="optional"):
        self.test_param=test_param
        super(CheckTest, self).__init__(name="Testing",
                                        onshape_element="https://cad.onshape.com/documents/cca81d10f239db0db9481e6f/v/ca51b7554314d6aab254d2e6/e/69c9eedda86512966b20bc90"
                                        )

    def execute_check(self):
        pass
