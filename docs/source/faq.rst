Frequently Asked Questions (FAQ)
################################

Here is a list of frequently asked questions related to Cornice Swagger.

How to make a schema parameter not required?
============================================

You may use ``colader.drop`` as it's missing field::

    field = colader.SchemaNode(colander.String(), missing=colader.drop)


How to define a schema with additionalAttributes?
=================================================

You can use ``Mapping.unknown`` attribute ::

    class Query(colander.MappingSchema):
        unknown='preserve'

