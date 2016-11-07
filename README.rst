cornice_swagger
===============

*Cornice extension to generate Swagger*

Git Repository and issue tracker: https://github.com/Cornices/cornice.ext.swagger

.. |travisci| image::  https://travis-ci.org/Cornices/cornice.ext.swagger.png
.. _travisci: https://travis-ci.org/Cornices/cornice.ext.swagger

.. image:: https://coveralls.io/repos/Cornices/cornice.ext.swagger/badge.png
    :target: https://coveralls.io/r/Cornices/cornice.ext.swagger

|travisci|_

To create a full swagger spec, this module will maximize extracting
documentation data from functional code, while allowing users to
directly specify parts of the Swagger Spec. This documentation serves as
a "how-to". Readers are encouraged to look at the source for more
detailed documentation if needed.

This module creates a `Swagger 2.0 compliant spec`_.

Throughout this documentation, ``code-styled text`` indicates a sort of
"proper noun" matching the official names used in related documentation
(Swagger Spec, Cornice, Pyramid, Colander).

**Outline**

1. Docstrings
2. Swagger Module
3. Converters

   1. Colander for input parameters

4. Scaffold

Description Docstrings
======================

-  ``cornice.resource.resource``-decorated classes in your view file should
   have docstrings (triple-quoted strings immediately after your class
   declaration)

   -  This docstring becomes the description for the respective endpoint
      group.
   -  Each endpoint group is a collection of Swagger Paths which start
      with the same URL base (the text between the first two ``/``
      characters in your URL after the true URL base).

-  ``cornice.resource.view``-decorated methods with your decorated Cornice
   Resource classes should have docstrings to document the individual
   HTTP method descriptions

*Note* The Swagger UI groups together endpoints which share the same
``tag``. The swagger module auto-tags all endpoints based on their path
beginning. Technically, a Swagger Spec stores a ``basePath`` in the
`root document object`_. However, as a well-formed REST URI begins with
a RESTful object with which to be interacted, this object (between the
first slashes) will be used to tag similar paths into a group.

*Warning* If you implement multiple ``@resource``-decorated classes
beginning with the same first URL segment in the ``path`` argument, it
may become ambiguous which docstring will be displayed in Swagger UI.
Only put a docstring on one such class to remove ambiguity.

Swagger Module
==============

``swagger.py`` uses
``generate_swagger_spec(services, title, version, **kwargs)`` to make
the actual Swagger Spec JSON. The arguments are:

.. _Swagger 2.0 compliant spec: https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md
.. _root document object: https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#fixed-fields

1. ``services`` - a list of Pyramid Services. Note that Cornice
   Resources are really Services under the hood.
2. ``title`` and ``version`` are both required Swagger Spec details for
   the `Info Object`_.
3. ``kwargs`` can be made of anything else which would go into the base
   `Swagger Object`_.

*Note* If you want to add to the ``Info Object``, simply pass in as an
``info`` argument with the additional details. The ``Info Object``
populated by the ``title`` and ``version`` args provided earlier will
simply be updated.

An example of a Pyramid Service which itself scans other Cornice
Resources and Services to generate a ``swagger.json`` Spec:

.. code:: python

   from pyramid.view import view_config
   from cornice import service
   from swagger import generate_swagger_spec


   @view_config(route_name="swagger", renderer="templates/index.pt")
   def swagger(request):
       return {"request": request}


   @view_config(route_name="swagger_json", renderer="json")
   def swagger_json(request):
       info = {"title": "Joes API", "version": "0.1", "contact": {
               "name": "Joe Smith",
               "email": "joe.cool@swagger.com"}
               }
       base_path = "/"
       services = get_services()
       spec = generate_swagger_spec(services, info["title"],
                                    info["version"], info=info,
                                    base_path=base_path, head=False)
       return spec

Swagger-UI integration
----------------------

To serve the swagger-ui we create a ``index.html`` and download the needed js
files with ``bower``.

