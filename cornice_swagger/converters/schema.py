"""
This module handles the conversion between colander object schemas and swagger
object schemas by converting types and node validators.
"""

import colander
from cornice_swagger.converters.exceptions import NoSuchConverter


def convert_length_validator_factory(max_key, min_key):

    def validator_converter(validator):
        converted = None

        if isinstance(validator, colander.Length):
            converted = {}
            if validator.max is not None:
                converted[max_key] = validator.max
            if validator.min is not None:
                converted[min_key] = validator.min

        return converted

    return validator_converter


def convert_oneof_validator_factory():

    def validator_converter(validator):
        converted = None

        if isinstance(validator, colander.OneOf):
            converted = {
                'enum': list(validator.choices)
            }
        return converted

    return validator_converter


def convert_range_validator(validator):

    converted = None

    if isinstance(validator, colander.Range):
        converted = {}

        if validator.max is not None:
            converted['maximum'] = validator.max
        if validator.min is not None:
            converted['minimum'] = validator.min

    return converted


def convert_regex_validator(validator):

    converted = None

    if isinstance(validator, colander.Regex):
        converted = {}

        if hasattr(colander, 'url') and validator is colander.url:
            converted['format'] = 'url'
        elif isinstance(validator, colander.Email):
            converted['format'] = 'email'
        else:
            converted['pattern'] = validator.match_object.pattern

    return converted


class ValidatorConversionDispatcher(object):

    def __init__(self, *converters):

        self.converters = converters

    def __call__(self, schema_node, validator=None):
        if validator is None:
            validator = schema_node.validator

        converted = {}
        if validator is not None:
            for converter in (self.convert_all_validator,) + self.converters:
                ret = converter(validator)
                if ret is not None:
                    converted = ret
                    break

        return converted

    def convert_all_validator(self, validator):

        if isinstance(validator, colander.All):
            converted = {}
            for v in validator.validators:
                ret = self(None, v)
                converted.update(ret)
            return converted
        else:
            return None


class TypeConverter(object):

    type = ''

    def __init__(self, dispatcher):

        self.dispatcher = dispatcher

    def convert_validator(self, schema_node):
        return {}

    def convert_type(self, schema_node):

        converted = {
            'type': self.type
        }

        if schema_node.title:
            converted['title'] = schema_node.title
        if schema_node.description:
            # keep 'description' for back-compatibility
            converted['summary'] = converted['description'] = schema_node.description
        if schema_node.default is not colander.null:
            converted['default'] = schema_node.default
        if 'example' in schema_node.__dict__:
            converted['example'] = schema_node.example

        return converted

    def __call__(self, schema_node):

        converted = self.convert_type(schema_node)
        converted.update(self.convert_validator(schema_node))

        return converted


class BaseStringTypeConverter(TypeConverter):
    type = 'string'
    format = None

    def convert_type(self, schema_node):

        converted = super(BaseStringTypeConverter,
                          self).convert_type(schema_node)

        if self.format is not None:
            converted['format'] = self.format

        return converted


class BooleanTypeConverter(TypeConverter):
    type = 'boolean'


class DateTypeConverter(BaseStringTypeConverter):
    format = 'date'


class DateTimeTypeConverter(BaseStringTypeConverter):
    format = 'date-time'


class NumberTypeConverter(TypeConverter):
    type = 'number'

    convert_validator = ValidatorConversionDispatcher(
        convert_range_validator,
        convert_oneof_validator_factory(),
    )


class IntegerTypeConverter(NumberTypeConverter):
    type = 'integer'


