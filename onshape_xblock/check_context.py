from onshape_client_MOVE import Client
from serialize import Serialize
from onshape_url import OnshapeElement

class CheckContext(object):
    def __init__(self, check_init_list=None, client=None, onshape_element=None):
        self.check_init_list = check_init_list
        self.client = client
        self.onshape_element = onshape_element

    def perform_all_checks(self, onshape_url=None):
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
        if onshape_url:
            onshape_element = OnshapeElement(onshape_url)
            self.onshape_element = onshape_element
        for check_init_args in self.check_init_list:
            check = self.create_check(check_init_args)
            check.execute_check()
            feedback_list.append(check.feedback)
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
        if "client" not in check_init_args:
            check_init_args["client"] = self.client
        if "onshape_element" not in check_init_args:
            check_init_args["onshape_element"] = self.onshape_element
        check = Serialize.init_class_based_on_type(package_name="onshape_xblock.checks", **check_init_args)
        return check
