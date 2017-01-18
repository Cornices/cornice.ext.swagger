Cornice Swagger
===============

|pypi| |travis| |master-coverage| |slack|

.. |travis| image::  https://travis-ci.org/Cornices/cornice.ext.swagger.png
    :target: https://travis-ci.org/Cornices/cornice.ext.swagger

.. |master-coverage| image:: https://coveralls.io/repos/github/Cornices/cornice.ext.swagger/badge.svg?branch=master
    :target: https://coveralls.io/github/Cornices/cornice.ext.swagger?branch=master

.. |pypi| image:: https://img.shields.io/pypi/v/cornice_swagger.svg
    :target: https://pypi.python.org/pypi/cornice_swagger

.. |slack| image:: https://img.shields.io/badge/slack-chat-blue.svg
    :target: https://corniceswagger.herokuapp.com/


*Cornice extension to generate OpenAPI/Swagger Specification*

* Git Repository and issue tracker: https://github.com/Cornices/cornice.ext.swagger
* Full Documentation: https://cornices.github.io/cornice.ext.swagger


This module create a full 
`OpenAPI/Swagger 2.0 compliant spec <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md>`_ 
maximizing the extracted documentation data from functional code,
while allowing users to directly specify parts of the spec.


Scaffold
--------

To get easier started there is a scaffold with can be used.::

   $ cookiecutter https://github.com/delijati/cookiecutter-cornice_swagger.git
   $ cd demo
   $ pip install -e .
   $ cd demo/static
   $ bower install