class StringTypeConverter(BaseStringTypeConverter):
    """
    Converts any type of string according to keyword arguments passed to the schema node.

    For example, you can provide a format like follows::

        class Obj(MappingSchema):
            field = SchemaNode(String(), format='url')


    # Dispatch shorthand 'format'/'pattern' arguments to the appropriate string type with
        # validator if it was not explicitly defined with validator argument and can be recognized.
        # Since, 'format' can be anything, this keyword must always be extracted from the node,
        # but it adds a lot of code duplication to give both format/validator keywords.
        # If you want a known 'format' keyword without the validator, set 'validator=colander.drop'.
        #
    """
    def convert_type(self, schema_node):

        # dispatch shorthand argument syntax (see docstring)
        kwarg_format = getattr(schema_node, 'format', None)
        kwarg_pattern = getattr(schema_node, 'pattern', None)
        kwarg_validator = getattr(schema_node, 'validator', None)
        if kwarg_format or kwarg_pattern:
            known_formats = {
                # officials
                'email': {'converter': BaseStringTypeConverter, 'validator': colander.Email},
                'url': {'converter': BaseStringTypeConverter, 'validator': colander.url},
                'date': {'converter': DateTypeConverter, 'validator': None},
                'date-time': {'converter': DateTimeTypeConverter, 'validator': None},
                'password': {'converter': BaseStringTypeConverter, 'validator': colander},
                'binary': {'converter': BaseStringTypeConverter, 'validator': colander.file_uri},
                'byte': {'converter': BaseStringTypeConverter, 'validator': colander.file_uri},
                # common but unofficial
                'time': {'converter': TimeTypeConverter, 'validator': None},
                'hostname': {'converter': BaseStringTypeConverter, 'validator': colander.url},
                'uuid': {'converter': BaseStringTypeConverter, 'validator': colander.uuid},
                'file': {'converter': BaseStringTypeConverter, 'validator': colander.file_uri},
            }
            # extended conversion/validation for known ones
            if kwarg_format and kwarg_format.lower() in known_formats:
                kwarg_format = kwarg_format.lower()
                format_converter_class = known_formats[kwarg_format]['converter']
                if kwarg_validator is None:
                    format_validator = known_formats[kwarg_format]['validator']
                    setattr(schema_node, 'validator', format_validator)
            elif kwarg_format == 'pattern' and not isinstance(kwarg_pattern, colander.Regex):
                raise NoSuchConverter(
                    "String schema with 'pattern' format is missing 'pattern' definition")
            elif kwarg_pattern is not None:
                # validator accepts tuple of multiple strings, but not OpenAPI,
                # instead use oneOf with multiple string SchemaNode each with their own pattern
                if isinstance(kwarg_pattern, str):
                    kwarg_pattern = colander.Regex(
                        kwarg_pattern, msg=colander._('Must match pattern'))  # noqa
                if not isinstance(kwarg_pattern, colander.Regex):
                    raise NoSuchConverter(
                        "Provided string pattern object unknown: {!s}".format(kwarg_pattern))
                format_converter_class = BaseStringTypeConverter
                kwarg_format = None  # don't write 'pattern' as string format
                if kwarg_validator is None:
                    setattr(schema_node, 'validator', kwarg_pattern)
            else:
                # any value for 'format' is permitted and left as is for string definition
                format_converter_class = BaseStringTypeConverter

            format_converter = format_converter_class(self.dispatcher)
            format_converter.format = kwarg_format
            converted = format_converter.convert_type(schema_node)
        else:
            # just a plain string
            converted = super(StringTypeConverter, self).convert_type(schema_node)
        return converted

    convert_validator = ValidatorConversionDispatcher(
        convert_length_validator_factory('maxLength', 'minLength'),
        convert_regex_validator,
        convert_oneof_validator_factory(),
    )


class TimeTypeConverter(BaseStringTypeConverter):
    format = 'time'


class ObjectTypeConverter(TypeConverter):
    type = 'object'

    def convert_type(self, schema_node):
        converted = super(ObjectTypeConverter,
                          self).convert_type(schema_node)

        properties = {}
        required = []

        for sub_node in schema_node.children:
            properties[sub_node.name] = self.dispatcher(sub_node)
            if sub_node.required:
                required.append(sub_node.name)

        if len(properties) > 0:
            converted['properties'] = properties

        if len(required) > 0:
            converted['required'] = required

        if schema_node.typ.unknown == 'preserve':
            converted['additionalProperties'] = {}

        return converted


class ArrayTypeConverter(TypeConverter):
    type = 'array'

    convert_validator = ValidatorConversionDispatcher(
        convert_length_validator_factory('maxItems', 'minItems'),
    )

    def convert_type(self, schema_node):

        converted = super(ArrayTypeConverter,
                          self).convert_type(schema_node)

        converted['items'] = self.dispatcher(schema_node.children[0])
        converted['title'] = converted.get('title') or type(schema_node).__name__
        return converted


class TypeConversionDispatcher(object):
    openapi_spec = 2

    def __init__(self, custom_converters={}, default_converter=None):

        self.converters = {
            colander.Boolean: BooleanTypeConverter,
            colander.Date: DateTypeConverter,
            colander.DateTime: DateTimeTypeConverter,
            colander.Float: NumberTypeConverter,
            colander.Integer: IntegerTypeConverter,
            colander.Mapping: ObjectTypeConverter,
            colander.Sequence: ArrayTypeConverter,
            colander.String: StringTypeConverter,
            colander.Time: TimeTypeConverter,
        }

        self.converters.update(custom_converters)
        self.default_converter = default_converter

    def __call__(self, schema_node):
        schema_type = schema_node.typ
        schema_type = type(schema_type)

        converter_class = self.converters.get(schema_type)
        if converter_class is None:
            if self.default_converter:

                converter_class = self.default_converter
            else:
                raise NoSuchConverter

        converter = converter_class(self)
        converted = converter(schema_node)

        return converted
