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
from onshape_client.client import Client, OAuthAuthorizationMethods, OAuthNotAuthorizedException
from onshape_client.onshape_url import OnshapeElement
from onshape_client.rest import ApiException
import importlib
from serialize import Serialize
import os

loader = ResourceLoader(__name__)  # pylint: disable=invalid-name

# log_file_name = 'logs/onshape_xblock_{}.log'.format(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
logging.basicConfig(level=logging.DEBUG)
logging.debug("Logs have started.")


class OnshapeXBlock(StudioEditableXBlockMixin, XBlock):
    """
    An Onshape XBlock that can be configured to validate all aspects of an onshape element.
    """

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
        default=[{"check_type": "check_volume", "max_points": 6}],
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
        default=1,
    )

    editable_fields = [
        'client_id',
        'client_secret',
        'redirect_uri',
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

    # OAuth initialization vars (these are set by the course creator.)
    client_id = String(scope=Scope.content,
                       default="",
                       display_name="Client ID",
                       help='Please create an OAuth app on the Onshape dev portal for this block here: https://dev-portal.onshape.com . Make sure to give the app read scope. This value need only be entered once per course')
    client_secret = String(scope=Scope.content,
                           display_name="Client Secret",
                           default="")
    redirect_uri = String(scope=Scope.content,
                          display_name="Redirect URI",
                          default="",
                          help="This redirect url should look something like: http://104.154.245.15/courses/course-v1:Onshape+OS101+SP2019/xblock/block-v1:Onshape+OS101+SP2019+type@onshape_xblock+block@b8a2ba01ca3e4542a02833e5ea5be3d5/handler/oauth_login_view .")

    # OAuth status vars (these are per user state)
    access_token = String(scope=Scope.preferences, default="")
    refresh_token = String(scope=Scope.preferences, default="")
    need_to_authenticate = Boolean(scope=Scope.preferences, default=False)
    oauth_authorization_url = String(scope=Scope.preferences, default="")

    has_score = True
    icon_class = "problem"

    def total_max_points(self):
        cumulative = 0
        for response in self.response_list:
            cumulative += response["max_points"]
        return cumulative

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_client(self):
        """Start the client if the client isn't already started."""
        try:
            client = Client.get_client(create_if_needed=False)
        except Exception as e:
            client = Client(configuration={"client_id": self.client_id,
                                  "client_secret": self.client_secret,
                                  "base_url": "https://cad.onshape.com",
                                  "token_uri": "https://oauth.onshape.com/oauth/token",
                                  "authorization_uri": "https://oauth.onshape.com/oauth/authorize",
                                  "oauth_authorization_method": OAuthAuthorizationMethods.MANUAL_FLOW,
                                  "scope": ["OAuth2Read"],
                                  "redirect_uri": self.redirect_uri,
                                  "access_token": self.access_token,
                                  "refresh_token": self.refresh_token
            })
        return client

    def oauth_login_view(self, context):
        html = loader.render_django_template('templates/html/oauth_login_view.html', {})
        css = loader.render_template('templates/css/onshape_xblock.css', {})
        frag = Fragment(html)
        frag.add_css(css)
        js_str = str(self.resource_string("static/js/dist/oauth_login_view.js"))
        frag.add_javascript(js_str)
        frag.initialize_js('makeOauthBlock')
        return frag

    def studio_view(self, context):
        """
        The studio view presented to the creator of the Onshape XBlock. This includes dynamic xblock type selection.

        """
        frag = super(OnshapeXBlock, self).studio_view(context)

        # js_context = dict(
        #     check_list_form=self.resource_string('public/json/check_list_form.json')
        # )
        # js = loader.render_django_template("static/js/inject_vars.js", js_context)
        #
        # frag.add_javascript(js)
        # frag.add_javascript(self.resource_string("static/js/dist/studio_view.js"))
        #
        # frag.initialize_js("")

        return frag


    def student_view(self, context=None):
        """
        The primary view of the Onshape_xblock, shown to students
        when viewing courses.
        """
        context = dict(
            help_text=self.help_text,
            prompt=self.prompt,
            check_list=self.check_list,
            max_attempts=self.max_attempts
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
        if self.need_to_authenticate:
            ui_args["oauthUrl"] = self.oauth_authorization_url
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
            if self.need_to_authenticate:
                self.error = "OAuthNotAuthenticated"
            else:
                logging.error(traceback.format_exc())
                body = json.loads(e.body)
                self.error = body["message"]

    # The callback for the OAuth client
    def set_need_to_authorize(self, url_state_tuple):
        self.need_to_authenticate = True
        self.oauth_authorization_url, state = url_state_tuple


    def get_oauth_authorize_message(self):
        oauth_callback_params = dict(
            url=self.oauth_authorization_url,
            error="OAUTH_NOT_INITIALIZED"
        )
        return oauth_callback_params

    @XBlock.json_handler
    def finish_oauth_authorization(self, request_data, suffix=''):
        """Return the authorization redirected-to url that includes the authorization code."""
        url = request_data["authorization_code_url"]

        # Pretend we have https so that the oauth library doesn't complain for using the XBlock SDK.
        if 'https' not in url:
            url = url.replace("http", "https")

        token_dict = Client.get_client().fetch_access_token(url)
        self.access_token = token_dict["access_token"]
        self.refresh_token = token_dict["refresh_token"]

    @XBlock.json_handler
    def check_answers(self, request_data, suffix=''):  # pylint: disable=unused-argument
        """Check the url given by the student against the constraints.
        Parameters
        ----------
        request_data: dict
            The data with a "url" key that points to the onshape url.
        """
        client = self.get_client()
        self.clear_errors()
        url = request_data["url"]
        if url:
            self.submitted_url = url

        try:
            # Either intentionally submitting current answer OR forced into submitting current
            if request_data["is_final_submission"] or self.attempts >= self.max_attempts:
                if not self.is_checked():
                    self.perform_checks()
                self.submit_final_grade()
            # Checking the current answer
            else:
                self.perform_checks()
                # Need to authenticate with OAuth
        except OAuthNotAuthorizedException as e:
            # Client id/ Client secret aren't specified
            self.set_need_to_authorize(client.oauth.authorization_url(client.authorization_uri))
            self.set_errors(e)
        except ApiException as e:
            self.set_errors(e)
        return self.assemble_ui_dictionary()

    def perform_checks(self):
        """Grade the submitted url and return either the error from the Onshape server
        OR return the ui dictionary."""
        check_context = CheckContext(check_init_list=self.check_list, onshape_element=self.submitted_url)
        self.response_list = check_context.perform_all_checks()
        self.score = self.calculate_points()
        self.attempts += 1

    def submit_final_grade(self):
        """Submit the grade to official xblock course."""
        self.runtime.publish(self, "grade",
                             {"value": self.score,
                              "max_value": self.total_max_points()})
        self.submitted_grade = True
        self.lock_submitted_url_with_microversion()

    def lock_submitted_url_with_microversion(self):
        self.submitted_url = OnshapeElement(self.submitted_url).get_microversion_url()

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""

        check_list_small = [{'check_type': 'check_volume'}]

        check_list_all = [{'check_type': 'check_volume'}, {'check_type': 'check_mass'}, {'check_type': 'check_center_of_mass'}, {'check_type': 'check_part_count'}, {'check_type': 'check_feature_list'}]

        scenario_default = ("Default Onshape XBlock",
                       """\
                            <onshape_xblock 
                                max_attempts="3" 
                                client_id="{client_id}"
                                client_secret="{client_secret}" 
                                redirect_uri="{redirect_uri}"
                                check_list="{check_list}">
                            </onshape_xblock>
                        """.format(client_id=os.environ["ONSHAPE_CLIENT_ID"],
                                   client_secret=os.environ["ONSHAPE_CLIENT_SECRET"],
                                   redirect_uri="http://localhost:8000/scenario/onshape_xblock.1/",
                                   check_list=check_list_small),
                       )

        three_at_once_scenario = ("Three Onshape Xblocks at once",
             """\
                <vertical_demo>
                    <onshape_xblock/>
                    <onshape_xblock/>
                    <onshape_xblock/>
                </vertical_demo>
             """)

        one_shot_scenario = ("Onshape XBlock one_shot_scenario",
                       """\
                            <onshape_xblock 
                                max_attempts="1" 
                                client_id="{client_id}"
                                client_secret="{client_secret}" 
                                redirect_uri="{redirect_uri}"
                                check_list="{check_list}">
                            </onshape_xblock>
                        """.format(client_id=os.environ["ONSHAPE_CLIENT_ID"],
                                   client_secret=os.environ["ONSHAPE_CLIENT_SECRET"],
                                   redirect_uri=os.environ["ONSHAPE_REDIRECT_URL"],
                                   check_list=check_list_small),
                       )

        return [
            three_at_once_scenario ,scenario_default

        ]
