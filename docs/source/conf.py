# flake8: noqa
# -*- coding: utf-8 -*-
import sys, os
try:
    import mozilla_sphinx_theme
except ImportError:
    print("please install the 'mozilla-sphinx-theme' distribution")

sys.path.insert(0, os.path.abspath("../.."))
extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'Cornice Swagger'
copyright = u'2016-2017, Josip Delic'

version = '0.3'
release = '0.3.0'

exclude_patterns = []

html_theme_path = [os.path.dirname(mozilla_sphinx_theme.__file__)]

html_theme = 'mozilla'
html_static_path = ['_static']
