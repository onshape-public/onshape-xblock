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
from xblock.fields import Boolean, Float, Integer, Scope, String, Dict, List
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin
import json
import os, sys
import inspect
from .utility import prepopulate_json
import pint
from onshape_client_MOVE import Client
from .checks.check_base import CheckBase
from .serialize import Serialize
from check_context import CheckContext
import logging
import traceback
from datetime import datetime

loader = ResourceLoader(__name__)  # pylint: disable=invalid-name

log_file_name = 'logs/onshape_xblock_{}.log'.format(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
logging.basicConfig(filename=log_file_name,level=logging.DEBUG)
logging.debug("Logs have started.")


class OnshapeXBlock(StudioEditableXBlockMixin, XBlock):
    """
    An Onshape XBlock that can be configured to validate all aspects of an onshape element.
    """

    api_access_key = String(
        display_name='API Access Key',
        help='The access key used to check the documents.',
        scope=Scope.user_state_summary,
        default='Please paste your access key from https://dev-portal.onshape.com'
    )
    api_secret_key = String(
        display_name='API Secret Key',
        help='The secret key used to check the documents.',
        scope=Scope.user_state_summary,
        default='Please paste your secret key from https://dev-portal.onshape.com'
    )

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
        default="An Onshape Problem",
    )
    check_list = List(
        display_name='The definition of the question. Please see the documentation for some examples',
        help='Please visit the documentation here to see the default definition of possible question types.',
        scope=Scope.content,
        multiline_editor=True,
        resettable_editor=True,
        default=[{"type": "check_volume"}],
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
    max_points = Float(
        display_name='Max Point Value',
        help='Points awarded for creating an element that passes the tests',
        scope=Scope.settings,
        enforce_type=True,
        default=10,
    )

    editable_fields = [
        'prompt',
        'display_name',
        'check_list',
        'help_text'
    ]

    # The number of points awarded.
    score = Float(scope=Scope.user_state)
    # The number of attempts used.
    attempts = Integer(scope=Scope.user_state, default=0)

    has_score = True
    icon_class = "problem"


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the Onshape_xblock, shown to students
        when viewing courses.
        """

        self.score = 0

        context = dict(
            help_text=self.help_text,
            prompt=self.prompt,
            check_list=self.check_list,
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
        frag.initialize_js('Onshape_xblock', {"d": self.check_list, "score": self.score, "max_score": self.max_points})
        return frag

    @XBlock.json_handler
    def check_answers(self, request_data, suffix=''):  # pylint: disable=unused-argument
        """Check the url given by the student against the constraints.
        Parameters
        ----------
        request_data: dict
            The data with a "url" key that points to the onshape url.
        """
        client = Client(configuration={"access_key": "***REMOVED***",
                                       "secret_key": "***REMOVED***",
                                       "base_url": "https://cad.onshape.com"})
        check_context = CheckContext(client=client, check_init_list=self.check_list)

        try:
            feedback = check_context.perform_all_checks(request_data["url"])
            return feedback

        except (requests.exceptions.HTTPError, pint.errors.DimensionalityError) as err:
            # Handle errors here. There should be some logic to turn scary errors into less scary errors for the user.
            if isinstance(err, requests.exceptions.HTTPError):
                return {"error": err.response.json()['message']}
            elif isinstance(err, pint.errors.DimensionalityError):
                return {"error": str(err)}

        except Exception as e:
            logging.error(traceback.format_exc())

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""

        scenario_default = ("Onshape XBlock", "<onshape_xblock/>")

        check_list = [{'type': 'volume'}, {'type': 'mass'}, {'type': 'center_of_mass'}, {'type': 'part_count'}, {'type': 'feature_list'}]

        check_xml_1 = ("Onshape XBlock",
                       """\
                            <onshape_xblock max_attempts='3' 
                                question_type='simple_checker' 
                                check_list={check_list} 
                                prompt='Design a great part according to this prompt'>
                            </onshape_xblock>
                        """.format(check_list=json.dumps(check_list))
                       )

        return [
            ("three onshape xblocks at once",
             """\
                <vertical_demo>
                    <onshape_xblock/>
                    <onshape_xblock/>
                    <onshape_xblock/>
                </vertical_demo>
             """),scenario_default

        ]
