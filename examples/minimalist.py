import colander
from cornice import Service
from cornice.validators import colander_body_validator
from wsgiref.simple_server import make_server
from pyramid.config import Configurator


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


# Setup and run our app
def setup():
    config = Configurator()
    config.include('cornice')
    config.include('cornice_swagger')
    # Create views to serve our OpenAPI spec
    config.cornice_enable_openapi_view(
        api_path='/__api__',
        title='MyAPI',
        description="OpenAPI documentation",
        version='1.0.0'
    )
    # Create views to serve OpenAPI spec UI explorer
    config.cornice_enable_openapi_explorer(api_explorer_path='/api-explorer')
    config.scan()
    app = config.make_wsgi_app()
    return app


if __name__ == '__main__':
    app = setup()
    server = make_server('127.0.0.1', 8000, app)
    print('Visit me on http://127.0.0.1:8000')
    print('''You can see the API explorer here:
    http://127.0.0.1:8000/api-explorer''')
    server.serve_forever()
