CHANGES
=======

0.3.0 (2017-01-12)
------------------

**Api**

- Use `cornice_swagger.swagger.CorniceSwagger` class to generate
  the swagger document rather then `generate_swagger_spec`.
- Allow overriding extractors in the application.
- Schemas are now broken into JSON pointers only if specified.

**Internals**

- Decouples converters from path generators.
- Make considerable changes in the package organisation.
- Reach 100% coverage on tests.

**Documentation**

- Create a Sphinx documentation.


0.2.1 (2016-12-10)
------------------

- Check if schema is not instantiated.
- Add support for query parameter description. [ridha]


0.2 (2016-11-08)
----------------

- Pypi release.
- Point scaffold doc to right url.


0.1 (2016-11-05)
----------------

- First release for new cornice 2.0
