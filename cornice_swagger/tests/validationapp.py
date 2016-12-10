from colander import (Invalid, MappingSchema, SequenceSchema, SchemaNode,
                      String, Integer, Range)


def validate_bar(node, value):
    if value != 'open':
        raise Invalid(node, "The bar is not open.")


class Integers(SequenceSchema):
    integer = SchemaNode(Integer(), type='int')


class Body(MappingSchema):
    # foo and bar are required, baz is optional
    foo = SchemaNode(String())
    bar = SchemaNode(String(), validator=validate_bar)
    baz = SchemaNode(String(), missing=None)
    ipsum = SchemaNode(Integer(), missing=1, validator=Range(0, 3))
    integers = Integers(missing=())


class Query(MappingSchema):
    yeah = SchemaNode(String(), description="Defines querystring yeah")
    mau = SchemaNode(String())


class RequestSchema(MappingSchema):
    body = Body(description="Defines a cornice body schema")
    querystring = Query()

    def deserialize(self, cstruct):
        if 'body' in cstruct and cstruct['body'] == b'hello,open,yeah':
            values = cstruct['body'].decode().split(',')
            cstruct['body'] = dict(zip(['foo', 'bar', 'yeah'], values))

        return MappingSchema.deserialize(self, cstruct)
