from cornice.resource import resource, view
from cornice.service import Service, clear_services, get_services
from cornice_swagger.tests.support import TestCase
from cornice_swagger.swagger import generate_swagger_spec
from cornice_swagger.util import PY3
from cornice.validators import colander_validator
from cornice_swagger.tests.validationapp import RequestSchema


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
    return spec


class TestSwaggerService(TestCase):
    def tearDown(self):
        clear_services()

    def test_with_klass(self):
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
        self.assertEqual(ret["tags"], [{
            'name': 'freshair',
            'description': 'Temp class docstring'
        }])
        self.assertEqual(ret["paths"]["/freshair"]["get"]["summary"],
                         'Temp view docstring')
        params = ret["paths"]["/freshair"]["get"]['parameters']
        self.assertEqual(len(params), 3)
        params = ret["paths"]["/freshair"]["get"]['parameters']
        self.assertEqual(
            sorted(x["in"] for x in params), ["body", "query", "query"])
        self.assertEqual(
            sorted(x["name"] for x in params), ["body", "mau", "yeah"])
        self.assertEqual([x.get("required") for x in params],
                         [True, True, None])
        self.assertEqual([x.get("type") for x in params],
                         ["string", "string", None])
        self.assertEqual([x.get("schema") for x in params],
                         [None, None, {
                             '$ref': '#/definitions/Body'
                         }])
        self.assertEqual([x.get("description") for x in params],
                         [None, None, "Defines a cornice body schema"])

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
        self.assertEqual(ret["tags"], [{
            'name': 'freshair',
            'description': ''
        }])
        self.assertEqual(ret["paths"]["/freshair"]["get"]["summary"],
                         'Temp view docstring')
        params = ret["paths"]["/freshair"]["get"]['parameters']
        self.assertEqual(len(params), 3)
        self.assertEqual(
            sorted(x["in"] for x in params), ["body", "query", "query"])
        self.assertEqual(
            sorted(x["name"] for x in params), ["body", "mau", "yeah"])
        self.assertEqual([x.get("required") for x in params],
                         [True, True, None])
        self.assertEqual([x.get("type") for x in params],
                         ["string", "string", None])
        self.assertEqual([x.get("schema") for x in params],
                         [None, None, {
                             '$ref': '#/definitions/Body'
                         }])
        self.assertEqual([x.get("description") for x in params],
                         [None, None, "Defines a cornice body schema"])
        self.assertEqual(
            sorted(ret["definitions"]['Body']["required"]), ['bar', 'foo'])

    def test_imperative(self):
        service = Service("TemperatureCooler", "/freshair")

        class TemperatureCooler(object):
            """Temp class docstring"""

            def view_get(self, request):
                """Temp view docstring"""
                return "red"

        service.add_view(
            "get",
            TemperatureCooler.view_get,
            validators=(colander_validator, ),
            schema=RequestSchema())
        ret = _generate_swagger([service])
        if PY3:
            self.assertEqual(ret["tags"], [{
                'name': 'freshair',
                'description': ''
            }])
        else:
            self.assertEqual(ret["tags"], [{
                'name': 'freshair',
                'description': 'Temp class docstring'
            }])
        self.assertEqual(ret["paths"]["/freshair"]["get"]["summary"],
                         'Temp view docstring')
        params = ret["paths"]["/freshair"]["get"]['parameters']
        self.assertEqual(len(params), 3)
        self.assertEqual(
            sorted(x["in"] for x in params), ["body", "query", "query"])
        self.assertEqual(
            sorted(x["name"] for x in params), ["body", "mau", "yeah"])
        self.assertEqual([x.get("required") for x in params],
                         [True, True, None])
        self.assertEqual([x.get("type") for x in params],
                         ["string", "string", None])
        self.assertEqual([x.get("schema") for x in params],
                         [None, None, {
                             '$ref': '#/definitions/Body'
                         }])
        self.assertEqual([x.get("description") for x in params],
                         [None, None, "Defines a cornice body schema"])
        self.assertEqual(
            sorted(ret["definitions"]['Body']["required"]), ['bar', 'foo'])


class TestSwaggerResource(TestCase):
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
