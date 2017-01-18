import six


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
    lines = six.u(docstring).expandtabs().splitlines()
    lines = [line.strip() for line in lines]
    res = six.u('\n').join(lines)
    return res
