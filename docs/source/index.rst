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
7. Allow user defined tags and responses on view definitions.


Documentation content
=====================

.. toctree::
    :maxdepth: 2

    quickstart
    tutorial
    api
    faq

.. toctree::
    :maxdepth: 1

    changelog
    contributors


Contribution & Feedback
=======================

You can find us at Github or the Slack chat.

- GitHub Repository: https://github.com/Cornices/cornice.ext.swagger
- Slack chat: https://corniceswagger.herokuapp.com

You may also try the Cornice Mailing List:

- Cornice Developers Mailing List: https://mail.mozilla.org/listinfo/services-dev
