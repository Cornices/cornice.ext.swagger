import unittest

import colander
from cornice.validators import colander_validator
from cornice.service import Service

from cornice_swagger.swagger import CorniceSwagger
from .support import BodySchema, QuerySchema


class GetRequestSchema(colander.MappingSchema):
    querystring = QuerySchema()


class PutRequestSchema(colander.MappingSchema):
    querystring = QuerySchema()
    body = BodySchema()


class TestCorniceSwaggerGenerator(unittest.TestCase):

    def setUp(self):

        service = Service("IceCream", "/icecream/{flavour}")

        class IceCream(object):
            """
            Ice cream service
            """

            @service.get(validators=(colander_validator, ), schema=GetRequestSchema())
            def view_get(self, request):
                """Serve icecream"""
                return self.request.validated

            @service.put(validators=(colander_validator, ), schema=PutRequestSchema())
            def view_put(self, request):
                """Add flavour"""
                return self.request.validated

        self.service = service
        self.swagger = CorniceSwagger([self.service])
        self.spec = self.swagger('IceCreamAPI', '4.2')

    def test_path(self):
        self.assertIn('/icecream/{flavour}', self.spec['paths'])

    def test_path_methods(self):
        path = self.spec['paths']['/icecream/{flavour}']
        self.assertIn('get', path)
        self.assertIn('put', path)

    def test_path_parameters(self):
        parameters = self.spec['paths']['/icecream/{flavour}']['parameters']
        self.assertEquals(len(parameters), 1)
        self.assertEquals(parameters[0]['name'], 'flavour')

    def test_path_default_tags(self):
        tags = self.spec['paths']['/icecream/{flavour}']['get']['tags']
        self.assertEquals(tags, ['icecream'])

    def test_with_schema_ref(self):
        swagger = CorniceSwagger([self.service], def_ref_depth=1)
        spec = swagger('IceCreamAPI', '4.2')
        self.assertIn('definitions', spec)

    def test_with_param_ref(self):
        swagger = CorniceSwagger([self.service], param_ref=True)
        spec = swagger('IceCreamAPI', '4.2')
        self.assertIn('parameters', spec)


class TestExtractContentTypes(unittest.TestCase):

    def test_json_renderer(self):

        service = Service("IceCream", "/icecream/{flavour}")

        class IceCream(object):
            """Ice cream service"""
            @service.get(validators=(colander_validator, ), schema=GetRequestSchema(),
                         renderer='json')
            def view_get(self, request):
                """Serve icecream"""
                return self.request.validated

        swagger = CorniceSwagger([service])
        spec = swagger('IceCreamAPI', '4.2')
        self.assertEquals(spec['paths']['/icecream/{flavour}']['get']['produces'],
                          ['application/json'])

    def test_xml_renderer(self):

        service = Service("IceCream", "/icecream/{flavour}")

        class IceCream(object):
            """Ice cream service"""
            @service.get(validators=(colander_validator, ), schema=GetRequestSchema(),
                         renderer='xml')
            def view_get(self, request):
                """Serve icecream"""
                return self.request.validated

        swagger = CorniceSwagger([service])
        spec = swagger('IceCreamAPI', '4.2')
        self.assertEquals(spec['paths']['/icecream/{flavour}']['get']['produces'],
                          ['text/xml'])

    def test_unkown_renderer(self):

        service = Service("IceCream", "/icecream/{flavour}")

        class IceCream(object):
            """Ice cream service"""
            @service.get(validators=(colander_validator, ), schema=GetRequestSchema(),
                         renderer='')
            def view_get(self, request):
                """Serve icecream"""
                return self.request.validated

        swagger = CorniceSwagger([service])
        spec = swagger('IceCreamAPI', '4.2')
        self.assertNotIn('produces', spec['paths']['/icecream/{flavour}']['get'])

    def test_ctypes(self):

        service = Service("IceCream", "/icecream/{flavour}")

        class IceCream(object):
            """Ice cream service"""
            @service.put(validators=(colander_validator, ), schema=GetRequestSchema(),
                         content_type=['application/json'])
            def view_put(self, request):
                """Serve icecream"""
                return self.request.validated

        swagger = CorniceSwagger([service])
        spec = swagger('IceCreamAPI', '4.2')
        self.assertEquals(spec['paths']['/icecream/{flavour}']['put']['consumes'],
                          ['application/json'])

    def test_multiple_views_with_different_ctypes(self):

        service = Service("IceCream", "/icecream/{flavour}")

        class IceCream(object):
            """Ice cream service"""

            def view_put(self, request):
                """Serve icecream"""
                return "red"

        service.add_view(
            "put",
            IceCream.view_put,
            validators=(colander_validator, ),
            schema=PutRequestSchema(),
            content_type=['application/json'],
        )
        service.add_view(
            "put",
            IceCream.view_put,
            validators=(colander_validator, ),
            schema=PutRequestSchema(),
            content_type=['text/xml'],
        )

        swagger = CorniceSwagger([service])
        spec = swagger('IceCreamAPI', '4.2')
        self.assertEquals(spec['paths']['/icecream/{flavour}']['put']['produces'],
                          ['application/json'])
