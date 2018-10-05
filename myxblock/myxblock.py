"""Onshape XBlock.

How we handle the UI:

We always pass an up to date dictionary, d, to the frontend. The frontend is somewhat functional - it
only holds state in that the DOM is set a certain way. It never holds state that is not visible to the user. And when a
frontend function is called, it is responsible for exactly synchronizing the frontend with the current dictionary passed
from the backend. Therefore all calls from the frontend roughly look like: user_action_taken_handler(action_context)
and the corresponding return will always be self.d - in otherwords all of the context that could possibly be needed to
show visuals. Anything that needs to be hidden from the user should not go in d."""

import pkg_resources
import posixpath
import requests
from testpackage.onshape import Onshape
from urlparse import urlparse
from xblock.core import XBlock
from xblock.fields import Boolean, Float, Integer, Scope, String, Dict
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin
from _keys import keys
import json
import os, sys
import inspect
from .utility import parse_url, prepopulate_json, quantify, u
import pint

loader = ResourceLoader(__name__)  # pylint: disable=invalid-name


class MyXBlock(StudioEditableXBlockMixin, XBlock):
    """
    A generic Onshape XBlock that can be configured to validate all sorts of parts of an onshape model.
    """

    # create instance of the onshape client; change key to test on another stack
    client = Onshape(access=keys["access"], secret=keys["secret"], target=keys["target"])

    display_name = String(
        display_name='Display Name',
        help='The title Studio uses for the component.',
        scope=Scope.settings,
        default='An Onshape problem'
    )
    prompt = String(
        display_name='Prompt',
        help='The text that gets displayed to the student as a prompt for the problem they need to solve and supply an answer to.',
        scope=Scope.content,
        multiline_editor=True,
        resettable_editor=False,
    )
    question_type = String(
        display_name='The type of the question',
        help='The type of the question being asked. Possible types are volume, mass, etc...',
        scope=Scope.content,
        multiline_editor=False,
        resettable_editor=False,
        default="volume"
    )
    d = Dict(
        display_name='The definition of the question. Please see the documentation for some examples',
        help='Please visit the documentation here to see the default definition of possible question types.',
        scope=Scope.content,
        multiline_editor=False,
        resettable_editor=False,
        default={},
    )
    help_text = String(
        display_name='Help text',
        help='The text that gets displayed when clicking the "+help" button.  If you remove the '
             'help text, the help feature is disabled.',
        scope=Scope.content,
        multiline_editor=True,
        resettable_editor=False,
        default='Paste the URL from your Onshape session into Document URL field. You can check your answers using the button below.',
    )

    editable_fields = [
        'prompt',
        'display_name',
        'd',
        'help_text'
    ]

    # The number of points awarded.
    score = Float(scope=Scope.user_state)
    # The number of attempts used.
    attempts = Integer(scope=Scope.user_state, default=0)
    # The maximum score as calculated from the problem definition
    max_score = Float(scope=Scope.user_state)

    has_score = True
    icon_class = "problem"

    # The max score base on the summation of scores within the checks.
    @property
    def max_score(self):
        max_score = 0
        for check in self.d["checks"]:
            max_score += check["points"]
        return max_score

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the MyXBlock, shown to students
        when viewing courses.
        """
        # Update the default dictionary with the user-specified values.
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "question_type_templates")
        self.d = prepopulate_json(self.d, file_path)
        self.score = 0

        context = dict(
            help_text=self.help_text,
            prompt=self.prompt,
            d=self.d,
        )

        html = loader.render_django_template('templates/html/myxblock.html', context)

        css_context = dict(
            correct_icon=self.runtime.local_resource_url(self, 'public/img/correct-icon.png'),
            incorrect_icon=self.runtime.local_resource_url(self, 'public/img/incorrect-icon.png'),
            unanswered_icon=self.runtime.local_resource_url(self, 'public/img/unanswered-icon.png'),
        )
        css = loader.render_template('templates/css/myxblock.css', css_context)

        frag = Fragment(html)
        frag.add_css(css)
        frag.add_javascript(self.resource_string("static/js/src/myxblock.js"))
        frag.initialize_js('MyXBlock', {"d": self.d, "score": self.score, "max_score": self.max_score})
        return frag

    class Checker:
        """The Checker contains a number of check_ functions. Check functions provide validation checks for a given document/element. A check is made based on the question type.
        For example, a volume question type will always call the "check_volume" function defined. Check functions need to at
        the very least provide a dictionary containing a boolean under the key "correct" to indicate whether or not the
        user satisfied the check. Other common response keys are "message", "actions", etc..."""

        def __init__(self, client, guess):
            """The client provides the connection to the Onshape Servers in order to validate the request. Constraints
            are the constraints for a correct answer for the current xblock. They are a dictionary as defined in the
            particular check function."""
            self.client = client
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

            # Get and test the mass
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
                        failed_feature_type_count=c_i[0]+1,
                        feature_type_expected=feature_type_target_list[c_i[0]],
                        feature_type_actual=feature_type_actual_list[c_i[0]],
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

    @XBlock.json_handler
    def check_answers(self, guess, suffix=''):  # pylint: disable=unused-argument
        """Check the answers given by the student against the constraints.

        This handler is called when the "Check" button is clicked and calls one of the check functions, as described
        by the question type. It passes the guess to the checker, which performs all of the various checks.
        """

        try:
            self.score = 0

            # Check the current guess against the constraints using the checker class. To avoid passing around the url
            # so much, the Checker class has the url components defined as fields
            responses = []
            checker = self.Checker(self.client, guess)
            for check in self.d["checks"]:
                response = checker.check(check)
                if response["correct"]:
                    self.score += check["points"]
                responses.append(response)

            self.runtime.publish(self, 'grade', dict(value=self.score, max_value=self.max_score))
            self.d["attempts"] += 1

            status = {"responses": responses, "score": self.score, "max_score": self.max_score,
                      "max_attempts": self.d["max_attempts"], "attempts": self.d["attempts"]}
        except (requests.exceptions.HTTPError, pint.errors.DimensionalityError) as err:
            # Handle errors here. There should be some logic to turn scary errors into less scary errors for the user.
            if isinstance(err, requests.exceptions.HTTPError):
                return {"error": err.response.json()['message']}
            elif isinstance(err, pint.errors.DimensionalityError):
                return {"error": str(err)}

        return status

    # @XBlock.json_handler
    # def save_answers(self, data, unused_suffix=''):
    #     """Save the answers given by the student without checking them."""
    #     pathComponents = path_parse(urlparse(data['documentUrl']).path)
    #
    #     self.check_and_save_answers(pathComponents[1], pathComponents[3], pathComponents[5])
    #     return self.get_status()

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""

        return [
            ("MyXBlock", """<myxblock max_attempts='3' question_type='simple_checker' d="{'type': 'simple_checker', 'checks':[{'type': 'volume'}, {'type': 'mass'}, {'type': 'center_of_mass'}, {'type': 'part_count'}, {'type': 'feature_list'}], 'max_attempts':10}" prompt='Design a great part according to this prompt'>
             </myxblock>
             """
             )
        ]