.. code:: html

   <!DOCTYPE html>
   <html>

   <head>
       <!-- swagger -->
       <link href="${request.static_url('foo:static/bower_components/swagger-ui/dist/css/typography.css')}"
       type='text/css' rel="stylesheet" />
       <link href="${request.static_url('foo:static/bower_components/swagger-ui/dist/css/reset.css')}"
       type='text/css' rel="stylesheet" />
       <link href="${request.static_url('foo:static/bower_components/swagger-ui/dist/css/screen.css')}"
       type='text/css' rel="stylesheet" />
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/lib/object-assign-pollyfill.js')}"></script>
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/lib/jquery-1.8.0.min.js')}"></script>
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/lib/jquery.slideto.min.js')}"></script>
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/lib/jquery.wiggle.min.js')}"></script>
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/lib/jquery.ba-bbq.min.js')}"></script>
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/lib/handlebars-2.0.0.js')}"></script>
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/lib/lodash.min.js')}"></script>
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/lib/backbone-min.js')}"></script>
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/dist/swagger-ui.min.js')}"></script>
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/lib/highlight.9.1.0.pack.js')}"></script>
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/lib/highlight.9.1.0.pack_extended.js')}"></script>
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/lib/jsoneditor.min.js')}"></script>
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/lib/js-yaml.min.js')}"></script>
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/lib/marked.js')}"></script>
       <script src="${request.static_url('foo:static/bower_components/swagger-ui/lib/swagger-oauth.js')}"></script>
   </head>

   <body>
       <div class="swagger-section container">
           <div id="swagger-ui-container" class="swagger-ui-wrap"></div>
       </div>
       <script type="text/javascript">
           $(function()
           {
               var swaggerUi = new SwaggerUi(
               {
                   url: "${request.route_url('swagger_json')}",
                   dom_id: "swagger-ui-container",
                   validatorUrl: null,
                   docExpansion: "list"
               });
               swaggerUi.load();
           });
       </script>
   </body>

   </html>

Converters
----------

Ideally, we'd maximaize how much documentation comes from functional code. As
we're already using Cornice, we can leverage its operators internally to
``generate_swagger_spec()``. This only gets us so far, and currently only
leverages the ``@resource`` decorator as it identifies services and provides
some path info from which to gleen ``path`` parameters and a description. For
example, this code...

.. code:: python

   class Body(MappingSchema):
       # foo and bar are required, baz is optional
       foo = SchemaNode(String())
       ipsum = SchemaNode(Integer(), missing=1, validator=Range(0, 3))
       integers = Integers(missing=())


   class Query(MappingSchema):
       yeah = SchemaNode(String())
       mau = SchemaNode(String())


   class RequestSchema(MappingSchema):
       body = Body(description="Defines a cornice body schema")
       querystring = Query()

   @resource(collection_path='/tokens', path='/tokens/{authId}',
             description='quick token description')
   class Token(object):
       """Authenticate by POSTing here"""
       def __init__(self, request):
           self.request = request

       @view(validators=(colander_validator, ), schema=RequestSchema())
       def collection_post(self):
           """Get authKey here and use as X-Identity-Token for future calls"""
           ...
       def delete(self):
           """Log out of system by deleting a token from your previous authId"""
           ...

Colander
~~~~~~~~

Since Cornice recommends Colander for validation, there are some handy
converters to convert Colander ``Schemas Nodes`` to Swagger ``Parameter
Objects``.

If you have defined Cornice ``Schema`` objects (comprised of ``Schema Nodes``),
you can pass it to ``schema_to_parameters`` which then converts the ``Schema``
to a list of ``Swagger Parameters``. Since ``Schema Nodes`` take in a Colander
type as an argument (``Tuple``, ``Boolean``, etc) the Swagger ``Parameter
Object`` "type" can be derived. This function is used by
``generate_swagger_spec`` to scan for Colander Schmas being decorated onto an
``Operation`` with the Cornice ``@view(schema=MyCoolSchema`` decorator, and the
create ``Parameter Objects``

Scaffold
--------

To get easier started there is a scaffold with can be used.

::

   $ cookiecutter https://github.com/delijati/cookiecutter-cornice_swagger.git
   $ cd demo
   $ pip install -e .
   $ cd demo/static
   $ bower install

Contributors
============

- Jason Haury

- Josip Delic
