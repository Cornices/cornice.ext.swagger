CHANGES
=======

0.5.1 (2017-04-10)
------------------

**Pyramid compliance**

- Support subpaths and regex when parsing paths (#68).

**Api**

- ``_extract_path_from_service``, now returns the path name along with the path
  swagger object (#68).


0.5.0 (2017-02-14)
------------------

**Api**

- Allow implementing a custom generator by subclassing the ``CorniceSwagger`` class (#63).
- Introduced a new method ``CorniceSwagger.generate`` to generate the spec (#63).
- Deprecated ``CorniceSwagger`` call method. You should now use ``generate`` (#63).
- Removed deprecated ``generate_swagger_spec`` call. (#64).
- Allow defining custom type converters on the ``CorniceSwagger`` class. (#65)

**Internals**

- Fixed coveralls repeated messages on PRs. (#62).

0.4.0 (2017-01-25)
------------------

**Api**

- Summaries from docstrings are now not included by default. You can enable them by passing
  ``summary_docstrings = True`` to the generator.
- Trying to document multiple views on same method now raises an exception. You should
  ignore the unwanted ones by content type.
- Raw ``swagger`` items are now recursively merged (instead of replaced) with
  the extracted fields.
- Add support for documenting operation ids via an ``operation_id`` argument on the view
  or by passing a ``default_op_ids`` callable to the generator.
- Add a shortcut to the generator on ``cornice_swagger.CorniceSwagger``.
- Support Cornice schema synonyms (headers and GET are the same as header and querystring).
- Add support for documenting security properties via a ``api_security`` list on the view
  or by passing a ``default_security`` list or callable to the generator.

**OpenAPI compliance**

- Remove invalid ``title`` field from response headers and request parameters.
- Support conversion of parameter validators.

**Internals**

- Fix default tag generator.
- Fix references when using declarative schemas.
- Simplify parameter converter by properly isolating ``body``.


0.3.0 (2017-01-17)
------------------

**Api**

- Use ``cornice_swagger.swagger.CorniceSwagger`` class to generate
  the swagger document rather then ``generate_swagger_spec``.
- Allow overriding extractors in the application.
- Schemas are now broken into JSON pointers only if specified.
- Allow documenting responses via ``response_schemas`` view attribute.
- Allow documenting tags via ``tags`` view attribute or using a
  ``default_tags`` parameter when calling the generator.

**Internals**

- Decouples converters from path generators.
- Make considerable changes in the package organisation.
- Reach 100% coverage on tests.

**Documentation**

- Create a Sphinx documentation hosted on
  https://cornices.github.io/cornice.ext.swagger.


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
