import unittest
import colander

from cornice_swagger.swagger import ResponseHandler, CorniceSwaggerException
from cornice_swagger.converters import convert_schema
from .support import (BodySchema, HeaderSchema, ResponseSchema, response_schemas,
                      DeclarativeSchema, AnotherDeclarativeSchema)


class SchemaResponseConversionTest(unittest.TestCase):

    def setUp(self):
        self.handler = ResponseHandler()

    def test_sanity(self):
        self.handler.from_schema_mapping(response_schemas)

    def test_status_codes(self):
        responses = self.handler.from_schema_mapping(response_schemas)
        self.assertIn('200', responses)
        self.assertIn('404', responses)
        self.assertEquals(responses['200']['description'], 'Return ice cream')
        self.assertEquals(responses['404']['description'], 'Return sadness')

    def test_response_schema(self):
        responses = self.handler.from_schema_mapping(response_schemas)
        self.assertDictEqual(responses['200']['schema'],
                             convert_schema(BodySchema(title='BodySchema')))
        self.assertDictEqual(responses['200']['headers'],
                             {'bar': {'type': 'string'}})

    def test_cornice_location_synonyms(self):

        class ReponseSchema(colander.MappingSchema):
            header = HeaderSchema()

        response_schemas = {'200': ReponseSchema(description='Return gelatto')}
        responses = self.handler.from_schema_mapping(response_schemas)

        self.assertDictEqual(responses['200']['headers'],
                             {'bar': {'type': 'string'}})

    def test_raise_exception_without_description(self):

        response_schemas = {
            '200': ResponseSchema()
        }

        self.assertRaises(CorniceSwaggerException,
                          self.handler.from_schema_mapping, response_schemas)


class RefResponseTest(unittest.TestCase):

    def setUp(self):
        self.handler = ResponseHandler(ref=1)
        self.handler.responses = {}

    def test_from_schema_mapping(self):
        responses = self.handler.from_schema_mapping(response_schemas)
        expected = {
            '200': {'$ref': '#/responses/ResponseSchema'},
            '404': {'$ref': '#/responses/ResponseSchema'}
        }
        self.assertEquals(expected, responses)
        ref = self.handler.response_registry['ResponseSchema']
        self.assertDictEqual(ref['schema'],
                             convert_schema(BodySchema(title='BodySchema')))
        self.assertDictEqual(ref['headers'],
                             {'bar': {'type': 'string'}})

    def test_declarative_response_schemas(self):

        self.handler.from_schema_mapping({
            '200': DeclarativeSchema(description='response schema')
        })

        self.handler.from_schema_mapping({
            '200': AnotherDeclarativeSchema(description='response schema')
        })

        ref = self.handler.response_registry['DeclarativeSchema']
        another_ref = self.handler.response_registry['AnotherDeclarativeSchema']

        self.assertNotEqual(ref['schema']['title'], another_ref['schema']['title'])
