"""Onshape XBlock.

How we handle the UI:

The ui expects a single object representing all state of xblock to be returned. Specifically, this is
the object returned from the OnshapeXBlock.assemble_ui_dictionary() method. In general, the only methods
that return anything should be that method, and consequently the handler methods. Every other method
should set state on the block itself using the declared fields from the mixin. In this way the edx
software keeps track of the xblock state by persisting those fields to a database.

"""

import pkg_resources
from xblock.core import XBlock
from xblock.fields import Boolean, Float, Integer, Scope, String, Dict, List
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin
import json
import pint
from check_context import CheckContext
import logging
import traceback
from onshape_client.client import Client
from onshape_client.onshape_url import OnshapeElement
import importlib
from serialize import Serialize

loader = ResourceLoader(__name__)  # pylint: disable=invalid-name

# log_file_name = 'logs/onshape_xblock_{}.log'.format(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
logging.basicConfig(level=logging.DEBUG)
logging.debug("Logs have started.")


class OnshapeXBlock(StudioEditableXBlockMixin, XBlock):
    """
    An Onshape XBlock that can be configured to validate all aspects of an onshape element.
    """

    api_access_key = String(
        display_name='API Access Key',
        help='The access key used to check the documents.',
        scope=Scope.settings,
        default='Please paste your access key from https://dev-portal.onshape.com'
    )
    api_secret_key = String(
        display_name='API Secret Key',
        help='The secret key used to check the documents.',
        scope=Scope.settings,
        default='Please paste your secret key from https://dev-portal.onshape.com'
    )

    display_name = String(
        display_name='Display Name',
        help='The title Studio uses for the component and the title that the student will see.',
        scope=Scope.settings,
        default='An Onshape problem'
    )
    prompt = String(
        display_name='Prompt',
        help='The text that gets displayed to the student as a prompt for the problem they need to enter the url. This'
             'should not be the instructions for the problem itself, as those should be put into a separate text xblock'
             'that allows for more customization.',
        scope=Scope.content,
        multiline_editor=False,
        resettable_editor=False,
        default="An Onshape Problem",
    )
    check_list = List(
        display_name='The definition of the question. Please see the documentation for some examples',
        help='Please visit the documentation here to see the default definition of possible question types.',
        scope=Scope.content,
        multiline_editor=True,
        resettable_editor=True,
        default=[{"type": "check_volume", "max_points": 6}],
    )
    help_text = String(
        display_name='Help text',
        help='The text that gets displayed when clicking the "+help" button.  If you remove the '
             'help text, the help feature is disabled.',
        scope=Scope.content,
        multiline_editor=False,
        resettable_editor=False,
        default='Paste the URL from your Onshape session into Document URL field. You can check your answers using the button below.',
    )
    max_attempts = Integer(
        display_name='Max Attempts Allowed',
        help='The number of times a user can submit a check. None indicates there is no limit.',
        scope=Scope.settings,
        enforce_type=False,
        default=3,
    )

    editable_fields = [
        'api_access_key',
        'api_secret_key',
        'prompt',
        'display_name',
        'check_list',
        'help_text',
        'max_attempts'
    ]

    # The number of points awarded.
    score = Float(scope=Scope.user_state, default=0)
    # The number of attempts used.
    attempts = Integer(scope=Scope.user_state, default=0)
    submitted_url = String(scope=Scope.user_state)
    submitted_grade = Boolean(scope=Scope.user_state, default=False)
    response_list = List(scope=Scope.user_state, default=[])
    error = String(scope=Scope.user_state, default="")

    # OAuth initialization vars
    access_token = String(scope=Scope.user_state, default="")
    refresh_token = String(scope=Scope.user_state, default="")
    client_id = String(scope=Scope.user_state, default="")
    client_secret = String(scope=Scope.user_state, default="")
    redirect_url = String(scope=Scope.user_state, default="")

    # OAuth status vars
    need_to_authenticate = String(scope=Scope.user_state, default="")
    oauth_authorization_url = String(scope=Scope.user_state, default="")
    oauth_authorization_is_done = String(scope=Scope.user_state, default="")

    has_score = True
    icon_class = "problem"


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def start_client(self):
        """Start the client if the client isn't already started."""
        try:
            Client.get_client()
        except Exception as e:
            Client(open_authorize_grant_callback=self.set_need_to_authorize)

    def oauth_login_view(self, context):
        html = loader.render_django_template('templates/html/oauth_login_view.html', {})
        css = loader.render_template('templates/css/onshape_xblock.css', {})
        frag = Fragment(html)
        frag.add_css(css)
        js_str = str(self.resource_string("static/js/dist/oauth_login_view.js"))
        frag.add_javascript(js_str)
        frag.initialize_js('makeOauthBlock')
        return frag

    def studio_view2(self, context):
        return self.studio_view(context)

    def studio_view(self, context):
        """
        The studio view presented to the creator of the Onshape XBlock. This includes dynamic xblock type selection.

        """
        self.start_client()

        html_context = dict(
            check_list_form=self.runtime.local_resource_url(self, 'public/json/check_list_form.json')
        )
        html = loader.render_django_template('templates/html/editor_view.html', html_context)

        frag = super(OnshapeXBlock, self).studio_view(context)

        frag.add_content(html)

        frag.add_javascript(self.resource_string("static/js/dist/studio_view.js"))

        frag.initialize_js("")

        return frag


    def student_view(self, context=None):
        """
        The primary view of the Onshape_xblock, shown to students
        when viewing courses.
        """
        self.start_client()
        context = dict(
            help_text=self.help_text,
            prompt=self.prompt,
            check_list=self.check_list
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
        js_str = str(self.resource_string("static/js/dist/student_view.js"))
        frag.add_javascript(js_str)
        init_args = self.assemble_ui_dictionary()
        frag.initialize_js('entry_point', json_args=init_args)
        return frag

    def total_max_points(self):
        cumulative = 0
        for check in self.check_list:
            cumulative += check["max_points"]
        return cumulative

    def calculate_points(self):
        cumulative = 0
        for check in self.response_list:
            cumulative += check["points"]
        return cumulative

    def assemble_ui_dictionary(self):
        ui_args = dict(
            current_score=self.score,
            max_attempts=self.max_attempts,
            max_points=self.total_max_points(),
            submitted=self.submitted_grade,
            attempts_made=self.attempts,
            submitted_url=self.submitted_url,
            response_list=self.response_list,
            error=self.error
        )
        return ui_args

    def is_checked(self):
        return self.response_list != []

    def clear_errors(self):
        self.error = ""

    def set_errors(self, error):
        """Evaluates and sets the necessary headers on the Onshape block from performing the checks."""
        try:
            raise error
        except (pint.errors.DimensionalityError) as err:
            # Handle errors here. There should be some logic to turn scary errors into less scary errors for the user.
            self.error = str(err)

        except Exception as e:
            logging.error(traceback.format_exc())
            body = json.loads(e.body)
            self.error = body["message"]

    # The callback for the OAuth client
    def set_need_to_authorize(self, url, done):
        self.need_to_authenticate = True
        self.oauth_authorization_url = url
        self.oauth_authorization_is_done = done


    def get_oauth_authorize_message(self):
        oauth_callback_params = dict(
            url=self.oauth_authorization_url,
            error="OAUTH_NOT_INITIALIZED"
        )
        return oauth_callback_params

    @XBlock.json_handler
    def finish_oauth_authorization(self, request_data, suffix=''):
        """Return the authorization redirected-to url that includes the authorization code."""
        self.oauth_authorization_is_done(request_data["authorization_code_url"])

    @XBlock.json_handler
    def check_answers(self, request_data, suffix=''):  # pylint: disable=unused-argument
        """Check the url given by the student against the constraints.
        Parameters
        ----------
        request_data: dict
            The data with a "url" key that points to the onshape url.
        """
        self.clear_errors()
        url = request_data["url"]
        if url:
            self.submitted_url = url
        # Either intentionally submitting current answer OR forced into submitting current
        if request_data["is_final_submission"] or self.attempts >= self.max_attempts:
            if not self.is_checked():
                self.perform_checks()
            self.submit_final_grade()
        # Checking the current answer
        else:
            self.perform_checks()
        if self.need_to_authenticate:
            # Authentication failed, need to follow OAuth flow
            return self.get_oauth_authorize_message()

        return self.assemble_ui_dictionary()

    def perform_checks(self):
        """Grade the submitted url and return either the error from the Onshape server
        OR return the ui dictionary."""
        check_context = CheckContext(check_init_list=self.check_list, onshape_element=self.submitted_url)
        try:
            self.response_list = check_context.perform_all_checks()
            self.score = self.calculate_points()
            self.attempts += 1
        except Exception as e:
            self.set_errors(e)

    def submit_final_grade(self, client=None):
        """Submit the grade to official xblock course."""
        self.runtime.publish(self, "grade",
                             {"value": self.score,
                              "max_value": self.total_max_points()})
        self.submitted_grade = True
        self.lock_submitted_url_with_microversion()

    def lock_submitted_url_with_microversion(self, client=None):
        self.submitted_url = OnshapeElement(self.submitted_url).get_microversion_url()

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""

        scenario_default = ("Default Onshape XBlock", "<onshape_xblock/>")

        check_list = [{'type': 'volume'}, {'type': 'mass'}, {'type': 'center_of_mass'}, {'type': 'part_count'}, {'type': 'feature_list'}]

        check_xml_1 = ("Onshape XBlock",
                       """\
                            <onshape_xblock max_attempts='3' 
                                question_type='simple_checker' 
                                check_list={check_list} 
                                prompt="\<html\>">
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
