import unittest
import webtest

from pyramid import testing
from cornice import Service
from cornice.validators import colander_validator
from flex.core import validate

from .support import GetRequestSchema, PutRequestSchema, response_schemas
from cornice_swagger.swagger import CorniceSwagger


class AppTest(unittest.TestCase):

    def setUp(self):
        service = Service('IceCream', '/icecream/{flavour}')

        class IceCream(object):
            """
            Ice cream service
            """

            @service.get(validators=(colander_validator, ),
                         schema=GetRequestSchema(),
                         response_schemas=response_schemas)
            def view_get(self, request):
                """Serve icecream"""
                return self.request.validated

            @service.put(validators=(colander_validator, ), schema=PutRequestSchema())
            def view_put(self, request):
                """Add flavour"""
                return self.request.validated

        api_service = Service('OpenAPI', '/api')

        @api_service.get()
        def api_get(request):
            swagger = CorniceSwagger([service, api_service])
            return swagger('IceCreamAPI', '4.2')

        self.config = testing.setUp()
        self.config.include('cornice')
        self.config.include('cornice_swagger')
        self.config.add_cornice_service(service)
        self.config.add_cornice_service(api_service)
        self.app = webtest.TestApp(self.config.make_wsgi_app())

    def test_validate_spec(self):
        spec = self.app.get('/api').json
        validate(spec)
