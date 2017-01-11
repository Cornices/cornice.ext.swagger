import sys


PY3 = sys.version_info[0] == 3


def trim(docstring):
    """
    Remove the tabs to spaces, and remove the extra spaces / tabs that are in
    front of the text in docstrings.

    Implementation taken from http://www.python.org/dev/peps/pep-0257/
    """
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    res = '\n'.join(lines)
    return res


def get_class_that_defined_method(meth):
    return getattr(meth, 'im_class', None)
