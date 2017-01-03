"""Cornice Swagger 2.0 documentor"""

import re
import cornice_swagger.swagger_model
from cornice_swagger.swagger_model import convert
import cornice_swagger.util


class CorniceSwaggerException(Exception):
    pass


class CorniceSwagger(object):

    def __init__(self, services, def_ref_depth=0,
                                 param_ref_depth=0):

        self.services = services

        self.definitions = DefinitionHandler(ref_depth=def_ref_depth)
        self.parameters = ParameterHandler(self.definitions,
                                           ref_depth=param_ref_depth)

    def __call__(self, title, version, base_path='/', info={}, **kwargs):

        info.update(title=title, version=version)

        swagger = {
            'swagger': '2.0',
            'info': info,
            'basePath': base_path
        }

        paths, tags = self._build_paths(**kwargs)
        if paths:
            swagger['paths'] = paths
        if tags:
            swagger['tags'] = tags

        definitions = self.definitions.definitions
        if definitions:
            swagger['definitions'] = definitions

        parameters = self.parameters.parameters
        if parameters:
            swagger['parameters'] = parameters

        return swagger

    def _build_paths(self, sort=False, ignore=['head', 'options'], **kwargs):

        paths = {}
        tags = []

        for service in self.services:
            path = self._extract_path_from_service(service)

            for method_name, view, args in service.definitions:
                if method_name.lower() in ignore:
                    continue

                op = self._extract_operation_from_view(view, args)

                # XXX: If tag not defined, try to guess it from path
                default_tag = service.path.split("/")[1]
                op.setdefault('tags', [default_tag])

                if default_tag not in [t['name'] for t in tags]:
                    tag = {'name': default_tag}
                    tags.append(tag)

                # If method is defined for more than one ctype, get previous ones
                ctypes = path.get(method_name.lower(), {}).get('consumes')
                if ctypes:
                    op['consumes'].union(op.get('consumes'))
                    op['consumes'] = ctypes

                # XXX: Swagger doesn't support different schemas for for a same
                # method with different ctypes as cornice, so this may overwrite the
                # previously defined schemas. We try to merge the existing schemas
                # with the previouly defined ones.
                parameters = op.get('parameters', [])
                def_params = path.get(method_name.lower(), {}).get('parameters', [])

                if parameters or def_params:
                    op['parameters'] = def_params + parameters

                path[method_name.lower()] = op
            paths[service.path] = path

        return paths, tags

    def _extract_path_from_service(self, service):

        path = {}

        # Extract path parameters
        param_names = re.findall('\{(.*?)\}', service.path)
        parameters = self.parameters.from_path(param_names)
        if parameters:
            path['parameters'] = parameters

        return path

    def _extract_operation_from_view(self, view, args):

        op = {
            'responses': {
                'default': {
                    'description': 'UNDOCUMENTED RESPONSE'
                }
            },
        }

        # If ctypes are defined in view, try get from renderers
        renderer = args['renderer']

        if "json" in renderer:  # allows for "json" or "simplejson"
            ctype = set(["application/json"])
        elif renderer == "xml":
            ctype = set(["text/xml"])
        else:
            ctype = None

        if ctype:
            op.setdefault('produces', ctype)

        # Get explicit content-types
        if args.get('content_type'):
            op['consumes'] = set(args['content_type'])

        # Get parameters from view schema
        if 'schema' in args:
            parameters = self.parameters.from_schema(args['schema'])
            if parameters:
                op['parameters'] = parameters

        # Get summary from docstring
        if cornice_swagger.util.is_string(view):
            if 'klass' in args:
                ob = args['klass']
                view_ = getattr(ob, view.lower())
                docstring = cornice_swagger.util.trim(view_.__doc__)
        else:
            docstring = cornice_swagger.util.trim(view.__doc__)

        if docstring:
            op['summary'] = docstring

        return op


class DefinitionHandler(object):

    definitions = {}
    json_pointer = '#/definitions/'

    def __init__(self, ref_depth=1):
        self.ref_depth = ref_depth

    def from_schema(self, obj, base_name=None):
        return self._ref(convert(obj), self.ref_depth, base_name)

    # XXX: Dismantle schemas can be dangerous since definition names must be unique
    def _ref(self, schema, depth, base_name=None):

        if depth == 0:
            return schema

        # If schema doesnt have a title, the caller may provide it
        if 'title' not in schema:
            if base_name:
                schema['title'] = base_name
            else:
                raise CorniceSwaggerException('Schema needs a title to be referenced')

        def set_pointers(schema, depth):
            if depth == 0:
                return schema

            if schema['type'] == 'object' and 'properties' in schema:
                for name, prop in schema['properties'].items():
                    if 'title' not in prop:
                        prop['title'] = name
                    pointer = self.json_pointer + prop['title']
                    schema['properties'][name] = {'$ref': pointer}
                    prop = set_pointers(prop, depth-1)
                    self.definitions[prop['title']] = prop

            return schema

        root_pointer = self.json_pointer + schema['title']
        schema = set_pointers(schema, depth)
        self.definitions[schema['title']] = schema

        return {'$ref': root_pointer}


class ParameterHandler(object):

    parameters = {}
    json_pointer = '#/parameters/'

    def __init__(self, definition_handler=DefinitionHandler(), ref_depth=0):
        self.definitions = definition_handler

    def from_schema(self, schema):

        params = []

        if not cornice_swagger.util.is_object(schema):
            schema = schema()

        for param_schema in schema.children:
            location = param_schema.name

            if location in ('path', 'header', 'querystring', 'body'):
                for obj in param_schema.children:
                    param = {
                        'name': obj.name,
                        'in': location,
                        'required': obj.required
                    }

                    schema = self.definitions.from_schema(obj)
                    if '$ref' in schema or schema['type'] == 'object':
                        param['schema'] = schema
                    else:
                        param.update(obj)

            # XXX: if only one object is provided, assume it to be body
            else:
                name = schema.get('name', str(schema.__class__.__name__))
                schema = self.definitions.from_schema(schema, base_name=name)
                param = {
                    'name': name,
                    'in': 'body',
                    'schema': schema
                }

            params.append(param)

        return params

    def from_path(self, param_names):

        params = []
        for name in param_names:
            param = {
                "name": name,
                "in": "path",
                "type": "string",
                "required": True,
            }
            params.append(param)

        return params


def generate_swagger_spec(services, title, version, **kwargs):
    """Utility to turn cornice web services into a Swagger-readable file.

    See https://helloreverb.com/developers/swagger for more information.
    https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md
    """


    swag = CorniceSwagger(services, def_ref_depth=-1, param_ref_depth=0)
    doc = swag(title, version, ignores=('head'), **kwargs)
    doc.update(**kwargs)

    return doc
