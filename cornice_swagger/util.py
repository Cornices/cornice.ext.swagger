import sys
import inspect


PY3 = sys.version_info[0] == 3

if PY3:
    builtin_str = str
    str = str
    bytes = bytes
    basestring = (str, bytes)
else:
    builtin_str = str
    bytes = str
    str = unicode  # noqa
    basestring = basestring


def is_string(s):
    return isinstance(s, basestring)


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
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    res = '\n'.join(trimmed)
    if not PY3 and not isinstance(res, str):
        res = res.decode('utf8')
    return res


def get_class_that_defined_method(meth):
    if hasattr(meth, "im_class"):
        return meth.im_class
    if PY3:
        if inspect.ismethod(meth):
            for cls in inspect.getmro(meth.__self__.__class__):
                if cls.__dict__.get(meth.__name__) is meth:
                    return cls
            # fallback to __qualname__ parsing
            meth = meth.__func__
        if inspect.isfunction(meth):
            cls = getattr(
                inspect.getmodule(meth),
                meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
            if isinstance(cls, type):
                return cls
    return None
