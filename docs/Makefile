# Makefile for Sphinx documentation
#
# To get started, run `make live`

# Path to the documentation virtual environment
CONDA_ENV_FILE = ./docs-environment.yml
CONDA_ENV_DIR = ./env

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= $(CONDA_ENV_DIR)/bin/sphinx-build
SPHINXAUTOBUILD ?= $(CONDA_ENV_DIR)/bin/sphinx-autobuild
SPHINXAPIDOC  ?= $(CONDA_ENV_DIR)/bin/sphinx-apidoc
SOURCEDIR     = source
BUILDDIR      = _build
APIDOCSDIR    = $(SOURCEDIR)/api

SRC = ../src/conda_tui

# Internal variables.
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(SPHINXOPTS) $(SOURCEDIR)

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

$(CONDA_ENV_DIR):
	$(CONDA_EXE) env $(shell [ -d $(CONDA_ENV_DIR) ] && echo update || echo create) -p $(CONDA_ENV_DIR) --file $(CONDA_ENV_FILE)

setup:  ## Setup docs environment
	$(MAKE) -B $(CONDA_ENV_DIR)

api-docs: $(CONDA_ENV_DIR)  ## Generate API docs via sphinx-apidoc
	$(SPHINXAPIDOC) -f -o $(APIDOCSDIR) $(SRC) -H "API Docs"

# Generate static HTML docs
html: api-docs
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

# Generate HTML docs and open in browser with live reload
live: api-docs
	$(SPHINXAUTOBUILD) "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) --watch $(SRC) --open-browser

# Clean all build artifacts (doesn't remove virtual environment)
clean:
	rm -rf $(BUILDDIR) $(APIDOCSDIR)

.PHONY: $(MAKECMDGOALS)
