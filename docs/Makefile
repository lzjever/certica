# Minimal Sphinx Makefile

SPHINXOPTS    ?=
# Use python -m sphinx which works with uv and other virtual environments
SPHINXBUILD  ?= python -m sphinx
SOURCEDIR    = source
BUILDDIR     = build

.PHONY: help Makefile

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

