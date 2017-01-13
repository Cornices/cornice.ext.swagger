.. _quickstart:

Quickstart
##########

Installing
==========

You may install us with pip::

    $ pip install cornice_swagger


From an existing Cornice application, you may create you OpenAPI/Swagger JSON using:

.. code-block:: python

    from cornice_swagger.swagger import CorniceSwagger
    from cornice.service import get_services

    my_generator = CorniceSwagger(get_services())
    my_spec = my_generator('MyAPI', '1.0.0')


Show me a minimalist useful example
===================================

.. code-block:: python

    import colander
    from cornice import Service
    from cornice.service import get_services
    from cornice.validators import colander_body_validator
    from wsgiref.simple_server import make_server
    from pyramid.config import Configurator
    from cornice_swagger.swagger import CorniceSwagger

    _VALUES = {}

    # Create a simple service that will store and retrieve values
    values = Service(name='foo',
                     path='/values/{value}',
                     description="Cornice Demo")


    # Create a request schema for storing values
    class PutBodySchema(colander.MappingSchema):
        value = colander.SchemaNode(colander.String(),
                                    description='My precious value')


    # Create our cornice service views
    class MyValueApi(object):
        """My precious API."""

        @values.get()
        def get_value(request):
            """Returns the value."""
            key = request.matchdict['value']
            return _VALUES.get(key)

        @values.put(validators=(colander_body_validator, ),
                    schema=PutBodySchema())
        def set_value(request):
            """Set the value and returns *True* or *False*."""

            key = request.matchdict['value']
            try:
                _VALUES[key] = request.json_body
            except ValueError:
                return False
            return True


    # Create a service to serve our OpenAPI spec
    swagger = Service(name='OpenAPI',
                      path='/__api__',
                      description="OpenAPI documentation")


    @swagger.get()
    def openAPI_spec(request):
        my_generator = CorniceSwagger(get_services())
        my_spec = my_generator('MyAPI', '1.0.0')
        return my_spec


    # Setup and run our app
    def setup():
        config = Configurator()
        config.include("cornice")
        config.scan()
        app = config.make_wsgi_app()
        return app


    if __name__ == '__main__':
        app = setup()
        server = make_server('127.0.0.1', 8000, app)
        server.serve_forever()


The resulting `swagger.json` at `http://localhost:8000/__api__` is:

.. code-block:: json

    {
        "swagger": "2.0",
        "info": {
            "version": "1.0.0",
            "title": "MyAPI"
        },
        "basePath": "/",
        "tags": [
            {
                "name": "values"
            },
            {
                "name": "__api__"
            }
        ]
        "paths": {
            "/values/{value}": {
                "parameters": [
                    {
                        "name": "value",
                        "in": "path",
                        "required": true,
                        "type": "string"
                    }
                ],
                "get": {
                    "summary": "Returns the value.",
                    "responses": {
                        "default": {
                            "description": "UNDOCUMENTED RESPONSE"
                        }
                    },
                    "tags": [
                        "values"
                    ],
                    "produces": [
                        "application/json"
                    ]
                },
                "put": {
                    "tags": [
                        "values"
                    ],
                    "summary": "Set the value and returns *True* or *False*.",
                    "responses": {
                        "default": {
                            "description": "UNDOCUMENTED RESPONSE"
                        }
                    },
                    "parameters": [
                        {
                            "name": "PutBodySchema",
                            "in": "body",
                            "schema": {
                                "required": [
                                    "value"
                                ],
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "type": "string",
                                        "description": "My precious value",
                                        "title": "Value"
                                    }
                                },
                                "title": "PutBodySchema"
                            },
                            "required": true
                        }
                    ],
                    "produces": [
                        "application/json"
                    ]
                }
            },
            "/__api__": {
                "get": {
                    "tags": [
                        "__api__"
                    ],
                    "responses": {
                        "default": {
                            "description": "UNDOCUMENTED RESPONSE"
                        }
                    },
                    "produces": [
                        "application/json"
                    ]
                }
            }
        }
    }

