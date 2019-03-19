from .utility import  u, quantify, parse_url


class Checker:
    """The Checker contains a number of check_ functions. Check functions provide validation checks for a given
    document/element. A check is made based on the question type.
    For example, a volume question type will always call the "check_volume" function defined. Check functions need to at
    the very least provide a dictionary containing a boolean under the key "correct" to indicate whether or not the
    user satisfied the check. Other common response keys are "message", "actions", etc..."""

    def __init__(self, client):
        """The client provides the connection to the Onshape Servers in order to validate the request. Constraints
        are the constraints for a correct answer for the current xblock. They are a dictionary as defined in the
        particular check function."""
        self.client = client

    def check_guess(self, guess):
        # parse the guess url into the constituent components.
        guess.update(parse_url(guess["url"]))
        self.guess = guess

    def check(self, check):
        """Perform the correct check for the stipulated check_type."""

        checker_function = getattr(self, "check_" + check["type"])
        return checker_function(check)

    def check_volume(self, check):

        # Get and set values
        constraints = check["constraints"]
        response = {}
        min_volume = quantify(constraints["min"], default_units=u.m ** 3)
        max_volume = quantify(constraints["max"], default_units=u.m ** 3)
        part_number = check["constraints"]['part_number']
        part_id = self.get_part_id(part_number)
        mass_properties = self.get_mass_properties(part_id)
        volume = quantify(mass_properties['bodies'][part_id]['volume'][0], default_units=u.m ** 3)

        # To allow all checks to throw an error, they need to be implemented individually like this:
        c = []
        c.append(min_volume < volume)
        c.append(volume < max_volume)

        # Make the check
        response["correct"] = all(c)

        # If the response is incorrect, give the formatted failure message.
        if not response["correct"]:
            response["points"] = 0
            response["message"] = constraints["failure_message"].format(volume=volume.to(min_volume.units),
                                                                        min_volume=min_volume,
                                                                        max_volume=max_volume,
                                                                        max_points=check["points"],
                                                                        points=response["points"]
                                                                        )
        return response

    def check_mass(self, check):

        # Get and test the mass
        constraints = check["constraints"]
        response = {}
        min_mass = quantify(constraints["min"], default_units=u.kg)
        max_mass = quantify(constraints["max"], default_units=u.kg)
        part_number = check["constraints"]['part_number']
        part_id = self.get_part_id(part_number)
        mass_properties = self.get_mass_properties(part_id)
        mass = quantify(mass_properties['bodies'][part_id]['mass'][0], default_units=u.kg)

        # To allow all checks to throw an error, they need to be implemented individually like this:
        c = []
        c.append(min_mass < mass)
        c.append(mass < max_mass)

        response["correct"] = all(c)

        # If the response is incorrect, give the formatted failure message.
        if not response["correct"]:
            response["points"] = 0
            response["message"] = constraints["failure_message"].format(mass=mass,
                                                                        min_mass=min_mass,
                                                                        max_mass=max_mass,
                                                                        max_points=check["points"],
                                                                        points=response["points"]
                                                                        )
        return response

    def check_center_of_mass(self, check):

        # Get and test the mass
        constraints = check["constraints"]
        tolerance = quantify(constraints['tolerance'], default_units=u.m)
        response = {}
        target_centroid = [quantify(x, default_units=u.m) for x in constraints["target_centroid"]]
        part_number = check["constraints"]['part_number']
        part_id = self.get_part_id(part_number)
        mass_properties = self.get_mass_properties(part_id)
        guess_centroid = [quantify(x, default_units=u.m) for x in
                          mass_properties['bodies'][part_id]['centroid'][0:3]]

        # To allow all checks to throw an error, they need to be implemented individually like this:
        c = []
        for x, target in zip(guess_centroid, target_centroid):
            c.append(x < target + tolerance)
            c.append(x > target - tolerance)

        response["correct"] = all(c)

        # If the response is incorrect, give the formatted failure message.
        if not response["correct"]:
            response["points"] = 0
            response["message"] = constraints["failure_message"].format(
                target_centroid=str(",".join([str(x) for x in target_centroid])),
                guess_centroid=str(",".join([str(x) for x in guess_centroid])),
                tolerance=tolerance,
                max_points=check["points"],
                points=response["points"]
            )
        return response

    def check_part_count(self, check):

        # Get and test the mass
        constraints = check["constraints"]
        response = {}
        part_count_check = constraints["part_count"]
        part_count_actual = len(self.get_parts())

        response["correct"] = part_count_actual == part_count_check

        # If the response is incorrect, give the formatted failure message.
        if not response["correct"]:
            response["points"] = 0
            response["message"] = constraints["failure_message"].format(part_count_check=part_count_check,
                                                                        part_count_actual=part_count_actual,
                                                                        max_points=check["points"],
                                                                        points=response["points"]
                                                                        )
        return response

    def check_feature_list(self, check):

        constraints = check["constraints"]
        response = {}
        feature_type_target_list = constraints["feature_type_list"]
        feature_type_actual_list = [t['message']['featureType'] for t in self.get_features()['features']]

        # First check the feature list length.
        if len(feature_type_target_list) != len(feature_type_actual_list):
            response["correct"] = False
            # If the response is incorrect, set the points to 0.
            if not response["correct"]:
                response["points"] = 0
                response["message"] = constraints["count_failure_message"].format(
                    count_expected=len(feature_type_target_list),
                    count_actual=len(feature_type_actual_list),
                    max_points=check["points"],
                    points=response["points"]
                )
            return response
        # Check the feature types one by one:
        else:
            # true/false list of type checks
            c = [t == a for t, a in zip(feature_type_target_list, feature_type_actual_list)]
            # Indices of failed type checks
            c_i = [i for i, x in enumerate(c) if not x]

            response["correct"] = all(c)
            # If the response is incorrect, set the points to 0.
            if not response["correct"]:
                response["points"] = 0
                response["message"] = constraints["type_failure_message"].format(
                    failed_feature_type_count=c_i[0] + 1,
                    feature_type_expected=feature_type_target_list[c_i[0]],
                    feature_type_actual=feature_type_actual_list[c_i[0]],
                    max_points=check["points"],
                    points=response["points"]
                )
            return response

    def check_configuration(self, check):

        # Map from BT config types to user-facing type names:
        map = {"BTMConfigurationParameterEnum": {"type": "List", "entry_name": "row"}, "BTMConfigurationParameterQuantity": {"type": "Variable", "entry_name": "usage"},
         "BTMConfigurationParameterBoolean": {"type":"Checkbox", "entry_name": "features"}}

        # Get and test the mass
        constraints = check["constraints"]
        response = {}
        configuration_target_list = constraints["configuration_list"]
        config = self.get_configuration()

        # Build the configuration list
        configuration_actual_list = []
        for config in config['configurationParameters']:
            d = map[config['typeName']]
            if d["type"] == "List":
                d["row_count"] = len(config['message']["options"])
            configuration_actual_list.append(d)

        # Check the feature types one by one:

        # true/false list of type checks
        c = [t['type'] == a['type'] for t, a in zip(configuration_target_list, configuration_actual_list)]
        # Indices of failed type checks
        c_i = [i for i, x in enumerate(c) if not x]

        response["correct"] = all(c)
        # If the response is incorrect, set the points to 0.
        if not response["correct"]:
            response["points"] = 0
            response["message"] = constraints["type_failure_message"].format(
                config_type_expected=configuration_target_list[c_i[0]]["type"],
                config_type_actual=configuration_actual_list[c_i[0]]["type"],
                max_points=check["points"],
                points=response["points"]
                )
        return response

    def get_part_id(self, part_number):
        """Return the partId of the part specified by "part_number" at the part specified by did, wvm, eid"""
        return self.get_parts()[part_number]['partId']

    def get_parts(self):
        """Return the partId of the part specified by "part_number" at the part specified by did, wvm, eid"""
        res = self.client.parts.get_parts_in_partstudio(self.guess['did'], self.guess['wvm'], self.guess['eid'])
        res.raise_for_status()
        return res.json()

    def get_mass_properties(self, part_id):
        res = self.client.parts.get_mass_properties(self.guess["did"], self.guess['wvm_pair'], self.guess["eid"],
                                                    part_id)
        res.raise_for_status()
        return res.json()

    def get_features(self):
        res = self.client.part_studios.get_features(self.guess['did'], self.guess['wvm_pair'],
                                                    self.guess['eid'])
        res.raise_for_status()
        return res.json()

    def get_configuration(self):
        res = self.client.elements_api.get_configuration3(self.guess['did'], self.guess['wvm_pair'], self.guess['wvm'],
                                                         self.guess['eid'], _preload_content=False)
        res.raise_for_status()
        return res.json()
