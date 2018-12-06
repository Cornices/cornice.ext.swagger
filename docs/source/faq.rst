Frequently Asked Questions (FAQ)
################################

Here is a list of frequently asked questions related to Cornice Swagger.

How to make a schema parameter not required?
============================================

You may use ``colander.drop`` as it's missing field::

    field = colander.SchemaNode(colander.String(), missing=colander.drop)


How to define a schema with additionalAttributes?
=================================================

You can use ``Mapping.unknown`` attribute ::

    class Query(colander.MappingSchema):
        unknown='preserve'


How do I integrate Swagger UI?
==============================

The fastest way to enable Swagger UI is to use directives
``cornice_enable_openapi_view`` together with
``cornice_enable_openapi_explorer`` they will provide a special view in your
application that will server the OpenAPI specification along with API explorer.


How do I work with colander schemas that require bound properties?
==================================================================

A common scenario is to have schemas that have optional fields that
substitute default values when fields are missing from request data.
This is normally solved by calling `bind()` on colander schemas,
one thing that is important to remember is that if the value
needs to be updated per request (like a date or UUID), you need to bind the
schema per request. At the same time for ``cornice_swagger`` to get proper
values when inspecting schema you also need to bind it on decorator level.
Here is an example how to solve this problem:

.. code:: python

    @colander.deferred
    def deferred_conn_id(node, kw):
        return kw.get('conn_id') or str(uuid.uuid4())


    class SomeSchema(colander.MappingSchema):
        username = colander.SchemaNode(colander.String())
        conn_id = colander.SchemaNode(
            colander.String(), missing=deferred_conn_id)


    def rebind_schema(schema):
        """
        Ensure we bind schema per request
        """
        def deferred_validator(request, **kwargs):
            # we need to regenerate the schema here
            kwargs['schema'] = schema().bind(request=request)
            return colander_validator(request, **kwargs)
        return deferred_validator


    @legacy_connect_api.post(
        schema=SomeSchema().bind(), validators=(rebind_schema(SomeSchema),))
    def connect(request):
        ...
