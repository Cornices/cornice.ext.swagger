import colander
from cornice import Service
from cornice.service import get_services
from cornice.validators import colander_body_validator
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from cornice_swagger import CorniceSwagger


_VALUES = {}


# Create a simple service that will store and retrieve values
values = Service(name='foo',
                 path='/values/{key}',
                 description="Cornice Demo")


# Create a body schema for our requests
class BodySchema(colander.MappingSchema):
    value = colander.SchemaNode(colander.String(),
                                description='My precious value')


# Create a response schema for our 200 responses
class OkResponseSchema(colander.MappingSchema):
    body = BodySchema()


# Aggregate the response schemas for get requests
response_schemas = {
    '200': OkResponseSchema(description='Return value')
}


# Create our cornice service views
class MyValueApi(object):
    """My precious API."""

    @values.get(tags=['values'], response_schemas=response_schemas)
    def get_value(request):
        """Returns the value."""
        key = request.matchdict['key']
        return _VALUES.get(key)

    @values.put(tags=['values'], validators=(colander_body_validator, ),
                schema=BodySchema(), response_schemas=response_schemas)
    def set_value(request):
        """Set the value and returns *True* or *False*."""

        key = request.matchdict['key']
        _VALUES[key] = request.json_body
        return _VALUES.get(key)


# Create a service to serve our OpenAPI spec
swagger = Service(name='OpenAPI',
                  path='/__api__',
                  description="OpenAPI documentation")


@swagger.get()
def openAPI_spec(request):
    doc = CorniceSwagger(get_services())
    my_spec = doc.generate('MyAPI', '1.0.0')
    return my_spec


# Setup and run our app
def setup():
    config = Configurator()
    config.include('cornice')
    config.include('cornice_swagger')
    config.scan()
    app = config.make_wsgi_app()
    return app


if __name__ == '__main__':
    app = setup()
    server = make_server('127.0.0.1', 8000, app)
    server.serve_forever()
