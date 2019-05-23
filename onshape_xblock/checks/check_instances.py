from onshape_xblock.check_imports import *


class CheckInstances(CheckBase):
    """An assembly instances check

    This assembly instances checks determines how many and what type the instances are. """

    instance_type_key = "instance_type"
    instance_type_target_default = [{instance_type_key: "Part"}, {instance_type_key: "Part"}]
    additional_form_properties = {
        "instance_list_target": {
            "type": "array",
            "title": "Target instance list definition",
            "items": {
                "type": "object",
                "title": "Instance",
                "properties": {
                    instance_type_key: {
                        "title": "The instance type (ex. Part, Assembly, etc...)",
                        "description": "note that a sketch has a feature type of 'newSketch'. Also note that assembly "
                                       "mates are specified with 'mate' type here and the mate type, like 'revolute' "
                                       "in the next box.",
                        "type": "string",
                        "default": "Part"
                    }
                }
            }
        }
    }

    def __init__(self,
                 instance_list_target=instance_type_target_default,
                 **kwargs):
        super(CheckInstances, self).__init__(name="Check Instances",
                                          **kwargs)
        self.instance_list_target = instance_list_target

    def execute_check(self):
        instances = self.get_instances()
        self.passed = False

        try:
            check_evaluation_list = self.check_lists(self.instance_list_target, instances, self.compare_instances)
        except AssertionError as e:
            self.failure_reason = e.message
            return

        if check_evaluation_list == True:
            self.passed = True

    @staticmethod
    def massage_instance(instance_deserialized):
        return {
            CheckInstances.instance_type_key: instance_deserialized['type']
        }

    @staticmethod
    def compare_instances(instance_target, instance_actual):
        result = {}
        instance_actual = CheckInstances.massage_instance(instance_actual)
        instance_target_type = instance_target[CheckInstances.instance_type_key]
        instance_actual_type = instance_actual[CheckInstances.instance_type_key]
        if not instance_target_type == instance_actual_type:
            result["failure_reason"] = "instance_type_mismatch"
            result["actual_type"] = instance_actual_type
            result["target_type"] = instance_target_type
        return result