from myxblock.utility import prepopulate_json
import os

def test_prepopulate_json():
    d = {"type":"test_type", "test_metatype": {"type":"inner_test_type"}}
    this_file_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(this_file_path, "json_templates")
    d_populated = prepopulate_json(d, path)
    assert d_populated == {'a': 'test! This is a simple test.', 'test_metatype': {'type': 'inner_test_type', 'another_attr':3}, 'type': 'test_type', 'test_metatype_list':[{'type':'inner_test_type', 'another_attr':3}]}