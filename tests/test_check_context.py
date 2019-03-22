from onshape_xblock.check_context import CheckContext
from onshape_xblock.checks.check_volume import CheckVolume


def test_check_creation(configured_cube_version):
    check_init_args = [{"type": "check_volume"}]
    check_context = CheckContext(onshape_element=configured_cube_version, check_init_list=check_init_args)
    assert isinstance(check_context.checks[0], CheckVolume)


def test_check_volume(configured_cube_version, checker_function):
    check_init_args_fail = {"type": "check_volume", "min_volume": "1 meter**3", "max_volume": "3 meter**3", "part_number": 0}
    feedback = checker_function(configured_cube_version, check_init_args_fail)
    assert not feedback["passed"]
    assert feedback["message"] != ""
    check_init_args_pass = {"type": "check_volume", "min_volume": "0 meter**3", "max_volume": "1 meter**3", "part_number": 0}
    feedback2 = checker_function(configured_cube_version, check_init_args_pass)
    assert feedback2["passed"]
    assert feedback2["message"] == ""


def test_check_center_of_mass(configured_cube_version, checker_function):
    check_init_args_fail = {"type": "check_center_of_mass", "target_centroid": [0,0,1], "tolerance": "0.3", "part_number": 0}
    feedback = checker_function(configured_cube_version, check_init_args_fail)
    assert not feedback["passed"]
    assert feedback["message"]
    check_init_args_pass = {"type": "check_center_of_mass", "target_centroid": [0, 0, 0], "tolerance": "0.3",
                            "part_number": 0}
    feedback2 = checker_function(configured_cube_version, check_init_args_pass)
    assert feedback2["passed"]
    assert feedback2["message"] == ""
    check_init_args_pass = {"type": "check_center_of_mass", "target_centroid": [0, 0, 0.2], "tolerance": "0.3",
                            "part_number": 0}
    feedback3 = checker_function(configured_cube_version, check_init_args_pass)
    assert feedback3["passed"]
    assert feedback3["message"] == ""

def test_check_configuration(configured_cube_version, checker_function):
    check_init_args_pass = {"type": "check_configuration", "configuration_target_list": [{"type":"List", "row_count":3},{"type": "Variable", "params_count": 4}]}
    feedback = checker_function(configured_cube_version, check_init_args_pass)
    assert feedback["passed"]
    # Fail with row_count
    check_init_args_fail = {"type": "check_configuration",
                            "configuration_target_list": [{"type": "List", "row_count": 4},
                                                          {"type": "Variable", "params_count": 4}]}
    feedback = checker_function(configured_cube_version, check_init_args_fail)
    assert not feedback["passed"]

def test_check_feature_list(configured_cube_version):
    pass

def test_check_mass(configured_cube_version, checker_function):
    check_init_args_fail = {"type": "check_mass", "min_mass": "0 lb", "max_mass": "0.001 lb", "part_number": 0}
    feedback = checker_function(configured_cube_version, check_init_args_fail)
    assert not feedback["passed"]
    assert feedback["message"] != ""
    check_init_args_pass = {"type": "check_mass", "min_mass": "0.038 lb", "max_mass": "0.0381 lb", "part_number": 0}
    feedback2 = checker_function(configured_cube_version, check_init_args_pass)
    assert feedback2["passed"]
    assert feedback2["message"] == ""

def test_check_part_count(configured_cube_version):
    pass