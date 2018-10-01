"""Onshape XBlock"""

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

loader = ResourceLoader(__name__)  # pylint: disable=invalid-name

def path_parse( path_string, normalize = True):
    result = []
    if normalize:
        tmp = posixpath.normpath( path_string )
    else:
        tmp = path_string
    while tmp != "/":
        ( tmp, item ) = posixpath.split( tmp )
        result.insert( 0, item )
    return result

class MyXBlock(StudioEditableXBlockMixin, XBlock):
    """
    An XBlock to retrieve and compare the volume of a part in Onshape.
    """

    # create instance of the onshape client; change key to test on another stack
    c = Onshape(access=keys["access"], secret=keys["secret"], target=keys["target"])

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    display_name = String(
        display_name='Display Name',
        help='The title Studio uses for the component.',
        scope=Scope.settings,
        default='Onshape problem'
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
    question_constraints = Dict(
        display_name='The constraints of what is considered a correct answer. These can vary significantly based on the question type.',
        help='Please visit the documentation here to see the possible question types.',
        scope=Scope.content,
        multiline_editor=False,
        resettable_editor=False,
        default='Paste the URL from your Onshape session into Document URL field. You can check your answers using the button below.',
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
    maximum_score = Float(
        display_name='Maximum score',
        help='The number of points students will be awarded when solving all fields correctly.  '
        'For partially correct attempts, the score will be pro-rated.',
        scope=Scope.settings,
        default=1.0,
    )
    max_attempts = Integer(
        display_name='Maximum attempts',
        help='Defines the number of times a student can try to answer this problem.  If the value '
        'is not set, infinite attempts are allowed.',
        scope=Scope.settings
    )

    editable_fields = [
        'prompt',
        'display_name',
        'question_constraints',
        'help_text',
        'maximum_score',
        'max_attempts',
    ]

    # The number of points awarded.
    score = Float(scope=Scope.user_state)
    # The number of attempts used.
    attempts = Integer(scope=Scope.user_state, default=0)
    partVolume = Float(scope=Scope.user_state)

    has_score = True
    icon_class = "problem"

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_status(self):
        """Status dictionary passed to the frontend code."""
        return dict(
            score=self.score,
            maximum_score=self.maximum_score,
            attempts=self.attempts,
            max_attempts=self.max_attempts,
            partVolume=self.partVolume,
            minVolume=self.question_constraints["min"],
            maxVolume=self.question_constraints["max"],
        )

    def student_view(self, context=None):
        """
        The primary view of the MyXBlock, shown to students
        when viewing courses.
        """
        context = dict(
            help_text=self.help_text,
            prompt=self.prompt,
            max_attempts=self.max_attempts,
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
        frag.initialize_js('MyXBlock', self.get_status())
        return frag

    def check_and_save_answers(self, documentId, workspaceId, elementId):
        """Common implementation for the check and save handlers."""
        # if self.max_attempts and self.attempts >= self.max_attempts:
        #     # The "Check" button is hidden when the maximum number of attempts has been reached, so
        #     # we can only get here by manually crafted requests.  We simply return the current
        #     # status without rechecking or storing the answers in that case.
        #     return self.partVolume < self.max_value and self.partVolume > self.min_value

        if self.question_type == "volume":
            res = self.c.parts.get_parts_in_partstudio(documentId, workspaceId, elementId)
            partId = res.json()[0]['partId']
            if (partId):
                massProperties = self.c.parts.get_mass_properties(documentId, ('w',workspaceId), elementId, partId)
                self.partVolume = massProperties.json()['bodies'][partId]['volume'][0]
                return self.partVolume < self.question_constraints["max"] and self.partVolume > self.question_constraints["min"]
        if self.question_type == "mass":
            return True


    @XBlock.json_handler
    def check_answers(self, data, suffix=''):  # pylint: disable=unused-argument
        """Check the answers given by the student.

        This handler is called when the "Check" button is clicked.
        """

        pathComponents = path_parse(urlparse(data['documentUrl']).path)


        self.score = None
        if (self.check_and_save_answers(pathComponents[1], pathComponents[3], pathComponents[5])):
            self.score = self.maximum_score
        self.runtime.publish(self, 'grade', dict(value=self.score, max_value=self.maximum_score))


        self.attempts += 1
        return self.get_status()




    @XBlock.json_handler
    def save_answers(self, data, unused_suffix=''):
        """Save the answers given by the student without checking them."""
        pathComponents = path_parse(urlparse(data['documentUrl']).path)

        self.check_and_save_answers(pathComponents[1], pathComponents[3], pathComponents[5])
        return self.get_status()

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("MyXBlock",
             """<myxblock max_attempts='3' question_type='volume' question_constraints="{'min':'0.0001249', 'max':'0.0001251'}" prompt='Design a part with a volume of 7.627968 in^3'>
             </myxblock>
             """)
        ]
