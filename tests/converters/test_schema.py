import unittest
import colander

from cornice_swagger.converters import convert_schema as convert


class StringConversionTest(unittest.TestCase):

    def test_sanity(self):
        node = colander.SchemaNode(colander.String())
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'string',
        })

    def test_validate_default(self):
        node = colander.SchemaNode(colander.String(), default='foo')
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'string',
            'default': 'foo',
        })

    def test_validate_length(self):
        node = colander.SchemaNode(colander.String(),
                                   validator=colander.Length(12, 42))
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'string',
            'maxLength': 42,
            'minLength': 12,
        })

    def test_validate_regex(self):
        node = colander.SchemaNode(colander.String(),
                                   validator=colander.Regex(r'foo*bar'))
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'string',
            'pattern': 'foo*bar',
        })

    def test_validate_regex_email(self):
        node = colander.SchemaNode(colander.String(),
                                   validator=colander.Email())
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'string',
            'format': 'email',
        })

    def test_validate_oneof(self):
        node = colander.SchemaNode(colander.String(),
                                   validator=colander.OneOf(["one", "two"]))
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'string',
            'enum': ['one', 'two'],
        })

    def test_title(self):
        node = colander.SchemaNode(colander.String(), title='foo')
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'string',
            'title': 'foo',
        })

    def test_description(self):
        node = colander.SchemaNode(colander.String(),
                                   description='bar')
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'string',
            'description': 'bar',
        })


class IntegerConversionTest(unittest.TestCase):

    def test_sanity(self):
        node = colander.SchemaNode(colander.Integer())
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'integer',
        })

    def test_default(self):
        node = colander.SchemaNode(colander.Integer(), default=1)
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'integer',
            'default': 1,
        })

    def test_enum(self):
        node = colander.SchemaNode(colander.Integer(),
                                   validator=colander.OneOf([1, 2, 3, 4]))
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'integer',
            'enum': [1, 2, 3, 4],
        })

    def test_range(self):
        node = colander.SchemaNode(colander.Integer(),
                                   validator=colander.Range(111, 555))
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'integer',
            'minimum': 111,
            'maximum': 555,
        })


class DateTimeConversionTest(unittest.TestCase):

    def test_sanity(self):
        node = colander.SchemaNode(colander.DateTime())
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'string',
            'format': 'date-time',
        })


class MappingConversionTest(unittest.TestCase):

    def test_sanity(self):
        node = colander.MappingSchema()
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'object',
        })

    def test_required(self):
        class Mapping(colander.MappingSchema):
            foo = colander.SchemaNode(colander.String())

        node = Mapping()
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'object',
            'properties': {
                'foo': {
                    'title': 'Foo',
                    'type': 'string'
                }
            },
            'required': ['foo']
        })

    def test_not_required(self):
        class Mapping(colander.MappingSchema):
            foo = colander.SchemaNode(colander.String(),
                                      missing=colander.drop)

        node = Mapping()
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'object',
            'properties': {
                'foo': {
                    'title': 'Foo',
                    'type': 'string'
                }
            },
        })

    def test_nested_schema(self):

        class BaseMapping(colander.MappingSchema):
            foo = colander.SchemaNode(colander.String(),
                                      missing=colander.drop)

        class TopMapping(colander.MappingSchema):
            bar = BaseMapping(missing=colander.drop)


        node = TopMapping()
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'object',
            'properties': {
                'bar': {
                    'title': 'Bar',
                    'type': 'object',
                    'properties': {
                        'foo': {
                            'title': 'Foo',
                            'type': 'string'
                        }
                    }
                }
            },
        })

    def test_open_schema(self):
        class Mapping(colander.MappingSchema):
            foo = colander.SchemaNode(colander.String(),
                                      missing=colander.drop)
            @staticmethod
            def schema_type():
                return colander.Mapping(unknown='preserve')

        node = Mapping()
        ret = convert(node)
        self.assertDictEqual(ret, {
            'type': 'object',
            'properties': {
                'foo': {
                    'title': 'Foo',
                    'type': 'string'
                }
            },
            'additionalProperties': {}
        })


class SequenceConversionTest(unittest.TestCase):

    def primitive_sequence_test(self):

        class Integers(colander.SequenceSchema):
            num = colander.SchemaNode(colander.Integer())

        ret = convert(Integers)
        self.assertDictEqual(ret, {
            'type': 'array',
            'items': {
                'type': 'integer',
            },
        })

    def mapping_sequence_test(self):

        class BaseMapping(colander.MappingSchema):
            name = colander.SchemaNode(colander.String())
            number = colander.SchemaNode(colander.Integer())

        class BaseMappings(colander.SequenceSchema):
            base_mapping = BaseMapping()

        schema = BaseMappings()
        ret = convert(schema)

        self.assertDictEqual(ret, {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'title': 'Name',
                    },
                    'number': {
                        'type': 'integer',
                        'title': 'Number',
                    }
                },
                'required': ['name', 'number'],
                'title': 'Base Mapping',
            },
        })

