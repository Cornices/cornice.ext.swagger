import unittest

import colander

from cornice.validators import colander_validator, colander_body_validator

from cornice_swagger.swagger import ParameterHandler
from cornice_swagger.converters import convert_schema
from .support import BodySchema, PathSchema, QuerySchema, HeaderSchema


class SchemaParamConversionTest(unittest.TestCase):

    def setUp(self):
        self.handler = ParameterHandler()

    def test_sanity(self):
        node = colander.MappingSchema()
        params = self.handler.from_schema(node)
        self.assertEquals(params, [])

    def test_covert_with_body_validator_schema(self):
        node = BodySchema()
        validators = [colander_body_validator]
        params = self.handler.from_schema(node, validators)
        self.assertEquals(len(params), 1)

        expected = {
            'name': 'BodySchema',
            'in': 'body',
            'required': True,
            'schema': convert_schema(BodySchema(title='BodySchema'))
        }

        self.assertDictEqual(params[0], expected)

    def test_covert_body_with_request_validator_schema(self):

        class RequestSchema(colander.MappingSchema):
            body = BodySchema()

        node = RequestSchema()
        validators = [colander_validator]
        params = self.handler.from_schema(node, validators)
        self.assertEquals(len(params), 1)

        expected = {
            'name': 'BodySchema',
            'in': 'body',
            'required': True,
            'schema': convert_schema(BodySchema(title='BodySchema'))
        }

        self.assertDictEqual(params[0], expected)

    def test_covert_query_with_request_validator_schema(self):

        class RequestSchema(colander.MappingSchema):
            querystring = QuerySchema()

        node = RequestSchema()
        validators = [colander_validator]
        params = self.handler.from_schema(node, validators)
        self.assertEquals(len(params), 1)

        expected = {
            'name': 'foo',
            'in': 'query',
            'type': 'string',
            'required': False
        }
        self.assertDictEqual(params[0], expected)

    def test_covert_headers_with_request_validator_schema(self):

        class RequestSchema(colander.MappingSchema):
            headers = HeaderSchema()

        node = RequestSchema()
        validators = [colander_validator]
        params = self.handler.from_schema(node, validators)
        self.assertEquals(len(params), 1)

        expected = {
            'name': 'bar',
            'in': 'header',
            'type': 'string',
            'required': True,
        }
        self.assertDictEqual(params[0], expected)

    def test_covert_path_with_request_validator_schema(self):

        class RequestSchema(colander.MappingSchema):
            path = PathSchema()

        node = RequestSchema()
        validators = [colander_validator]
        params = self.handler.from_schema(node, validators)
        self.assertEquals(len(params), 1)

        expected = {
            'name': 'meh',
            'in': 'path',
            'type': 'string',
            'required': True,
            'default': 'default'
        }
        self.assertDictEqual(params[0], expected)

    def test_convert_multiple_with_request_validator_schema(self):

        class RequestSchema(colander.MappingSchema):
            body = BodySchema()
            path = PathSchema()
            querystring = QuerySchema()
            headers = HeaderSchema()

        node = RequestSchema()
        validators = [colander_validator]
        params = self.handler.from_schema(node, validators)

        names = [param['name'] for param in params]
        expected = ['BodySchema', 'foo', 'bar', 'meh']
        self.assertEqual(sorted(names), sorted(expected))

    def test_convert_descriptions(self):
        class RequestSchema(colander.MappingSchema):
            body = BodySchema(description='my body')

        node = RequestSchema()
        validators = [colander_validator]
        params = self.handler.from_schema(node, validators)

        expected = {
            'name': 'BodySchema',
            'in': 'body',
            'required': True,
            'description': 'my body',
            'schema': convert_schema(BodySchema(title='BodySchema',
                                                description='my body'))
        }

        self.assertDictEqual(params[0], expected)


class PathParamConversionTest(unittest.TestCase):

    def setUp(self):
        self.handler = ParameterHandler()

    def test_from_path(self):
        params = self.handler.from_path('/my/{param}/path/{id}')
        names = [param['name'] for param in params]
        expected = ['param', 'id']
        self.assertEqual(sorted(names), sorted(expected))
        for param in params:
            self.assertEquals(param['in'], 'path')


class RefParamTest(unittest.TestCase):

    def setUp(self):
        self.handler = ParameterHandler(ref=1)
        self.handler.parameters = {}

    def test_ref_from_path(self):
        params = self.handler.from_path('/path/{id}')
        expected = {
            'name': 'id',
            'in': 'path',
            'type': 'string',
            'required': True,
        }

        self.assertEquals(params, [{'$ref': '#/parameters/id'}])
        self.assertDictEqual(self.handler.parameter_registry, dict(id=expected))

    def test_ref_from_body_validator_schema(self):
        node = BodySchema()
        validators = [colander_body_validator]
        params = self.handler.from_schema(node, validators)

        expected = {
            'name': 'BodySchema',
            'in': 'body',
            'required': True,
            'schema': convert_schema(BodySchema(title='BodySchema'))
        }

        self.assertEquals(params, [{'$ref': '#/parameters/BodySchema'}])
        self.assertDictEqual(self.handler.parameter_registry, dict(BodySchema=expected))

    def test_ref_from_request_validator_schema(self):

        class RequestSchema(colander.MappingSchema):
            querystring = QuerySchema()

        node = RequestSchema()
        validators = [colander_validator]
        params = self.handler.from_schema(node, validators)

        expected = {
            'name': 'foo',
            'in': 'query',
            'type': 'string',
            'required': False
        }

        self.assertEquals(params, [{'$ref': '#/parameters/foo'}])
        self.assertDictEqual(self.handler.parameter_registry, dict(foo=expected))
