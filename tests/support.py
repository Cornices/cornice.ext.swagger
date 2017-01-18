import colander


class MyNestedSchema(colander.MappingSchema):
    my_precious = colander.SchemaNode(colander.Boolean())


class BodySchema(colander.MappingSchema):
    id = colander.SchemaNode(colander.String())
    timestamp = colander.SchemaNode(colander.Int())
    obj = MyNestedSchema()


class QuerySchema(colander.MappingSchema):
    foo = colander.SchemaNode(colander.String(), missing=colander.drop)


class HeaderSchema(colander.MappingSchema):
    bar = colander.SchemaNode(colander.String())


class PathSchema(colander.MappingSchema):
    meh = colander.SchemaNode(colander.String(), default='default')


class GetRequestSchema(colander.MappingSchema):
    querystring = QuerySchema()


class PutRequestSchema(colander.MappingSchema):
    body = BodySchema()
    querystring = QuerySchema()
    headers = HeaderSchema()


class ResponseSchema(colander.MappingSchema):
    body = BodySchema()
    headers = HeaderSchema()


response_schemas = {
    '200': ResponseSchema(description='Return ice cream'),
    '404': ResponseSchema(description='Return sadness')
}
