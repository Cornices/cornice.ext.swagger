"""Cornice Swagger 2.0 documentor"""
import re
from functools import partial

import colander
import six

from cornice_swagger.util import body_schema_transformer, merge_dicts, trim
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
        self.schema_transformers = [body_schema_transformer]

    def __call__(self, title, version, base_path='/', info={}, swagger={},
                 schema_transformers=[], **kwargs):
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
        :param schema_transformers:
            List of schema transformers that take a colander schema and view arguments
            and return a modified schema. The transformers are applied in a sequence.
            You may add transformers to this pipeline when using custom schemas that
            doesn't correspond to the schemas used with `colander_validator`.

        :rtype: dict Full OpenAPI/Swagger compliant specification for the application.
        """

        info = info.copy()
        swagger = swagger.copy()
        info.update(title=title, version=version)
        swagger.update(swagger='2.0', info=info, basePath=base_path)
        self.schema_transformers.extend(schema_transformers)

        paths, tags = self._build_paths(**kwargs)

        # Update the provided tags with the extracted ones preserving order
        if tags:
            swagger.setdefault('tags', [])
            tag_names = {t['name'] for t in swagger['tags']}
            for tag in tags:
                if tag['name'] not in tag_names:
                    swagger['tags'].append(tag)

        # Create/Update swagger sections with extracted values where not provided
        if paths:
            swagger.setdefault('paths', {})
            merge_dicts(swagger['paths'], paths)

        definitions = self.definitions.definition_registry
        if definitions:
            swagger.setdefault('definitions', {})
            merge_dicts(swagger['definitions'], definitions)

        parameters = self.parameters.parameter_registry
        if parameters:
            swagger.setdefault('parameters', {})
            merge_dicts(swagger['parameters'], parameters)

        responses = self.responses.response_registry
        if responses:
            swagger.setdefault('responses', {})
            merge_dicts(swagger['responses'], responses)

        return swagger

    def _build_paths(self, ignore_methods=['head', 'options'], ignore_ctypes=[],
                     default_tags=None, default_op_ids=None, default_security=None, **kwargs):
        """
        Build the Swagger "paths" and "tags" attributes from cornice service
        definitions.

        :param ignore_methods:
            List of service methods that should NOT be presented on the
            documentation. You may use this to remove methods that are not
            essential on the API documentation. Default ignores HEAD ans OPTIONS.
        :param ignore_ctypes:
            List of service content-types that should NOT be presented on
            the documentation. You may use this when a Cornice service definition
            has multiple view definitions for a same method, which is not supported
            on Swagger.
        :param default_tags:
            Provide a default list of tags or a callable that takes a cornice
            service and the method name (e.g GET) and returns a list of Swagger
            tags to be used if not provided by the view.
        :param default_op_ids:
            Provide a callable that takes a cornice service and the method name
            (e.g GET) and returns an operation Id that should be unique.
        :param default_security:
            Provide a default list or a callable that takes a cornice
            service and the method name (e.g GET) and returns a list of Swagger
            security policies.
        """

        paths = {}
        tags = []

        for service in self.services:
            path = self._extract_path_from_service(service, **kwargs)

            for method, view, args in service.definitions:

                if method.lower() in ignore_methods:
                    continue

                op = self._extract_operation_from_view(view, args, **kwargs)

                if any(ctype in op.get('consumes', []) for ctype in ignore_ctypes):
                    continue

                # XXX: Swagger doesn't support different schemas for for a same method
                # with different ctypes as cornice. If this happens, you may ignore one
                # content-type from the documentation otherwise we raise an Exception
                # Related to https://github.com/OAI/OpenAPI-Specification/issues/146
                previous_definition = path.get(method.lower())
                if previous_definition:
                    raise CorniceSwaggerException(("Swagger doesn't support multiple "
                                                   "views for a same method. You may "
                                                   "ignore one."))

                # If tag not defined and a default tag is provided
                if 'tags' not in op and default_tags:
                    if callable(default_tags):
                        op['tags'] = default_tags(service, method)
                    else:
                        op['tags'] = default_tags

                # Check if tags was correctly defined as a list
                if not isinstance(op.get('tags', []), list):
                    raise CorniceSwaggerException('tags should be a list or callable')

                # Add method tags to root tags
                for tag in op.get('tags', []):
                    if tag not in [t['name'] for t in tags]:
                        root_tag = {'name': tag}
                        tags.append(root_tag)

                # If operation id is not defined and a default generator is provided
                if 'operationId' not in op and default_op_ids:
                    if not callable(default_op_ids):
                        raise CorniceSwaggerException('default_op_id should be a callable.')
                    op['operationId'] = default_op_ids(service, method)

                # If security options not defined and default is provided
                if 'security' not in op and default_security:
                    if callable(default_security):
                        op['security'] = default_security(service, method)
                    else:
                        op['security'] = default_security

                if not isinstance(op.get('security', []), list):
                    raise CorniceSwaggerException('security should be a list or callable')

                path[method.lower()] = op
            paths[service.path] = path

        return paths, tags

    def _extract_path_from_service(self, service, **kwargs):
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

    def _extract_operation_from_view(self, view, args={},
                                     summary_docstrings=False, **kwargs):
        """
        Extract swagger operation details from colander view definitions.

        :param view:
            View to extract information from.
        :param args:
            Arguments from the view decorator.
        :param summary_docstrings:
            Enable extracting operation summaries from view docstrings.

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

        # If 'produces' are not defined in the view, try get from renderers
        renderer = args.get('renderer', '')

        if "json" in renderer:  # allows for "json" or "simplejson"
            produces = ['application/json']
        elif renderer == 'xml':
            produces = ['text/xml']
        else:
            produces = None

        if produces:
            op.setdefault('produces', produces)

        # Get explicit accepted content-types
        consumes = args.get('content_type')

        # A single content-type is provided, so wrap it in a list
        if isinstance(consumes, six.string_types):
            consumes = [consumes]

        if consumes:
            op['consumes'] = list(consumes)

        # Get parameters from view schema
        schema = self._extract_transform_schema(args)
        parameters = self.parameters.from_schema(schema)
        if parameters:
            op['parameters'] = parameters

        # Get summary from docstring
        if isinstance(view, six.string_types):
            if 'klass' in args:
                ob = args['klass']
                view_ = getattr(ob, view.lower())
                docstring = trim(view_.__doc__)
        else:
            docstring = trim(view.__doc__)

        if docstring and summary_docstrings:
            op['summary'] = docstring

        # Get response definitions
        if 'response_schemas' in args:
            op['responses'] = self.responses.from_schema_mapping(args['response_schemas'])

        # Get response tags
        if 'tags' in args:
            op['tags'] = args['tags']

        # Get response operationId
        if 'operation_id' in args:
            op['operationId'] = args['operation_id']

        # Get security policies
        if 'api_security' in args:
            op['security'] = args['api_security']

        return op

    def _extract_transform_schema(self, args):
        """
        Extract schema from view args and transform it using
        the pipeline of schema transformers

        :param args:
            Arguments from the view decorator.

        :rtype: colander.MappingSchema()
            View schema cloned and transformed
        """

        schema = args.get('schema', colander.MappingSchema())
        if not isinstance(schema, colander.Schema):
            schema = schema()
        schema = schema.clone()
        for transformer in self.schema_transformers:
            schema = transformer(schema, args)
        return schema


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

    def from_schema(self, schema_node):
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

        for param_schema in schema_node.children:
            location = param_schema.name
            if location is 'body':
                name = param_schema.__class__.__name__
                if name == 'body':
                    name = schema_node.__class__.__name__ + 'Body'
                param = convert_parameter(location,
                                          param_schema,
                                          partial(self.definitions.from_schema, base_name=name))
                param['name'] = name
                if self.ref:
                    param = self._ref(param)
                params.append(param)

            elif location in (('path', 'header', 'headers', 'querystring', 'GET')):
                for node_schema in param_schema.children:
                    param = convert_parameter(location,
                                              node_schema,
                                              self.definitions.from_schema)
                    if self.ref:
                        param = self._ref(param)
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
                    title = field_schema.__class__.__name__
                    if title == 'body':
                        title = response_schema.__class__.__name__ + 'Body'
                    field_schema.title = title
                    response['schema'] = self.definitions.from_schema(field_schema)

                elif location in ('header', 'headers'):
                    header_schema = convert_schema(field_schema)
                    headers = header_schema.get('properties')
                    if headers:
                        # Response headers doesn't accept titles
                        for header in headers.values():
                            header.pop('title')

                        response['headers'] = headers

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

    def get_tags_from_path(service, method):
        return [service.path.split("/")[1]]

    swag = CorniceSwagger(services, def_ref_depth=-1, param_ref=0)
    doc = swag(title, version, ignores=('head'),
               default_tags=get_tags_from_path,
               summary_docstrings=True, **kwargs)
    doc.update(**kwargs)

    return doc
