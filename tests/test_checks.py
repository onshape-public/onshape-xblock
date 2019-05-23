from onshape_xblock.check_context import CheckContext
from onshape_xblock.checks.check_volume import CheckVolume


def test_check_creation(configured_cube_version):
    check_init_args = [{"check_type": "check_volume"}]
    check_context = CheckContext(onshape_element=configured_cube_version, check_init_list=check_init_args)
    assert isinstance(check_context.checks[0], CheckVolume)


def test_check_volume(configured_cube_version, checker_function):
    check_init_args_fail = {"check_type": "check_volume", "check_parameters": { "min_volume": "1 meter**3", "max_volume": "3 meter**3", "part_number": 0}}
    feedback = checker_function(configured_cube_version, check_init_args_fail)
    assert not feedback["passed"]
    assert feedback["message"]
    check_init_args_pass = {"check_type": "check_volume", "min_volume": "0 meter**3", "max_volume": "1 meter**3", "part_number": 0}
    feedback2 = checker_function(configured_cube_version, check_init_args_pass)
    assert feedback2["passed"]
    assert feedback2["message"]


def test_check_center_of_mass(configured_cube_version, checker_function):
    check_init_args_fail = {"check_type": "check_center_of_mass", "target_centroid": [0,0,1], "tolerance": "0.3", "part_number": 0}
    feedback = checker_function(configured_cube_version, check_init_args_fail)
    assert not feedback["passed"]
    assert feedback["message"]
    check_init_args_pass = {"check_type": "check_center_of_mass", "target_centroid": [0, 0, 0], "tolerance": "0.3",
                            "part_number": 0}
    feedback2 = checker_function(configured_cube_version, check_init_args_pass)
    assert feedback2["passed"]
    assert feedback2["message"]
    check_init_args_pass = {"check_type": "check_center_of_mass", "target_centroid": [0, 0, 0.2], "tolerance": "0.3",
                            "part_number": 0}
    feedback3 = checker_function(configured_cube_version, check_init_args_pass)
    assert feedback3["passed"]
    assert feedback3["message"]

def test_check_configuration(configured_cube_version, checker_function):
    check_init_args_pass = {"check_type": "check_configuration", "configuration_target_list": [{"configuration_type":"List", "row_count":3},{"configuration_type": "Variable", "params_count": 4}]}
    feedback = checker_function(configured_cube_version, check_init_args_pass)
    assert feedback["passed"]
    # Fail with row_count
    check_init_args_fail = {"check_type": "check_configuration",
                            "configuration_target_list": [{"configuration_type": "List", "row_count": 4},
                                                          {"configuration_type": "Variable", "params_count": 4}]}
    feedback = checker_function(configured_cube_version, check_init_args_fail)
    assert not feedback["passed"]

def test_check_feature_list(configured_cube_version, checker_function):
    check_init_args_pass = {"check_type": "check_feature_list", "feature_list_target": [{"feature_type": "newSketch"}, {"feature_type": "extrude"}, {"feature_type": "fillet"}, {"feature_type": "chamfer"}]}
    feedback = checker_function(configured_cube_version, check_init_args_pass)
    assert feedback["passed"]
    check_init_args_fail_type = {"check_type": "check_feature_list", "feature_list_target": [{"feature_type": "extrude"}, {"feature_type": "extrude"}, {"feature_type": "fillet"}, {"feature_type": "chamfer"}]}
    feedback = checker_function(configured_cube_version, check_init_args_fail_type)
    assert not feedback["passed"]
    check_init_args_fail_length = {"check_type": "check_feature_list", "feature_list_target": [{"feature_type": "extrude"}, {"feature_type": "fillet"}, {"feature_type": "chamfer"}]}
    feedback = checker_function(configured_cube_version, check_init_args_fail_length)
    assert not feedback["passed"]

def test_check_feature_list_assembly(configured_cube_version, checker_function):
    check_init_args_pass = {"check_type": "check_feature_list", "feature_list_target": [{"feature_type": "newSketch"}, {"feature_type": "extrude"}, {"feature_type": "fillet"}, {"feature_type": "chamfer"}]}
    feedback = checker_function(configured_cube_version, check_init_args_pass)
    assert feedback["passed"]
    check_init_args_fail_type = {"check_type": "check_feature_list", "feature_list_target": [{"feature_type": "extrude"}, {"feature_type": "extrude"}, {"feature_type": "fillet"}, {"feature_type": "chamfer"}]}
    feedback = checker_function(configured_cube_version, check_init_args_fail_type)
    assert not feedback["passed"]
    check_init_args_fail_length = {"check_type": "check_feature_list", "feature_list_target": [{"feature_type": "extrude"}, {"feature_type": "fillet"}, {"feature_type": "chamfer"}]}
    feedback = checker_function(configured_cube_version, check_init_args_fail_length)
    assert not feedback["passed"]

def test_check_mass(configured_cube_version, checker_function):
    check_init_args_fail = {"check_type": "check_mass", "min_mass": "0 lb", "max_mass": "0.001 lb", "part_number": 0}
    feedback = checker_function(configured_cube_version, check_init_args_fail)
    assert not feedback["passed"]
    assert feedback["message"]
    check_init_args_pass = {"check_type": "check_mass", "min_mass": "0.038 lb", "max_mass": "0.0381 lb", "part_number": 0}
    feedback2 = checker_function(configured_cube_version, check_init_args_pass)
    assert feedback2["passed"]
    assert feedback2["message"]

def test_check_part_count(configured_cube_version, checker_function):
    check_init_args_pass = {"check_type": "check_part_count", "target_part_count": 1}
    feedback = checker_function(configured_cube_version, check_init_args_pass)
    assert feedback["passed"]
    check_init_args_fail = {"check_type": "check_part_count", "target_part_count": 3}
    feedback = checker_function(configured_cube_version, check_init_args_fail)
    assert not feedback["passed"]

def test_check_element_type(configured_cube_version, checker_function):
    check_init_args_pass = {"check_type": "check_element_type", "expected_element_type": "Partstudio"}
    feedback = checker_function(configured_cube_version, check_init_args_pass)
    assert feedback["passed"]
    check_init_args_pass = {"check_type": "check_element_type", "expected_element_type": "Assembly"}
    feedback = checker_function(configured_cube_version, check_init_args_pass)
    assert not feedback["passed"]

