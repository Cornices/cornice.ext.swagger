import unittest

import colander

from cornice_swagger.swagger import ResponseHandler, CorniceSwaggerException
from cornice_swagger.converters import convert_schema
from .support import BodySchema, HeaderSchema


class ResponseSchema(colander.MappingSchema):
    body = BodySchema()
    headers = HeaderSchema()


class GetResponses(colander.MappingSchema):
    ok = ResponseSchema(description='Yaay', name='200')
    not_found = ResponseSchema(description='Nooo', name='404')


class SchemaResponseConversionTest(unittest.TestCase):

    def setUp(self):
        self.handler = ResponseHandler()

    def test_sanity(self):
        self.handler.from_schema(GetResponses())

    def test_status_codes(self):
        responses = self.handler.from_schema(GetResponses())
        self.assertIn('200', responses)
        self.assertIn('404', responses)
        self.assertEquals(responses['200']['description'], 'Yaay')
        self.assertEquals(responses['404']['description'], 'Nooo')

    def test_response_schema(self):
        responses = self.handler.from_schema(GetResponses())
        self.assertDictEqual(responses['200']['schema'],
                             convert_schema(BodySchema(title='BodySchema')))
        self.assertDictEqual(responses['200']['headers'],
                             convert_schema(HeaderSchema())['properties'])

    def test_raise_exception_without_description(self):

        class GetResponses(colander.MappingSchema):
            ok = ResponseSchema(name='200')

        self.assertRaises(CorniceSwaggerException,
                          self.handler.from_schema, GetResponses())


class RefResponseTest(unittest.TestCase):

    def setUp(self):
        self.handler = ResponseHandler(ref=1)
        self.handler.responses = {}

    def test_from_schema(self):
        responses = self.handler.from_schema(GetResponses())
        expected = {
            '200': {'$ref': '#/responses/ResponseSchema'},
            '404': {'$ref': '#/responses/ResponseSchema'}
        }
        self.assertEquals(expected, responses)
        ref = self.handler.responses['ResponseSchema']
        self.assertDictEqual(ref['schema'],
                             convert_schema(BodySchema(title='BodySchema')))
        self.assertDictEqual(ref['headers'],
                             convert_schema(HeaderSchema())['properties'])
