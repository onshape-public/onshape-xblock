from myxblock.utility import prepopulate_json, quantify, u, parse_url
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
    assert quantify(1, default_units=u.kg, tolerance=0.01)

def test_parse_url():
    assert parse_url("https://demo - c.dev.onshape.com/documents/bbf2f04e5541d6ce51dae74a/w"
                     "/ef55e51efbb9f35e80894316/e/7fbd104f45e32b7184862b9b") == {'did': 'bbf2f04e5541d6ce51dae74a',
                                                                                 'eid': '7fbd104f45e32b7184862b9b',
                                                                                 'wvm': 'ef55e51efbb9f35e80894316',
                                                                                 'wvm_pair': ('w', 'ef55e51efbb9f35e80894316'),
                                                                                 'wvm_type': 'w'}