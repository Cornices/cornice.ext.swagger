"""Cornice Swagger 2.0 documentor"""
import re
import six

import colander
from cornice.validators import colander_validator, colander_body_validator

import cornice_swagger.util
from cornice_swagger.converters import convert_schema, convert_parameter


class CorniceSwaggerException(Exception):
    """Raised when cornice services have structural problems to be converted."""


class CorniceSwagger(object):
    """Handles the creation of a swagger document from a cornice application."""

    def __init__(self, services, def_ref_depth=0, param_ref=False, resp_ref=False):
        """
        :param services:
            List of cornice services to document. You may use
            cornice.service.get_services() to get it.
        :param def_ref_depth:
            How depth swagger object schemas should be split into
            swaggger definitions with JSON pointers. Default (0) is no split.
            You may use negative values to split everything.
        :param param_ref:
            Defines if swagger parameters should be put inline on the operation
            or on the parameters section and referenced by JSON pointers.
            Default is inline.
        :param resp_ref:
            Defines if swagger responses should be put inline on the operation
            or on the responses section and referenced by JSON pointers.
            Default is inline.
        """

        self.services = services

        self.definitions = DefinitionHandler(ref=def_ref_depth)
        self.parameters = ParameterHandler(self.definitions,
                                           ref=param_ref)
        self.responses = ResponseHandler(self.definitions,
                                         ref=resp_ref)

    def __call__(self, title, version, base_path='/', info={}, swagger={}, **kwargs):
        """
        Generate a Swagger 2.0 documentation. Keyword arguments may be used
        to provide additional information to build methods as such ignores.

        :param title:
            The name presented on the swagger document.
        :param version:
            The version of the API presented on the swagger document.
        :param base_path:
            The path that all requests to the API must refer to.
        :param info:
            Swagger info field.
        :param swagger:
            Extra fields that should be provided on the swagger documentation.
        """

        info.update(title=title, version=version)
        swagger.update(swagger='2.0', info=info, basePath=base_path)

        paths, tags = self._build_paths(**kwargs)
        if paths:
            swagger['paths'] = paths
        if tags:
            swagger['tags'] = tags

        definitions = self.definitions.definition_registry
        if definitions:
            swagger['definitions'] = definitions

        parameters = self.parameters.parameter_registry
        if parameters:
            swagger['parameters'] = parameters

        responses = self.responses.response_registry
        if responses:
            swagger['responses'] = responses

        return swagger

    def _build_paths(self, ignore=['head', 'options'], default_tags=None,
                     **kwargs):
        """
        Build the Swagger "paths" and "tags" attributes from cornice service
        definitions.

        :param ignore:
            List of service methods that should NOT be presented on the documentation.
        :param default_tags:
            Provide a default list of tags or a callable that takes a cornice
            service and returns a list of Swagger tags to be used if a tag is
            not provided by the view.
        """

        paths = {}
        tags = []

        for service in self.services:
            path = self._extract_path_from_service(service)

            for method_name, view, args in service.definitions:
                if method_name.lower() in ignore:
                    continue

                op = self._extract_operation_from_view(view, args)

                # If tag not defined and a default tag is provided
                if 'tags' not in op and default_tags:
                    if callable(default_tags):
                        default_tags = default_tags(service)
                    op['tags'] = default_tags

                # Check if tags was correctly defined as a list
                if not isinstance(op.get('tags', []), list):
                    raise CorniceSwaggerException('Tags should be defined as a list.')

                # Add method tags to root tags
                for tag in op.get('tags', []):
                    if tag not in [t['name'] for t in tags]:
                        root_tag = {'name': tag}
                        tags.append(root_tag)

                # If method is defined for more than one ctype, get previous ones
                ctypes = path.get(method_name.lower(), {}).get('consumes')
                if ctypes and op.get('consumes') not in ctypes:
                    op['consumes'] = ctypes + op['consumes']

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
        """
        Extract path object and its parameters from service definitions.

        :param service:
            Cornice service to extract information from.

        :rtype: dict
            Path definition.
        """

        path = {}

        # Extract path parameters
        parameters = self.parameters.from_path(service.path)
        if parameters:
            path['parameters'] = parameters

        return path

    def _extract_operation_from_view(self, view, args={}):
        """
        Extract swagger operation details from colander view definitions.

        :param view:
            View to extract information from.
        :param args:
            Arguments from the view decorator.

        :rtype: dict
            Operation definition.
        """

        op = {
            'responses': {
                'default': {
                    'description': 'UNDOCUMENTED RESPONSE'
                }
            },
        }

        # If ctypes are defined in view, try get from renderers
        renderer = args.get('renderer', '')

        if "json" in renderer:  # allows for "json" or "simplejson"
            ctype = ['application/json']
        elif renderer == 'xml':
            ctype = ['text/xml']
        else:
            ctype = None

        if ctype:
            op.setdefault('produces', ctype)

        # Get explicit content-types
        if args.get('content_type'):
            op['consumes'] = args['content_type']

        # Get parameters from view schema
        if 'schema' in args:
            validators = args.get('validators')
            parameters = self.parameters.from_schema(args['schema'], validators)
            if parameters:
                op['parameters'] = parameters

        # Get summary from docstring
        if isinstance(view, six.string_types):
            if 'klass' in args:
                ob = args['klass']
                view_ = getattr(ob, view.lower())
                docstring = cornice_swagger.util.trim(view_.__doc__)
        else:
            docstring = cornice_swagger.util.trim(view.__doc__)

        if docstring:
            op['summary'] = docstring

        # Get response definitions
        if 'response_schemas' in args:
            op['responses'] = self.responses.from_schema_mapping(args['response_schemas'])

        # Get response tags
        if 'tags' in args:
            op['tags'] = args['tags']

        return op


