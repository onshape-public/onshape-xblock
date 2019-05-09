from onshape_xblock.check_imports import *


class CheckFeatureList(CheckBase):
    """A feature list check
    Check whether a feature list is as expected. """
    
    feature_type_key = "feature_type"
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
                        "description": "note that a sketch has a feature type of 'newSketch'",
                        "type": "string",
                        "default": "extrude"
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

        self.actual_feature_count = len(features)
        if self.actual_feature_count != self.target_feature_count:
            self.failure_reason = "incorrect number of features"
            self.passed = False
            return

        check_evaluation_list = []
        for feature_target, feature_actual in zip(self.feature_list_target, features):
            check_evaluation_list.append(self.check_feature(feature_target, self.massage_feature(feature_actual)))
        self.passed = all([r == {} for r in check_evaluation_list])

    @staticmethod
    def massage_feature(feature_deserialized):
        return {
            CheckFeatureList.feature_type_key: feature_deserialized["message"]["featureType"]
        }

    @staticmethod            
    def check_feature(feature_target, feature_actual):
        result = {}
        feature_target_type = feature_target[CheckFeatureList.feature_type_key]
        feature_actual_type = feature_actual[CheckFeatureList.feature_type_key]
        if not feature_actual_type == feature_target_type:
            result["failure_reason"] = "feature_type_mismatch"
            result["actual_type"] = feature_actual_type
            result["target_type"] = feature_target_type
        return result