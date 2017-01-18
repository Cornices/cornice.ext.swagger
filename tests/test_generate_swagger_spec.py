import unittest

from cornice.resource import resource, view
from cornice.service import Service, clear_services, get_services
from flex.core import validate

from cornice_swagger.swagger import generate_swagger_spec
from cornice.validators import colander_validator
from .validationapp import RequestSchema


def _generate_swagger(services):
    info = {
        'title': 'Joes API',
        'version': '0.1',
        'contact': {
            'name': 'Joe Smith',
            'email': 'joe.cool@swagger.com'
        }
    }
    base_path = '/jcool'
    spec = generate_swagger_spec(
        services,
        info['title'],
        info['version'],
        info=info,
        basePath=base_path)

    validate(spec)
    return spec


class TestSwaggerService(unittest.TestCase):
    def tearDown(self):
        clear_services()

    def test_with_klass(self):
        class TemperatureCooler(object):
            """Temp class docstring"""

            def put_view(self):
                """Temp view docstring"""
                pass

        service = Service(
            "TemperatureCooler", "/freshair", klass=TemperatureCooler)
        service.add_view(
            "put",
            "put_view",
            validators=(colander_validator, ),
            schema=RequestSchema())
        ret = _generate_swagger([service])
        self.assertEqual(ret["info"], {
            'version': '0.1',
            'contact': {
                'name': 'Joe Smith',
                'email': 'joe.cool@swagger.com'
            },
            'title': 'Joes API'
        })
        self.assertEqual(ret["basePath"], '/jcool')
        self.assertEqual(ret["swagger"], '2.0')
        self.assertEqual(ret["tags"], [{'name': 'freshair'}])
        self.assertEqual(ret["paths"]["/freshair"]["put"]["summary"],
                         'Temp view docstring')
        params = ret["paths"]["/freshair"]["put"]['parameters']
        self.assertEqual(len(params), 3)
        params = ret["paths"]["/freshair"]["put"]['parameters']
        self.assertEqual(
            sorted(x["in"] for x in params), ["body", "query", "query"])
        self.assertEqual(
            sorted(x["name"] for x in params), ["Body", "mau", "yeah"])
        self.assertEqual([x.get("required") for x in params],
                         [True, True, True])
        self.assertEqual([x.get("type") for x in params],
                         [None, "string", "string"])
        self.assertEqual([x.get("schema") for x in params],
                         [{
                             '$ref': '#/definitions/Body'
                         }, None, None])
        self.assertEqual(
         sorted([x.get("description") for x in params], key=lambda x: x or ""),
         [None, "Defines a cornice body schema", "Defines querystring yeah"]
        )

        self.assertEqual(
            sorted(ret["definitions"]['Body']["required"]), ['bar', 'foo'])

    def test_declerative(self):
        service = Service("TemperatureCooler", "/freshair")

        class TemperatureCooler(object):
            """Temp class docstring"""

            @service.get(validators=(colander_validator, ),
                         schema=RequestSchema())
            def view_get(self, request):
                """Temp view docstring"""
                return "red"

        ret = _generate_swagger([service])
        self.assertEqual(ret["tags"], [{'name': 'freshair'}])
        self.assertEqual(ret["paths"]["/freshair"]["get"]["summary"],
                         'Temp view docstring')
        params = ret["paths"]["/freshair"]["get"]['parameters']
        self.assertEqual(len(params), 3)
        self.assertEqual(
            sorted(x["in"] for x in params), ["body", "query", "query"])
        self.assertEqual(
            sorted(x["name"] for x in params), ["Body", "mau", "yeah"])
        self.assertEqual([x.get("required") for x in params],
                         [True, True, True])
        self.assertEqual([x.get("type") for x in params],
                         [None, "string", "string"])
        self.assertEqual([x.get("schema") for x in params],
                         [{
                             '$ref': '#/definitions/Body'
                         }, None, None])
        self.assertEqual(
         sorted([x.get("description") for x in params], key=lambda x: x or ""),
         [None, "Defines a cornice body schema", "Defines querystring yeah"]
        )
        self.assertEqual(
            sorted(ret["definitions"]['Body']["required"]), ['bar', 'foo'])

    def test_imperative(self):
        service = Service("TemperatureCooler", "/freshair")

        class TemperatureCooler(object):
            """Temp class docstring"""

            def view_put(self, request):
                """Temp view docstring"""
                return "red"

        service.add_view(
            "put",
            TemperatureCooler.view_put,
            validators=(colander_validator, ),
            schema=RequestSchema())
        ret = _generate_swagger([service])
        self.assertEqual(ret["tags"], [{'name': 'freshair'}])
        self.assertEqual(ret["paths"]["/freshair"]["put"]["summary"],
                         'Temp view docstring')
        params = ret["paths"]["/freshair"]["put"]['parameters']
        self.assertEqual(len(params), 3)
        self.assertEqual(
            sorted(x["in"] for x in params), ["body", "query", "query"])
        self.assertEqual(
            sorted(x["name"] for x in params), ["Body", "mau", "yeah"])
        self.assertEqual([x.get("required") for x in params],
                         [True, True, True])
        self.assertEqual([x.get("type") for x in params],
                         [None, "string", "string"])
        self.assertEqual([x.get("schema") for x in params],
                         [{
                             '$ref': '#/definitions/Body'
                         }, None, None])
        self.assertListEqual(
         sorted([x.get("description") for x in params], key=lambda x: x or ""),
         [None, "Defines a cornice body schema", "Defines querystring yeah"]
        )
        self.assertEqual(
            sorted(ret["definitions"]['Body']["required"]), ['bar', 'foo'])

    def test_schema_not_instantiated(self):
        class TemperatureCooler(object):
            """Temp class docstring"""

            def get_view(self):
                """Temp view docstring"""
                pass

        service = Service(
            "TemperatureCooler", "/freshair", klass=TemperatureCooler)
        service.add_view(
            "get",
            "get_view",
            validators=(colander_validator, ),
            schema=RequestSchema)
        ret = _generate_swagger([service])
        self.assertEqual(ret["info"], {
            'version': '0.1',
            'contact': {
                'name': 'Joe Smith',
                'email': 'joe.cool@swagger.com'
            },
            'title': 'Joes API'
        })
        self.assertEqual(ret["basePath"], '/jcool')


class TestSwaggerResource(unittest.TestCase):
    def tearDown(self):
        clear_services()

    def test_resource(self):
        @resource(
            collection_path='/users', path='/users/{id}', name='user_service')
        class User(object):
            def __init__(self, request, context=None):
                self.request = request
                self.context = context

            def collection_get(self):
                return {'users': [1, 2, 3]}

            @view(
                renderer='json',
                content_type='application/json',
                schema=RequestSchema())
            def collection_post(self):
                return {'test': 'yeah'}

        services = get_services()
        ret = _generate_swagger(services)

        self.assertEqual(
            sorted(ret["paths"].keys()), [
                '/users',
                '/users/{id}',
            ])

        self.assertEqual(
            sorted(ret["definitions"]['Body']["required"]), ['bar', 'foo'])
