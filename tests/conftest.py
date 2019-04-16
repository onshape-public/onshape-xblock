import pytest
from onshape_client.onshape_url import OnshapeElement
from onshape_xblock.check_context import CheckContext

@pytest.fixture
def configured_cube_version():
    return OnshapeElement("https://cad.onshape.com/documents/cca81d10f239db0db9481e6f/v/ca51b7554314d6aab254d2e6/e/69c9eedda86512966b20bc90")

@pytest.fixture
def check_context():
    return CheckContext()

@pytest.fixture
def checker_function(check_context):
    """Returns a helper method to get the feedback given init args and the element itself"""
    def checker(onshape_element, check_init_args):
        check_context.onshape_element = onshape_element
        check = check_context.create_check(check_init_args)
        feedback = check.get_display_feedback()
        return feedback
    return checker
