import unittest
import webtest

from pyramid import testing
from cornice import Service
from cornice.service import clear_services
from cornice.validators import colander_validator
from flex.core import validate

from .support import GetRequestSchema, PutRequestSchema, response_schemas
from cornice_swagger import CorniceSwagger


class AppTest(unittest.TestCase):

    def tearDown(self):
        clear_services()
        testing.tearDown()

    def setUp(self):
        service = Service('IceCream', '/icecream/{flavour}')

        @service.get(validators=(colander_validator, ),
                     schema=GetRequestSchema(),
                     response_schemas=response_schemas)
        def view_get(request):
            """Serve icecream"""
            return request.validated

        @service.put(validators=(colander_validator, ), schema=PutRequestSchema())
        def view_put(request):
            """Add flavour"""
            return request.validated

        api_service = Service('OpenAPI', '/api')

        @api_service.get()
        def api_get(request):
            swagger = CorniceSwagger([service, api_service])
            return swagger.generate('IceCreamAPI', '4.2')

        self.config = testing.setUp()
        self.config.include('cornice')
        self.config.include('cornice_swagger')
        self.config.add_cornice_service(service)
        self.config.add_cornice_service(api_service)
        self.app = webtest.TestApp(self.config.make_wsgi_app())

    def test_app_get(self):
        self.app.get('/icecream/strawberry')

    def test_app_put(self):
        body = {'id': 'chocolate', 'timestamp': 123, 'obj': {'my_precious': True}}
        headers = {'bar': 'foo'}
        self.app.put_json('/icecream/chocolate', body, headers=headers)

    def test_validate_spec(self):
        spec = self.app.get('/api').json
        validate(spec)


class AppSpecViewTest(unittest.TestCase):

    def tearDown(self):
        clear_services()
        testing.tearDown()

    def setUp(self):
        service = Service('IceCream', '/icecream/{flavour}')

        @service.get(validators=(colander_validator, ),
                     schema=GetRequestSchema(),
                     response_schemas=response_schemas)
        def view_get(request):
            """Serve icecream"""
            return request.validated

        self.config = testing.setUp()
        self.config.include('cornice')
        self.config.include('cornice_swagger')
        self.config.cornice_enable_openapi_view(
            title='IceCreamAPI',
            description="OpenAPI documentation",
            version='4.2'
        )
        self.config.add_cornice_service(service)
        self.app = webtest.TestApp(self.config.make_wsgi_app())

    def test_validate_spec(self):
        spec = self.app.get('/api-explorer/swagger.json').json
        validate(spec)


class AppUIViewTest(unittest.TestCase):

    def tearDown(self):
        clear_services()
        testing.tearDown()

    def setUp(self):
        service = Service('IceCream', '/icecream/{flavour}')

        @service.get(validators=(colander_validator, ),
                     schema=GetRequestSchema(),
                     response_schemas=response_schemas)
        def view_get(request):
            """Serve icecream"""
            return request.validated

        self.config = testing.setUp()
        self.config.include('cornice')
        self.config.include('cornice_swagger')
        self.config.cornice_enable_openapi_view(
            title='IceCreamAPI',
            description="OpenAPI documentation",
            version='4.2'
        )
        self.config.cornice_enable_openapi_explorer()
        self.config.add_cornice_service(service)
        self.app = webtest.TestApp(self.config.make_wsgi_app())

    def test_served_explorer(self):
        result = self.app.get('/api-explorer')
        'swagger-ui-bundle.js' in result.text
        'swagger-ui-standalone-preset.js' in result.text
        'swagger-ui.css' in result.text
        'SwaggerUIBundle' in result.text


class AppGoodRoutesTest(unittest.TestCase):

    def tearDown(self):
        clear_services()
        testing.tearDown()

    def setUp(self):
        service = Service('Ice Route', pyramid_route='ice_test')

        @service.get()
        def view_get(request):
            """Serve icecream"""
            return request.validated

        self.config = testing.setUp()
        self.config.add_route('ice_test', '/ice_test/{flavour}')
        self.config.include('cornice')
        self.config.include('cornice_swagger')
        self.config.add_cornice_service(service)
        self.services = [service]
        self.app = webtest.TestApp(self.config.make_wsgi_app())

    def test_route_explicit_registry(self):
        swagger = CorniceSwagger(
            self.services, pyramid_registry=self.config.registry)
        spec = swagger.generate('IceCreamAPI', '4.2')
        self.assertIn('/ice_test/{flavour}', spec['paths'])

    def test_route_fallback_registry(self):
        swagger = CorniceSwagger(self.services)
        spec = swagger.generate('IceCreamAPI', '4.2')
        self.assertIn('/ice_test/{flavour}', spec['paths'])


class AppBadRoutesTest(unittest.TestCase):

    def tearDown(self):
        clear_services()
        testing.tearDown()

    def setUp(self):
        service = Service('Ice Route', pyramid_route='ice_testXXX')
        self.config = testing.setUp()
        self.config.include('cornice')
        self.config.include('cornice_swagger')
        self.config.add_cornice_service(service)
        self.services = [service]
        self.app = webtest.TestApp(self.config.make_wsgi_app())

    def test_route(self):
        with self.assertRaises(ValueError):
            swagger = CorniceSwagger(self.services)
            swagger.generate('IceCreamAPI', '4.2')
