from abc import abstractmethod

from onshape_xblock.checkers.checker_base import CheckerBase

class CheckerTest(CheckerBase):
    def __init__(self, test_param):
        self.test_param=test_param
        super(CheckerTest, self).__init__()

    @abstractmethod
    def check(self, url):
        return NotImplemented
