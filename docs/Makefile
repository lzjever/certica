# Minimal Sphinx Makefile

SPHINXOPTS    ?=
SOURCEDIR    = source
BUILDDIR     = build

# Auto-detect sphinx-build: prefer uv run if available, otherwise use python -m sphinx
# Check if uv command exists and use it, otherwise fall back to python -m sphinx
# Allow override via SPHINXBUILD environment variable
SPHINXBUILD ?= $(shell command -v uv >/dev/null 2>&1 && echo "uv run sphinx-build" || echo "python -m sphinx")

.PHONY: help Makefile

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

