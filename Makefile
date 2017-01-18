# Makefile for Sphinx documentation
#

SPHINXOPTS       =
SPHINXBUILD      = sphinx-build
SPHINXBUILDDIR   = docs/build
SPHINXSOURCEDIR  = docs/source

ALLSPHINXOPTS    = -d $(SPHINXBUILDDIR)/doctrees $(SPHINXOPTS) $(SPHINXSOURCEDIR)
SPHINXBUILDFILES = docs Makefile examples cornice_swagger CHANGES.rst CONTRIBUTORS.rst


.PHONY: help clean docs docs-pub docs-pack

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo " docs          to make docs standalone HTML files"
	@echo " docs-pub      publish docs to github pages"
	@echo " docs-pack     pack docs do publish on pythonhosted"

clean:
	-rm -rf $(BUILDDIR)/*

docs:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(SPHINXBUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(SPHINXBUILDDIR)/html."

docs-pub:
	git checkout gh-pages
	rm -rf *
	git checkout master $(SPHINXBUILDFILES)
	git clean -X -f -d
	git reset HEAD
	make docs
	mv -fv docs/build/html/* ./
	rm -rf $(SPHINXBUILDFILES)
	touch .nojekyll
	git add -A
	git commit -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`"
	git push origin gh-pages
	git checkout master

docs-pack: docs
	cd docs/build/html; zip -r docs.zip *
	mv docs/build/html/docs.zip .
