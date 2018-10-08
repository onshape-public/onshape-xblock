from myxblock.checker import Checker
import pytest
from testpackage.onshape import Onshape
from myxblock._keys import keys

# This is V1 of Pipe PartStudio
guess = {
    "url": "https://demo-c.dev.onshape.com/documents/6c0a84d1dc511212535631f1/w/9396160c6b63012b7f2d6da9/e/f505e39c4f3cb163cd9deb00"}


@pytest.fixture
def checker():
    client = Onshape(access=keys["access"], secret=keys["secret"], target=keys["target"])
    return Checker(client, guess)


def test_check_part_count(checker):
    check = {
        "type": "center_of_mass",
        "points": 1,
        "constraints": {
            "part_count": 1,
            "failure_message": "Your PartStudio has {part_count_actual} parts but should have {part_count_check} parts. {points}/{max_points}"
        }
    }
    assert checker.check_part_count(check)["correct"]


def test_check_volume(checker):
    check = {
        ''"type": "volume",
        "points": 1,
        "constraints": {
            "min": "9 in**3",
            "max": "10 in**3",
            "part_number": 0,
            "failure_message": "Your part's volume of {volume} is incorrect. It should be between {min_volume} and {max_volume}. {points}/{max_points}"
        }
    }
    assert checker.check_volume(check)["correct"]


def test_check_configuration(checker):
    check = {
        "type": "feature_list",
        "points": 1,
        "constraints": {
            "configuration_list": [{"type": "List", "row_count": 2}, {"type": "Variable"}, {"type": "Variable"},
                                   {"type": "Checkbox"}],
            "type_failure_message": "Your PartStudio has a {config_type_actual} in the configuration where it should have a {config_type_expected} configuration type.",
            "count_failure_message": "Your PartStudio configuration's {config_type} should have {config_entry_count_expected}, but currently only has {config_entry_count_actual} {config_type_entries}."
        }
    }
    assert checker.check_configuration(check)["correct"]