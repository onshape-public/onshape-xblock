import pytest
from onshape_xblock.onshape_url import OnshapeElement
from onshape_xblock.check_context import CheckContext

@pytest.fixture
def configured_cube_version():
    return OnshapeElement("https://cad.onshape.com/documents/cca81d10f239db0db9481e6f/v/39711aea80fd4100faa1b147/e/69c9eedda86512966b20bc90")

@pytest.fixture
def check_context():
    return CheckContext()
