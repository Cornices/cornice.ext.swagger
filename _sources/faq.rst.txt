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


How do I integrate Swagger UI?
==============================

TO integrate swagger-ui you can create a ``index.html`` and download the needed JS
files with ``bower``. You can then serve it with a Cornice or a Simple Pyramid HTML service.

An example HTML file is:

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

