Cornice Swagger
###############

**Cornice Swagger** is an extension package for `Cornice <https://cornice.readthedocs.io/>`_
that allows generating an OpenAPI/Swagger specification from Cornice service definitions.

What does it do?
================

Cornice swagger builds a valid OpenAPI document with basically these things:

1. Path listing and parameters from service path definitions.
2. Methods defined from each service view.
3. Descriptions from view docstrings.
4. Parameters from request schemas when using cornice/colander validators on the
   view definition.
5. Produced content-types when using colander renderers.
6. Accepted content types when they are provided on view definitions.

.. important::
   Right now there still no way to document Swagger responses with this module.
   If you can, please
   `help us with that <https://github.com/Cornices/cornice.ext.swagger/issues/4>`_.

Documentation content
=====================

.. toctree::
   :maxdepth: 1

   quickstart
   tutorial
   api
   faq


Contribution & Feedback
=======================

You can find us at Github and leave us feedback on the Issue Tracker.

- GitHub Repository: https://github.com/Cornices/cornice.ext.swagger
- Issue Tracker: https://github.com/Cornices/cornice.ext.swagger/issues

You may also try the Cornice Mailing List:

- Cornice Developers Mailing List: https://mail.mozilla.org/listinfo/services-dev
