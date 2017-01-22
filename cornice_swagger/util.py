import colander
import six
from cornice.validators import colander_body_validator


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


def body_schema_transformer(schema, args):
    validators = args.get('validators', [])
    if colander_body_validator in validators:
        body_schema = schema
        schema = colander.MappingSchema()
        schema['body'] = body_schema
    return schema
