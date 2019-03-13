from onshape_xblock.utility import prepopulate_json, quantify, u, parse_url
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
    assert quantify(1, default_units=u.kg, tolerance=0.01)

def test_parse_url():
    assert parse_url("https://demo - c.dev.onshape.com/documents/bbf2f04e5541d6ce51dae74a/w"
                     "/ef55e51efbb9f35e80894316/e/7fbd104f45e32b7184862b9b") == {'did': 'bbf2f04e5541d6ce51dae74a',
                                                                                 'eid': '7fbd104f45e32b7184862b9b',
                                                                                 'wvm': 'ef55e51efbb9f35e80894316',
                                                                                 'wvm_pair': ('w', 'ef55e51efbb9f35e80894316'),
                                                                                 'wvm_type': 'w'}



def test_serialization():
    from onshape_xblock.checkers.checker_test import CheckerTest
    from onshape_xblock.checkers.checker_volume import CheckerVolume
    my_instance = CheckerTest("This is a test")
    my_serialization = Serialize.serialize(my_instance)
    my_second_instance = Serialize.deserialize(my_serialization)
    assert(isinstance(my_second_instance, CheckerTest))

    a_serializable_string = """{"py/object": "onshape_xblock.checkers.checker_volume.CheckerVolume", "points": 1, "failure_message": "Your part's volume of {volume} is incorrect. It should be between {min_volume} and {max_volume}. {points}/{max_points}", "name": "Check Volume", "constraints": {"py/object": "onshape_xblock.checkers.checker_volume.ConstraintVolume", "part_number": 0}}"""

    volume_deserialized = Serialize.deserialize(a_serializable_string)
    assert (isinstance(volume_deserialized, CheckerVolume))