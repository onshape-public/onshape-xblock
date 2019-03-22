from abc import abstractmethod, ABCMeta, abstractproperty
from ..serialize import Serialize
from ..onshape_client_MOVE import Client
import importlib
from ..onshape_url import OnshapeElement
from jinja2 import Template
from ..utility import res_to_dict


class CheckBase(object):
    """Instructions for making a new check:

    Check Execution:

    A check is a subclass of this CheckBase. It implements an 'execute_check' method that is meant to
    do the work of setting the 'passed' field on the check to either true or false, as well as a number
    of other variables for setting the check's state.

    Check Feedback:

    Check feedback is generated from a 'message_template' field that gets customized with the fields of
     the check itself within the rendering context, allowing for complex display logic in the feedback
     html. """
    __metaclass__ = ABCMeta

    def __init__(self, name="The checker name", max_points=1, client=None,
                 onshape_element=None):
        """Initialize the definition of the check"""
        self.max_points = max_points
        # The points scored for this check
        self.points = 0
        self.name = name
        # Start client on the fly if need be.
        self.client = client if client else Client()

        # A key value map for template substitutions
        self.template_context = {"a_test_variable_name": "a test variable value"}

        self.onshape_element = onshape_element if isinstance(onshape_element, OnshapeElement) or not onshape_element \
            else OnshapeElement(onshape_element)

        # The failure message if the check has failed
        self.failure_message = ""

        # Whether or not the check passed
        self.passed=False

    @abstractmethod
    def execute_check(self):
        """A method that checks the Onshape document and sets feedback based on what it finds.

        Parameters
        ----------
        onshape_element: :obj:`OnshapeElement`
            A url to an Onshape element.
        """
        return NotImplemented

    def get_display_feedback(self):
        """Return only things that should get passed to the UI.
        """

        self.execute_check()
        if self.passed:
            self.points = self.max_points
        else:
            self.format_failure_message()
        return {"message": self.failure_message, "passed": self.passed, "max_points": self.max_points, "points": self.points}

    @abstractproperty
    def failure_message_template(self):
        pass

    #     Useful shared client functions.

    def get_part_id(self, part_number):
        """Return the partId of the part specified by "part_number" at the part specified by did, wvm, eid"""
        return self.get_parts()[part_number].part_id

    def get_parts(self):
        parts = self.client.parts_api.get_parts_wmve(self.onshape_element.did, self.onshape_element.wvm,
                                                     self.onshape_element.wvmid, self.onshape_element.eid)
        return parts

    def get_mass_properties(self, part_id):
        mass_props = self.client.part_studios_api.get_mass_properties(self.onshape_element.did, self.onshape_element.wvm,
                                                               self.onshape_element.wvmid, self.onshape_element.eid,
                                                               part_id=[part_id])
        return mass_props

    def get_features(self):
        res = self.client.part_studios_api.get_features(self.onshape_element.did, self.onshape_element.wvm, self.onshape_element.wvmid,
                                                        self.onshape_element.eid)
        return res_to_dict(res)

    def get_configuration(self):
        res = self.client.part_studios_api.get_configuration4(self.onshape_element.did, self.onshape_element.wvm, self.onshape_element.wvmid, self.onshape_element.eid, _preload_content=False)

        return res_to_dict(res)

    def format_failure_message(self):
        self.failure_message = Template(self.failure_message_template).render(self.__dict__)

#   ----------------------------PRIVATE FUNCTIONS -------------------------------------