class DefinitionHandler(object):
    """Handles Swagger object definitions provided by cornice as colander schemas."""

    json_pointer = '#/definitions/'

    def __init__(self, ref=0):
        """
        :param ref:
            The depth that should be used by self.ref when calling self.from_schema.
        """

        self.definition_registry = {}
        self.ref = ref

    def from_schema(self, schema_node, base_name=None):
        """
        Creates a Swagger definition from a colander schema.

        :param schema_node:
            Colander schema to be transformed into a Swagger definition.
        :param base_name:
            Schema alternative title.

        :rtype: dict
            Swagger schema.
        """
        return self._ref_recursive(convert_schema(schema_node), self.ref, base_name)

    def _ref_recursive(self, schema, depth, base_name=None):
        """
        Dismantle nested swagger schemas into several definitions using JSON pointers.
        Note: This can be dangerous since definition titles must be unique.

        :param schema:
            Base swagger schema.
        :param depth:
            How many levels of the swagger object schemas should be split into
            swaggger definitions with JSON pointers. Default (0) is no split.
            You may use negative values to split everything.
        :param base_name:
            If schema doesn't have a name, the caller may provide it to be
            used as reference.

        :rtype: dict
            JSON pointer to the root definition schema,
            or the original definition if depth is zero.
        """

        if depth == 0:
            return schema

        if schema['type'] != 'object':
            return schema

        name = base_name or schema['title']

        pointer = self.json_pointer + name
        for child_name, child in schema.get('properties', {}).items():
            schema['properties'][child_name] = self._ref_recursive(child, depth-1)

        self.definition_registry[name] = schema

        return {'$ref': pointer}


