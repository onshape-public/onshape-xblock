import jsonpickle
from checkers.checker_test import CheckerTest

class Serialize(jsonpickle.handlers.BaseHandler):

    @staticmethod
    def serialize(thing):
        return jsonpickle.encode(thing)

    @staticmethod
    def deserialize(serialized_thing):
        return jsonpickle.decode(serialized_thing)
