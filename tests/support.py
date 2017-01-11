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