class ParameterHandler(object):
    """Handles swagger parameter definitions."""

    json_pointer = '#/parameters/'

    def __init__(self, definition_handler=DefinitionHandler(), ref=False):
        """
        :param definition_handler:
            Callable that handles swagger definition schemas.
        :param ref:
            Specifies the ref value when calling from_xxx methods.
        """

        self.parameter_registry = {}

        self.definitions = definition_handler
        self.ref = ref

    def from_schema(self, schema_node, validators=[]):
        """
        Creates a list of Swagger params from a colander request schema.

        :param schema_node:
            Request schema to be transformed into Swagger.
        :param validators:
            Validators used in colander with the schema.
        :rtype: list
            List of Swagger parameters.
        """

        params = []

        if not isinstance(schema_node, colander.Schema):
            schema_node = schema_node()

        if colander_validator in validators:
            for param_schema in schema_node.children:
                location = param_schema.name
                if location is 'body':
                    name = param_schema.__class__.__name__
                    param = convert_parameter(location,
                                              param_schema,
                                              self.definitions.from_schema)
                    param['name'] = name
                    if self.ref:
                        param = self._ref(param)
                    params.append(param)

                elif location in ('path', 'headers', 'querystring'):
                    for node_schema in param_schema.children:
                        param = convert_parameter(location,
                                                  node_schema,
                                                  self.definitions.from_schema)
                        if self.ref:
                            param = self._ref(param)
                        params.append(param)

        elif colander_body_validator in validators:
            name = schema_node.__class__.__name__
            param = convert_parameter('body', schema_node)
            param['name'] = name
            if self.ref:
                param = self._ref(param, schema_node.__class__.__name__)
            params.append(param)

        return params

    def from_path(self, path):
        """
        Create a list of Swagger path params from a cornice service path.

        :type path: string
        :rtype: list
        """

        param_names = re.findall('\{(.*?)\}', path)
        params = []
        for name in param_names:
            param_schema = colander.SchemaNode(colander.String(), name=name)
            param = convert_parameter('path', param_schema)
            if self.ref:
                param = self._ref(param)
            params.append(param)

        return params

    def _ref(self, param, base_name=None):
        """
        Store a parameter schema and return a reference to it.

        :param schema:
            Swagger parameter definition.
        :param base_name:
            Name that should be used for the reference.

        :rtype: dict
            JSON pointer to the original parameter definition.
        """

        name = base_name or param.get('title', '') or param.get('name', '')

        pointer = self.json_pointer + name
        self.parameter_registry[name] = param

        return {'$ref': pointer}


class ResponseHandler(object):
    """Handles swagger response definitions."""

    json_pointer = '#/responses/'

    def __init__(self, definition_handler=DefinitionHandler(), ref=False):
        """
        :param definition_handler:
            Callable that handles swagger definition schemas.
        :param ref:
            Specifies the ref value when calling from_xxx methods.
        """

        self.response_registry = {}

        self.definitions = definition_handler
        self.ref = ref

    def from_schema_mapping(self, schema_mapping):
        """
        Creates a Swagger response object from a dict of response schemas.

        :param schema_mapping:
            Dict with entries matching ``{status_code: response_schema}``.
        :rtype: dict
            Response schema.
        """

        responses = {}

        for status, response_schema in schema_mapping.items():

            response = {}
            if response_schema.description:
                response['description'] = response_schema.description
            else:
                raise CorniceSwaggerException('Responses must have a description.')

            for field_schema in response_schema.children:
                location = field_schema.name
                if location == 'body':
                    field_schema.title = field_schema.__class__.__name__
                    response['schema'] = self.definitions.from_schema(field_schema)
                elif location == 'headers':
                    headers = convert_schema(field_schema)
                    if 'properties' in headers:
                        response['headers'] = headers['properties']

            pointer = response_schema.__class__.__name__
            if self.ref:
                response = self._ref(response, pointer)
            responses[status] = response

        return responses

    def _ref(self, resp, base_name=None):
        """
        Store a response schema and return a reference to it.

        :param schema:
            Swagger response definition.
        :param base_name:
            Name that should be used for the reference.

        :rtype: dict
            JSON pointer to the original response definition.
        """

        name = base_name or resp.get('title', '') or resp.get('name', '')

        pointer = self.json_pointer + name
        self.response_registry[name] = resp

        return {'$ref': pointer}


def generate_swagger_spec(services, title, version, **kwargs):
    """Utility to turn cornice web services into a Swagger-readable file.
    """

    def get_tags_from_path(service):
        return [service.path.split("/")[1]]

    swag = CorniceSwagger(services, def_ref_depth=-1, param_ref=0)
    doc = swag(title, version, ignores=('head'),
               default_tags=get_tags_from_path, **kwargs)
    doc.update(**kwargs)

    return doc
