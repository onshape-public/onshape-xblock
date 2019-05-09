from onshape_client.client import Client
from serialize import Serialize
from onshape_client.onshape_url import OnshapeElement


class CheckContext(object):
    def __init__(self, check_init_list=None, onshape_element=None):
        self.check_init_list = check_init_list
        self.checks = []
        if onshape_element:
            self.onshape_element = onshape_element if isinstance(onshape_element, OnshapeElement) else OnshapeElement(onshape_element)
        else:
            self.onshape_element = None
        if check_init_list:
            for check_init_args in check_init_list:
                self.checks.append(self.create_check(check_init_args))

    def perform_all_checks(self):
        """Perform all the checks indicated in the check context

        Parameters
        ----------
            onshape_url: str
                The well formatted onshape url that points to the element to be tested.

        Returns
        -------
            A list of feedback items to be displayed to the student
        """
        feedback_list = []
        for check in self.checks:
            feedback_list.append(check.perform_check_and_get_display_feedback())
        return feedback_list

    def create_check(self, check_init_args):
        """Create a check instance

        Parameters:
        -----------
            check_init_args: dict
                All the arguments that will be passed into the check instance upon initialization.

        Returns:
        --------
            The created check instance.

        """
        # Inject fields that we want in all clients into the mix.
        check = Serialize.init_class_based_on_type(package_name="onshape_xblock.checks",
                                                   onshape_element=self.onshape_element,
                                                   **check_init_args)
        return check
