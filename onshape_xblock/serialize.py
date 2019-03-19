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
    def init_class_list(input_list, default_package_name="onshape_xblock.checks"):
        """Call the init methods for each element of the list. The type specifies both the module and the class name.
        There is an implicit assumption that these follow this pattern: my_amazing_class.MyAmazingClass.

        Parameters
        ----------
        input_list: list
            A list of dictionaries of initialization args to call with respect to the instantiated Checker as determined
             by the 'type' param for each dict.
        default_package_name: :obj:`str`
            Optional name for the package from which to initialize the class if not defined within the list element.

        Returns
        -------
        list of checker instances
            A list of initialized checks."""

        if isinstance(input_list, str) or isinstance(input_list, bytes):
            input_list = jsonpickle.loads(input_list)

        final_list = []
        for class_args in input_list:
            if "package_name" not in class_args:
                class_args["package_name"] = default_package_name
            final_list.append(Serialize.init_class_based_on_type(**class_args))

        return final_list

    @staticmethod
    def init_class_based_on_type(package_name=None, type=None, **class_init_args):
        if not type:
            raise AttributeError("Must define a checker type.")
        module_name = package_name + "." + type
        class_name = Serialize.to_pascal_case(type)
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        return class_(**class_init_args)

    @staticmethod
    def to_pascal_case(snake_str):
        components = snake_str.split('_')
        # We capitalize the first letter of each component except the first one
        # with the 'title' method and join them together.
        return ''.join(x.title() for x in components)

