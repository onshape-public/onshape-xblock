from serialize import Serialize
import json
from pathlib import Path
from pkgutil import get_data


def get_check_fields():

    # Should this just get all of the modules within the package? Or is this a place we can specify particular values?
    check_name_list = [{"type": "check_volume"},
                       {"type": "check_mass"},
                       {"type": "check_center_of_mass"},
                       {"type": "check_configuration"},
                       {"type": "check_base"}]
    check_class_list = Serialize.init_class_list(check_name_list, init_class=False)
    return check_class_list

def generate_form():
    d = get_data("onshape_xblock.public.json", "check_list_form")
    json.loads(d)

if __name__ == "__main__":
    print(generate_form())
    print get_check_fields()