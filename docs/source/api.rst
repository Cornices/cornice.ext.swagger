Cornice Swagger API
###################

Here you may find information about the Cornice Swagger internals and methods that
may be overwritten by applications.

Basic Generator
===============

.. py:module:: cornice_swagger

.. autoclass:: cornice_swagger.swagger.CorniceSwagger
    :members:
    :member-order: bysource

Generator Internals
===================

.. automethod:: cornice_swagger.swagger.CorniceSwagger._build_paths
.. automethod:: cornice_swagger.swagger.CorniceSwagger._extract_path_from_service
.. automethod:: cornice_swagger.swagger.CorniceSwagger._extract_operation_from_view

Section Handlers
================

Swagger definitions and parameters are handled in separate classes. You may overwrite
those if you want to change the converters behaviour.


.. autoclass:: cornice_swagger.swagger.DefinitionHandler
.. automethod:: cornice_swagger.swagger.DefinitionHandler.__init__
.. automethod:: cornice_swagger.swagger.DefinitionHandler.from_schema
.. automethod:: cornice_swagger.swagger.DefinitionHandler._ref_recursive

.. autoclass:: cornice_swagger.swagger.ParameterHandler
.. automethod:: cornice_swagger.swagger.ParameterHandler.__init__
.. automethod:: cornice_swagger.swagger.ParameterHandler.from_schema
.. automethod:: cornice_swagger.swagger.ParameterHandler.from_path
.. automethod:: cornice_swagger.swagger.ParameterHandler._ref

.. autoclass:: cornice_swagger.swagger.ResponseHandler
.. automethod:: cornice_swagger.swagger.ResponseHandler.__init__
.. automethod:: cornice_swagger.swagger.ResponseHandler.from_schema_mapping
.. automethod:: cornice_swagger.swagger.ResponseHandler._ref

Colander converters
===================

You may use the ``cornice_swagger.converters`` submodule to access the colander
to swagger request and schema converters. These may be also used without
``cornice_swagger`` generators.

.. automodule:: cornice_swagger.converters
.. autofunction:: cornice_swagger.converters.convert_schema
.. autofunction:: cornice_swagger.converters.convert_parameter
