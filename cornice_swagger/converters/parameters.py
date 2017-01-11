"""Converts from colander request chema to Swagger parameters."""

from cornice_swagger.converters.exceptions import NoSuchConverter


class ParameterConverter(object):
    _in = None

    def convert(self, schema_node, definition_handler):
        """
        Convert node schema into a parameter object.
        """

        converted = {
            'name': schema_node.name,
            'in': self._in,
            'required': schema_node.required
        }
        if schema_node.description:
            converted['description'] = schema_node.description

        if schema_node.default:
            converted['default'] = schema_node.default

        schema = definition_handler(schema_node)

        if '$ref' in schema or schema['type'] == 'object':
            converted['schema'] = schema
        else:
            converted['type'] = schema['type']
        return converted


class PathParameterConverter(ParameterConverter):
    _in = 'path'


class QueryParameterConverter(ParameterConverter):
    _in = 'query'


class HeaderParameterConverter(ParameterConverter):
    _in = 'header'


class BodyParameterConverter(ParameterConverter):
    _in = 'body'

    def convert(self, schema_node, definition_handler):
        schema_node.title = schema_node.__class__.__name__
        converted = super(BodyParameterConverter, self).convert(schema_node,
                                                                definition_handler)

        return converted


class ParameterConversionDispatcher(object):

    converters = {
        'body': BodyParameterConverter,
        'path': PathParameterConverter,
        'querystring': QueryParameterConverter,
        'headers': HeaderParameterConverter,
    }

    def __init__(self, definition_handler):
        self.definition_handler = definition_handler

    def __call__(self, location, schema_node):

        converter_class = self.converters.get(location)
        if converter_class is None:
            raise NoSuchConverter()

        converter = converter_class()
        converted = converter.convert(schema_node, self.definition_handler)

        return converted
