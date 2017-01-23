.. _quickstart:

Quickstart
##########

Installing
==========

You may install us with pip::

    $ pip install cornice_swagger


From an existing Cornice application, you may add this extension to your
Pyramid configurator after including cornice::

    from pyramid.config import Configurator

    def setup():
        config = Configurator()
        config.include('cornice')
        config.include('cornice_swagger')


You can than create your OpenAPI/Swagger JSON using::


    from cornice_swagger import CorniceSwagger
    from cornice.service import get_services

    my_generator = CorniceSwagger(get_services())
    my_spec = my_generator('MyAPI', '1.0.0')


Using a scaffold
================

If you want to start a new project, there is a cookiecutter scaffold that can be used::

   $ cookiecutter https://github.com/delijati/cookiecutter-cornice_swagger.git
   $ cd demo
   $ pip install -e .
   $ cd demo/static
   $ bower install



Show me a minimalist useful example
===================================

.. literalinclude:: ../../examples/minimalist.py
    :language: python


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
            }
        ]
        "paths": {
            "/values/{key}": {
                "parameters": [
                    {
                        "name": "value",
                        "in": "path",
                        "required": true,
                        "type": "string"
                    }
                ],
                "get": {
                    "tags": [
                        "values"
                    ],
                    "responses": {
                        "200": {
                            "description": "Return value",
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
                                "title": "BodySchema"
                            }
                        }

                    },
                    "produces": [
                        "application/json"
                    ]
                },
                "put": {
                    "tags": [
                        "values"
                    ],
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
                    ],
                    "responses": {
                        "200": {
                            "description": "Return value",
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
                                "title": "BodySchema"
                            }
                        }
                    }
                }
            },
            "/__api__": {
                "get": {
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

