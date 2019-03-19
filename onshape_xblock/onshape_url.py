import urlparse

class OnshapeElement(object):
    """ Turn a standard Onshape URL into an OnshapeElement object. Ensure that the URL is correctly formatted, and
    create the useful fields."""
    def __init__(self, url):
        path = urlparse.urlparse(url).path.split('/')
        self.wvmid = path[4]
        self.wvm = path[3]
        self.did = path[2]
        self.eid = path[6]