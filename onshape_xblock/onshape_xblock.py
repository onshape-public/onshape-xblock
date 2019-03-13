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
from urlparse import urlparse
from xblock.core import XBlock
from xblock.fields import Boolean, Float, Integer, Scope, String, Dict
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin
import json
import os, sys
import inspect
from .utility import prepopulate_json
import pint
from .checker import Checker
from onshape_client_MOVE import Client

loader = ResourceLoader(__name__)  # pylint: disable=invalid-name


class OnshapeXBlock(StudioEditableXBlockMixin, XBlock):
    """
    A generic Onshape XBlock that can be configured to validate all sorts of parts of an onshape model.
    """

    api_access_key = String(
        display_name='API Access Key',
        help='The access key used to check the documents.',
        scope=Scope.user_state_summary,
        default='Please paste your access key from https://dev-portal.onshape.com'
    )
    api_secret_key = String(
        display_name='Display Name',
        help='The secret key used to check the documents.',
        scope=Scope.user_state_summary,
        default='Please paste your secret key from https://dev-portal.onshape.com'
    )

    client = Client(configuration={"access_key":"***REMOVED***", "secret_key":"***REMOVED***", "base_url":"https://cad.onshape.com"})
    checker = Checker(client)

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
        The primary view of the Onshape_xblock, shown to students
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

        html = loader.render_django_template('templates/html/onshape_xblock.html', context)

        css_context = dict(
            correct_icon=self.runtime.local_resource_url(self, 'public/img/correct-icon.png'),
            incorrect_icon=self.runtime.local_resource_url(self, 'public/img/incorrect-icon.png'),
            unanswered_icon=self.runtime.local_resource_url(self, 'public/img/unanswered-icon.png'),
        )
        css = loader.render_template('templates/css/onshape_xblock.css', css_context)

        frag = Fragment(html)
        frag.add_css(css)
        frag.add_javascript(self.resource_string("static/js/src/onshape_xblock.js"))
        frag.initialize_js('Onshape_xblock', {"d": self.d, "score": self.score, "max_score": self.max_score})
        return frag

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

            for check in self.d["checks"]:
                response = self.checker.check(check)
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
            ("Onshape_xblock", """<onshape_xblock max_attempts='3' question_type='simple_checker' d="{'type': 'simple_checker', 'checks':[{'type': 'volume'}, {'type': 'mass'}, {'type': 'center_of_mass'}, {'type': 'part_count'}, {'type': 'feature_list'}], 'max_attempts':10}" prompt='Design a great part according to this prompt'>
             </onshape_xblock>
             """
             )
        ]
