from onshape_xblock.check_imports import *
from onshape_xblock.checks import check_element_type


class CheckFeatureList(CheckBase):
    """A feature list check
    Check whether a feature list is as expected. """
    
    feature_type_key = "feature_type"
    secondary_type_key = "secondary_type"
    feature_list_target_default = [{feature_type_key: "newSketch"}, {feature_type_key: "extrude"}]
    additional_form_properties = {
        "feature_list_target": {
            "type": "array",
            "title": "Target feature list definition",
            "items": {
                "type": "object",
                "title": "Feature",
                "properties": {
                    feature_type_key: {
                        "title": "The feature type (ex. boolean, extrude, etc...)",
                        "description": "note that a sketch has a feature type of 'newSketch'. Also note that assembly "
                                       "mates are specified with 'mate' type here and the mate type, like 'revolute' "
                                       "in the next box.",
                        "type": "string",
                        "default": "extrude"
                    },
                    secondary_type_key: {
                        "title": "The feature subtype for mates (fixed, revolute, etc...)",
                        "description": "Only add here if the feature type is a 'mate' type. Otherwise this field doesn't do anything.",
                        "type": "string",
                        "default": "revolute"
                    }
                }
            }
        }
    }

    def __init__(self,
                 feature_list_target=feature_list_target_default,
                 **kwargs):
        super(CheckFeatureList, self).__init__(name="Check Feature List",
                                          **kwargs)
        self.feature_list_target = feature_list_target
        self.target_feature_count = len(feature_list_target)

    def execute_check(self):
        features = self.get_features()
        self.passed = False

        try:
            check_evaluation_list = self.check_lists(self.feature_list_target, features, self.check_feature)
        except AssertionError as e:
            self.failure_reason = e.message
            return

        if check_evaluation_list == True:
            self.passed = True

    @staticmethod
    def massage_feature(feature_deserialized):
        main_type = feature_deserialized["message"]["featureType"]
        secondary_type = None
        if main_type == "mate":
            secondary_type = feature_deserialized["message"]["parameters"][0]["message"]["value"].lower()
        result = {
            CheckFeatureList.feature_type_key: feature_deserialized["message"]["featureType"]
        }
        if secondary_type:
            result[CheckFeatureList.secondary_type_key] = secondary_type
        return result

    @staticmethod
    def massage_target_feature(target_feature):
        if target_feature[CheckFeatureList.feature_type_key] != 'mate':
            del target_feature[CheckFeatureList.secondary_type_key]

    @staticmethod
    def check_feature(feature_target, feature_actual):
        feature_actual = CheckFeatureList.massage_feature(feature_actual)
        result = {}
        feature_target_type = feature_target[CheckFeatureList.feature_type_key]
        feature_actual_type = feature_actual[CheckFeatureList.feature_type_key]
        if not feature_target == feature_actual:
            result["failure_reason"] = "feature_type_mismatch"
            result["actual_type"] = feature_actual_type
            result["target_type"] = feature_target_type
        return result