from onshape_xblock.check_imports import *


class CheckConfiguration(CheckBase):
    """A configuration check

    This configuration check checks whether or not the specified Onshape part has a configuration within the bounds defined. """
    configuration_target_list_default = [{"configuration_type": "List", "row_count": 5},
                                         {"configuration_type": "Variable", "params_count": 5},
                                         {"configuration_type": "Checkbox"}]

    additional_form_properties = {
        "config_target": {
            "type": "array",
            "title": "Target configuration definition",
            "items": {
                "type": "object",
                "title": "Configuration Setting",
                "properties": {
                    "configuration_type": {
                        "title": "The configuration type of this setting",
                        "type": "string",
                        "default": "List",
                        "enum": [
                            "List",
                            "Variable",
                            "Checkbox"
                        ],
                        "uniqueItems": True
                    }
                },
                "dependencies": {
                    "configuration_type": {
                        "oneOf": [
                            {
                                "properties": {
                                    "configuration_type": {
                                        "enum": [
                                            "List"
                                        ]
                                    },
                                    "row_count": {
                                        "type": "string",
                                        "title": "Expected number of rows within this configuration setting"
                                    }
                                }
                            },
                            {
                                "properties": {
                                    "configuration_type": {
                                        "enum": [
                                            "Variable"
                                        ]
                                    },
                                    "param_count": {
                                        "type": "number",
                                        "default": 0,
                                        "title": "Expected number of dependencies on this variable"
                                    }
                                }
                            },
                            {
                                "properties": {
                                    "configuration_type": {
                                        "enum": [
                                            "Checkbox"
                                        ]
                                    },
                                    "default": {
                                        "type": "boolean",
                                        "title": "Expected default for this setting (true if checked)"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    }

    map = {"BTMConfigurationParameterEnum": "List",
           "BTMConfigurationParameterQuantity": "Variable",
           "BTMConfigurationParameterBoolean": "Checkbox"}

    def __init__(self,
                 configuration_target_list=configuration_target_list_default,
                 **kwargs):
        super(CheckConfiguration, self).__init__(name="Check Configuration", **kwargs)
        self.configuration_target_list = configuration_target_list
        self.config_type_expected = None
        self.config_type_actual = None
        self.config_error_index = None

    def execute_check(self):
        configuration_target_list = self.configuration_target_list
        configs = self.get_configuration()['configurationParameters']

        if len(configuration_target_list) != len(configs):
            self.passed = False
            self.failure_reason = "params_length_mismatch"
            self.failure = {"target_length": len(configuration_target_list)}
            return

        # Build the configuration list
        check_evaluation_list = []
        for config_target, config_actual in zip(configuration_target_list, configs):
            check_evaluation_list.append(self.check_config_var(config_target, config_actual))

        self.passed = all([r == {} for r in check_evaluation_list])

    @staticmethod
    def check_config_var(config_target, config_actual):
        """Takes in a target config definition, and an actual config, and returns {} if actual matches target specs,
        and otherwise returns {"reason":<failure_reason>}, where other keys in the dict are present depending on which
        type of failure it is. For example, this may be a response: {"reason":"config_type_mismatch", "target_type":
        "List", "actual_type":"Variable"}"""
        result = {}
        config_target_type = config_target["configuration_type"]
        config_actual_type = CheckConfiguration.map[config_actual['typeName']]

        # Check for configuration type mismatch
        if not config_target_type == config_actual_type:
            result["failure_reason"] = "config_type_mismatch"
            result["actual_type"] = config_actual_type
            result["target_type"] = config_target_type
            # short circuit if types don't match
            return result

        # Check for type constraints mismatch
        if config_target_type == "List":
            if not config_target["row_count"] == len(config_actual['message']["options"]):
                result["failure_reason"] = "bad_row_count"
                result["desired_row_count"] = config_target["row_count"]
                result["actual_row_count"] = len(config_actual['message']["options"])
        elif config_target_type == "Variable":
            # Could check for ranges/defaults in the future.
            pass
        elif config_target_type == "Checkbox":
            # Could check for default in the future.
            pass
        else:
            raise TypeError("{} is not a proper configuration type. The acceptable types are List, Variable and "
                            "Checkbox.")
        return result
