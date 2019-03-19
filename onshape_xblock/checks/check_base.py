from abc import abstractmethod, ABCMeta, abstractproperty
from ..serialize import Serialize
from ..onshape_client_MOVE import Client
import importlib
from ..onshape_url import OnshapeElement
from onshape_xblock.feedback import Feedback

class CheckBase(object):
    __metaclass__ = ABCMeta

    def __init__(self, name="The checker name", points=1, client=None,
                 onshape_element=None):
        """Initialize the definition of the check"""
        self.points = points
        self.name = name
        # Start client on the fly if need be.
        self.client = client if client else Client()

        if not onshape_element:
            raise EnvironmentError("No Onshape Element Selected")
        else:
            self.onshape_element = onshape_element if isinstance(onshape_element, OnshapeElement) else OnshapeElement(onshape_element)

        self.feedback = None
        # A key value map for jinja substitutions
        self.template_context = {"a_test_variable_name": "a test variable value"}

    @abstractmethod
    def execute_check(self):
        """A method that checks the Onshape document and sets feedback based on what it finds.

        Parameters
        ----------
        onshape_element: :obj:`OnshapeElement`
            A url to an Onshape element.

        """
        return NotImplemented

    def get_feedback(self):
        self.execute_check()
        if not self.feedback.message:
            if self.feedback.passed:
                self.feedback.message = self.feedback.format_message(self.success_message_template)
            else:
                self.feedback.message = self.feedback.format_message(self.failure_message_template)
        return self.feedback

    @abstractproperty
    def failure_message_template(self):
        pass

    @abstractproperty
    def success_message_template(self):
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
        res = self.client.part_studios_api.get_mass_properties(self.onshape_element.did, self.onshape_element.wvm,
                                                               self.onshape_element.wvmid, self.onshape_element.eid,
                                                               part_id=[part_id])
        return res

    def get_features(self):
        res = self.client.part_studios_api.get_features(self.onshape_element.did, self.onshape_element.wvm, self.onshape_element.wvmid,
                                                        self.onshape_element.eid)
        res.raise_for_status()
        return res.json()

    def get_configuration(self):
        res = self.client.elements_api.get_configuration3(self.onshape_element.did, self.onshape_element.wvm, self.onshape_element.wvmid,
                                                          self.onshape_element.eid, _preload_content=False)
        res.raise_for_status()
        return res.json()

#   ----------------------------PRIVATE FUNCTIONS -------------------------------------

