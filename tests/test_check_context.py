from onshape_xblock.check_context import CheckContext
from onshape_xblock.checks.check_volume import CheckVolume


def test_check_creation(configured_cube_version):
    check_init_args = {"type": "check_volume", "onshape_element": configured_cube_version}
    check_context = CheckContext()
    check = check_context.create_check(check_init_args)
    assert isinstance(check, CheckVolume)


def test_check_volumes(configured_cube_version, check_context):
    check_init_args_fail = {"type": "check_volume", "min": "1 meter**3", "max": "3 meter**3",
                       "onshape_element": configured_cube_version, "part_number": 0}
    check = check_context.create_check(check_init_args_fail)
    feedback = check.get_feedback()
    assert not feedback.passed
    assert feedback.message
    check_init_args_pass = {"type": "check_volume", "min": "0 meter**3", "max": "1 meter**3",
                       "onshape_element": configured_cube_version, "part_number": 0}
    check2 = check_context.create_check(check_init_args_pass)
    feedback2 = check2.get_feedback()
    assert check2.feedback.passed
    assert feedback2.message


def test_check_center_of_mass(configured_cube_version, check_context):
    check_init_args_fail = {"type": "check_center_of_mass", "target_centroid": [0,0,1], "tolerance": "0.3", "onshape_element": configured_cube_version, "part_number": 0}
    check = check_context.create_check(check_init_args_fail)
    feedback = check.get_feedback()
    assert not feedback.passed
    assert feedback.message

def test_check_configuration(configured_cube_version):
    pass

def test_check_feature_list(configured_cube_version):
    pass

def test_check_mass(configured_cube_version):
    pass

def test_check_part_count(configured_cube_version):
    pass

def test_check_volume(configured_cube_version):
    pass
