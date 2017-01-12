.. _tutorial:

Here you may find the general aspects used by Colander Swagger to generate
the swagger documentation. Most examples presented on this section refer
to the example on `quickstart`.

Generating summaries with view docstrings
=========================================

You may use view docstrings to create operation summaries. For example,
the following view definition docstring will correspond to the following
swagger summary:

.. code-block:: python

    values = Service(name='foo',
                     path='/values')

    @values.get()
    def get_value(request):
        """Returns the value."""


.. code-block:: json

    {
        "paths": {
            "/values": {
                "get": {
                    "summary": "Returns the value."
                }
            }
        }
    }


Extracting path parameters
==========================

Path parameters may be automatically extracted from the service definition,
you may overwrite then with schemas on the view if you wish to add more
view-specific information.

Another example:

.. code-block:: python

    values = Service(name='foo',
                     path='/values/{value}')


.. code-block:: json

    {
        "paths": {
            "/values/{value}": {
                "parameters": [
                    {
                        "name": "value",
                        "in": "path",
                        "required": true,
                        "type": "string"
                    }
                ]
            }
        }
    }


Extracting parameters from cornice schemas
==========================================

When using colander validators such as ``colader_validator`` or
``colander_body_validator``, we can extract the operation parameters
from the request schema. The schemas should comply with
`Cornice 2.0 colander schemas <https://cornice.readthedocs.io/en/latest/schema.html#multiple-request-attributes>`_.


.. code-block:: python

    from cornice.validators import colander_body_validator

    values = Service(name='foo',
                     path='/values/{value}')

    class PutBodySchema(colander.MappingSchema):
        value = colander.SchemaNode(colander.String(),
                                    description='My precious value')


    @values.put(validators=(colander_body_validator, ),
                schema=PutBodySchema())
    def set_value(request):
        """Set the value and returns *True* or *False*."""


.. code-block:: json

    {
        "paths": {
            "/values/{value}": {
                "put": {
                    "parameters": [
                        {
                            "name": "PutBodySchema",
                            "in": "body",
                            "required": true,
                            "schema": {
                                "title": "PutBodySchema",
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "type": "string",
                                        "description": "My precious value",
                                        "title": "Value"
                                    }
                                },
                                "required": [
                                    "value"
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }


When using `colander_validator`, the request should have fields corresponding
the parameters locations as follows:


.. code-block:: python

    from cornice.validators import colander_body_validator

    class BodySchema(colander.MappingSchema):
        value = colander.SchemaNode(colander.String(),
                                    description='My precious value')


    class QuerySchema(colander.MappingSchema):
        foo = colander.SchemaNode(colander.String(), missing=colander.drop)


    class HeaderSchema(colander.MappingSchema):
        bar = colander.SchemaNode(colander.String(), default='blah')


    class PutRequestSchema(colander.MappingSchema):
        body = BodySchema()
        querystring = QuerySchema()
        header = HeaderSchema()


    @values.put(validators=(colander_validator, ),
                schema=PutRequestSchema())
    def set_value(request):
        """Set the value and returns *True* or *False*."""

