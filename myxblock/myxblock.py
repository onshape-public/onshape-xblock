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
from .utility import parse_url

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

    has_score = True
    icon_class = "problem"

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
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.question_type+".json")
        d = json.load(open(file_path))
        d.update(self.d)
        self.d = d

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
        frag.initialize_js('MyXBlock', self.d)
        return frag


    class Checker:
        """The Checker contains a number of check_ functions. Check functions provide validation checks for a given document/element. A check is made based on the question type.
        For example, a volume question type will always call the "check_volume" function defined. Check functions need to at
        the very least provide a dictionary containing a boolean under the key "correct" to indicate whether or not the
        user satisfied the check. Other common response keys are "message", "actions", etc..."""
        def __init__(self, client):
            """The client provides the connection to the Onshape Servers in order to validate the request. Constraints
            are the constraints for a correct answer for the current xblock. They are a dictionary as defined in the
            particular check function."""
            self.client = client

        def check(self, check, guess):
            """Perform the correct check for the stipulated check_type."""

            #change the guess url (if there is one) into the constituent components.
            guess.update(parse_url(guess["url"]))
            checker_function = getattr(self, "check_" + check["type"])
            return checker_function(check["constraints"], guess)

        def check_volume(self, constraints, guess):
            res = self.client.parts.get_parts_in_partstudio(guess["did"], guess["wvm"], guess["eid"])
            if res.status_code != 200:
                raise UserWarning(res.message)
            partId = res.json()[0]['partId']
            mass_properties = self.client.parts.get_mass_properties(guess["did"], guess["wvm_pair"], guess["eid"], partId)
            volume = mass_properties.json()['bodies'][partId]['volume'][0]
            correct = volume < constraints["max"] and volume > constraints["min"]
            return {"correct":correct}

        def check_mass(self, constraints, guess):
            res = self.c.parts.get_parts_in_partstudio(guess['url'])
            if res.status_code != 200:
                raise UserWarning(res.message)
            partId = res.json()[0]['partId']
            mass_properties = self.client.parts.get_mass_properties(guess["did"], guess["wvm_pair"], guess["eid"], partId)
            mass = mass_properties.json()['bodies'][partId]['mass'][0]
            correct = mass < self.constraints["max"] and mass > self.constraints["min"]
            return {"correct": correct}


    @XBlock.json_handler
    def check_answers(self, guess, suffix=''):  # pylint: disable=unused-argument
        """Check the answers given by the student against the constraints.

        This handler is called when the "Check" button is clicked and calls one of the check functions, as described
        by the question type.
        """

        self.score = None

        # Check the current guess against the constraints using the checker class.
        responses = {}
        checker = self.Checker(self.client)
        for check_name, check in self.d["checks"].items():
            responses[check_name] = checker.check(check, guess)


        # Update the user's state based on the result of the check. For now, just give the user points.
        for check_name, response in responses.items():
            if response["correct"]:
                self.d["score"] += self.d["checks"][check_name]["points"]

        self.runtime.publish(self, 'grade', dict(value=self.d["score"], max_value=self.d['v']['max_score']))
        self.d["attempts"] += 1

        return self.d



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
            ("MyXBlock", """<myxblock max_attempts='3' question_type='volume' d="{}" prompt='Design a part with a volume of 7.627968 in^3'>
             </myxblock>
             """
             )
        ]
