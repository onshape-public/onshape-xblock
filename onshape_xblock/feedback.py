from jinja2 import Template

class Feedback(object):
    def __init__(self, message=None, passed=None, **kwargs):
        self.message = message
        self.passed = passed
        if not passed:
            self.points = 0
        for k, v in kwargs.items():
            setattr(self, k, v)

    def format_message(self, message_template):
        """Format the message template based on the current feedback"""
        return Template(message_template).render(**self.__dict__)
