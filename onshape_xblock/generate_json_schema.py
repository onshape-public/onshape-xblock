"""For generating the list of checks presented to the course designer from the static portions of each check class,
much like how the xblock itself generates the UI."""
from serialize import Serialize
import json, codecs, io
from importlib_resources import read_text, path
from pathlib import Path
import os
import checks
import pkgutil
import inspect
from onshape_xblock.public import json as json_dir


class GenerateCheckListForm():

    def __init__(self):
        self.form_template_filename = "check_list_form_template.json"
        self.form_output_filename = "check_list_form.json"
        self.form_template = self.get_form_template()
        self.set_static_check_classes()
        self.generate_json_schema()
        self.save_check_form()

    def set_static_check_classes(self):
        check_name_list = [{"check_type" : name} for _, name, _ in pkgutil.iter_modules([os.path.dirname(inspect.getfile(checks))])]
        check_class_list = Serialize.init_class_list(check_name_list, init_class=False)

        self.static_check_classes = {class_type["check_type"]: class_stuff for class_type, class_stuff in zip(check_name_list, check_class_list)}

    def generate_json_schema(self):
        for check_type, check in self.static_check_classes.items():
            self.insert_check_dependencies(check_type)
            self.insert_check_definitions(check_type, check)
            self.insert_check_options(check_type)

    def get_form_template(self):
        d = read_text(json_dir, self.form_template_filename)
        return json.loads(d)

    def insert_check_definitions(self, check_type, check):
        """Insert/merge the check form definitions. If the value is present in the template, keep it there."""
        definitions = self.form_template["definitions"]["check_base"]["definitions"]
        definitions[check_type] = check.form_definition()

    def insert_check_dependencies(self, check_type):
        """Insert the check dependency."""
        oneOf = self.form_template["definitions"]["check_base"]["dependencies"]["check_type"]["oneOf"]
        v = {"properties": {
                "check_type": {
                    "enum": [
                        check_type
                    ]
                },
                "check_parameters": {
                    "$ref": "#/definitions/check_base/definitions/" + check_type
                }
            }}
        oneOf.append(v)

    def insert_check_options(self, check_type):
        """Insert the checks into the enum list"""
        enum = self.form_template["definitions"]["check_base"]["properties"]["check_type"]["enum"]
        enum.append(check_type)

    def save_check_form(self):

        with path(json_dir, self.form_output_filename) as p:
            with open(str(p), 'w') as f:
                f.write(json.dumps(self.form_template, ensure_ascii=False))



if __name__ == "__main__":
    thing = GenerateCheckListForm()
