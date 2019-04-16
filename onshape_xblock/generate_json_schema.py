"""For generating the list of checks presented to the course designer from the static portions of each check class,
much like how the xblock itself generates the UI."""
from serialize import Serialize
import json, codecs, io
from importlib_resources import read_binary
from pathlib import Path
import os


class GenerateCheckListForm():

    def __init__(self):
        self.form_package = "onshape_xblock.public.json"
        self.form_template_filename = "check_list_form_template.json"
        self.form_output_filename = "check_list_form.json"
        self.form_template = self.get_form_template()
        self.static_check_classes = self.get_static_check_classes()
        self.insert_check_definitions()
        self.insert_check_dependencies()
        self.save_check_form()

    def get_static_check_classes(self):

        # Should this just get all of the modules within the package? Or is this a place we can specify particular values?
        check_name_list = [{"type": "check_volume"},
                           {"type": "check_mass"},
                           {"type": "check_center_of_mass"},
                           {"type": "check_configuration"}]
        check_class_list = Serialize.init_class_list(check_name_list, init_class=False)
        return check_class_list

    def get_form_template(self):
        d = read_binary(self.form_package, self.form_template_filename)
        return json.loads(d)

    def insert_check_definitions(self):
        """Insert/merge the check form definitions. If the value is present in the template, keep it there."""
        for check in self.static_check_classes:
            check_type = check.check_type
            definitions = self.form_template["definitions"]["check_base"]["definitions"]
            if check_type in definitions:
                definitions[check_type].update(check.form_definition)
            else:
                definitions[check_type] = check.form_definition

    def insert_check_dependencies(self):
        """Insert the check dependency if it isn't already there."""
        check_type_to_index = {}
        oneOf = self.form_template["definitions"]["check_base"]["dependencies"]["check_type"]["oneOf"]
        for index, property in enumerate(oneOf):
            check_type = property["properties"]["check_type"]["enum"][0]
            check_type_to_index[check_type] = index
        for check in self.static_check_classes:
            check_type = check.check_type
            if check_type not in check_type_to_index:
                v = {"properties": {
                        "check_type": {
                            "enum": [
                                check_type
                            ]
                        },
                        "additional_args": {
                            "$ref": "#/definitions/check_base/definitions/" + check_type
                        }
                    }}
                oneOf.append(v)

    def save_check_form(self):
        outfile_path = Path(os.getcwd()) / self.form_output_filename

        with io.open(str(outfile_path), 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.form_template, ensure_ascii=False))

        # with open(outfile_path, 'wb') as f:
        #     json.dump(self.form_template, codecs.getwriter('utf-8')(f), ensure_ascii=False)



if __name__ == "__main__":
    thing = GenerateCheckListForm()
