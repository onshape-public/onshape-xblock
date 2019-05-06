import jsonpickle
import importlib

class Serialize(jsonpickle.handlers.BaseHandler):

    @staticmethod
    def serialize(thing):
        return jsonpickle.encode(thing)

    @staticmethod
    def deserialize(serialized_thing):
        return jsonpickle.decode(serialized_thing)

    @staticmethod
    def init_class_list(input_list, default_package_name="onshape_xblock.checks", init_class=True):
        """Call the init methods for each element of the list. The check_type specifies both the module and the class name.
        There is an implicit assumption that these follow this pattern: my_amazing_class.MyAmazingClass.

        Parameters
        ----------
        input_list: list
            A list of dictionaries of initialization args to call with respect to the instantiated Checker as determined
             by the 'check_type' param for each dict.
        default_package_name: :obj:`str`
            Optional name for the package from which to initialize the class if not defined within the list element.
        init_class: :obj:`bool`
            If True, this will initialize the class. Otherwise, it will return the static class

        Returns
        -------
        list of checker instances
            A list of initialized checks."""

        if isinstance(input_list, str) or isinstance(input_list, bytes):
            input_list = jsonpickle.loads(input_list)

        final_list = []
        for class_args in input_list:
            if "package_name" not in class_args:
                package_name = default_package_name
            else:
                package_name = class_args["package_name"]
            final_list.append(Serialize.init_class_based_on_type(package_name=package_name, init_class=init_class, **class_args))
        return final_list

    @staticmethod
    def init_class_based_on_type(package_name=None, check_type=None, init_class=True, **class_init_args):
        if not check_type:
            raise AttributeError("Must define a checker type.")
        module_name = package_name + "." + check_type
        class_name = Serialize.to_pascal_case(check_type)
        module = importlib.import_module(module_name)
        try:
            class_ = getattr(module, class_name)
        except AttributeError as e:
            raise AttributeError("The class name in module {} needs to match {}".format(module_name, class_name))
        if init_class:
            return class_(**class_init_args)
        else:
            return class_

    @staticmethod
    def to_pascal_case(snake_str):
        components = snake_str.split('_')
        # We capitalize the first letter of each component except the first one
        # with the 'title' method and join them together.
        return ''.join(x.title() for x in components)

