from onshape_xblock.serialize import Serialize
from onshape_xblock.checks.check_test import CheckTest
from onshape_xblock.checks.check_volume import CheckVolume

def test_serialization():

    my_instance = CheckTest("This is a test")
    my_serialization = Serialize.serialize(my_instance)
    my_second_instance = Serialize.deserialize(my_serialization)
    assert(isinstance(my_second_instance, CheckTest))

    a_serializable_string = """{"py/object": "onshape_xblock.checks.checker_volume.CheckVolume", "points": 1, "failure_message": "Your part's volume of {volume} is incorrect. It should be between {min_volume} and {max_volume}. {points}/{max_points}", "name": "Check Volume", "constraints": {"py/object": "onshape_xblock.checks.checker_volume.ConstraintVolume", "part_number": 0}}"""

    volume_deserialized = Serialize.deserialize(a_serializable_string)
    assert (isinstance(volume_deserialized, CheckVolume))

def test_init_checker_list():
    checker_list = \
        [
            {"type":"check_volume", "min":"45"},
            {"type":"check_test", "test_param":"Look at me!"},
        ]

    response = Serialize.init_class_list(checker_list)
    assert isinstance(response[0], CheckVolume)
