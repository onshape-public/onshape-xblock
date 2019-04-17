from onshape_xblock.utility import prepopulate_json, quantify, u, merge_d
from onshape_xblock.serialize import Serialize
import os


def test_prepopulate_json():
    d = {"type":"test_type", "test_metatype": {"type":"inner_test_type"}, 'test_metatype':[{'type':'inner_test_type'}]}
    this_file_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(this_file_path, "json_templates")
    d_populated = prepopulate_json(d, path)
    assert d_populated == {'a': 'test! This is a simple test.', 'test_metatype': {'type': 'inner_test_type', 'another_attr':3}, 'type': 'test_type', 'test_metatype':[{'type':'inner_test_type', 'another_attr':3}]}


def test_quantify():
    assert quantify(0) == 0 * u.meter
    assert quantify(1) == 1 * u.meter
    assert quantify("0") == 0 * u.meter
    assert quantify("1") == 1 * u.meter
    assert quantify(0, default_units=u.kg) == 0 * u.kg
    assert quantify(1, default_units=u.kg) == 1 * u.kg
    assert quantify("1", default_units=u.kg) == 1 * u.kg
    assert quantify(1, default_units=u.kg, tolerance=0.01)
    assert quantify("3 meter") == 3*u.m
    assert quantify("3 meter**3") == 3 * u.m ** 3


def test_parse_url():
    from onshape_client.onshape_url import OnshapeElement
    onshape_url = OnshapeElement("https://cad.onshape.com/documents/cca81d10f239db0db9481e6f/v/39711aea80fd4100faa1b147/e/69c9eedda86512966b20bc90")
    assert onshape_url.did == "cca81d10f239db0db9481e6f"
    assert onshape_url.wvm == "v"
    assert onshape_url.wvmid == "39711aea80fd4100faa1b147"
    assert onshape_url.eid == "69c9eedda86512966b20bc90"
    assert onshape_url.get_url() == "https://cad.onshape.com/documents/cca81d10f239db0db9481e6f/v/39711aea80fd4100faa1b147/e/69c9eedda86512966b20bc90"
    assert onshape_url.get_microversion_url() == "https://cad.onshape.com/documents/cca81d10f239db0db9481e6f/v/39711aea80fd4100faa1b147/m/4b471df5f9c9590b2a2496cf/e/69c9eedda86512966b20bc90"
    onshape_element_long_form = OnshapeElement("https://cad.onshape.com/documents/cca81d10f239db0db9481e6f/w/80887f5994121967bf4d59a6/m/aa1867247974aa51baf6da3d/e/69c9eedda86512966b20bc90")
    assert onshape_element_long_form.optional_microversion == "aa1867247974aa51baf6da3d"
