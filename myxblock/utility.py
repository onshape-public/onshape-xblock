import urlparse


def parse_url(url):
    """Parse an Onshape element url into a dictionary containing did, eid, and wvm_pair"""
    path = urlparse.urlparse(url).path.split('/')
    # Expected parameters in the path
    d_expected = {3: "wvm_type", 2: "did", 6: "eid", 4: "wvm"}
    d = {}
    for index, name in d_expected.items():
        try:
            d[name] = path[index]
        except IndexError:
            pass
    d["wvm_pair"] = (d["wvm_type"], d["wvm"])
    return d