.PHONY: help clean install dev-install test test-cov lint format format-check check build sdist wheel docs html clean-docs upload upload-test check-package

# Use uv if available, otherwise fall back to pip
UV := $(shell command -v uv 2>/dev/null)
ifeq ($(UV),)
	PIP_CMD = pip
	PYTHON_CMD = python
else
	PIP_CMD = uv pip
	PYTHON_CMD = uv run python
	# dev group is installed by default with uv sync
	UV_SYNC = uv sync --group docs
endif

help:
	@echo "Available targets:"
	@echo ""
	@echo "Setup (run first):"
	@echo "  dev-install   - Install package with development dependencies (recommended for active development)"
	@echo "  setup-venv    - Create virtual environment and install dependencies only (no package install)"
	@echo "                  Use for: CI/CD, code review, or when you don't need to import the package"
	@echo "  install       - Install the package (after setup-venv or standalone)"
	@echo ""
	@echo "Testing:"
	@echo "  test          - Run all tests"
	@echo "  test-cov      - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint          - Run linting checks (flake8)"
	@echo "  format        - Format code with black"
	@echo "  format-check  - Check code formatting"
	@echo "  check         - Run all checks (lint + format check + tests)"
	@echo ""
	@echo "Building:"
	@echo "  build         - Build source and wheel distributions"
	@echo "  sdist         - Build source distribution"
	@echo "  wheel         - Build wheel distribution"
	@echo "  check-package - Check package before uploading"
	@echo ""
	@echo "Publishing:"
	@echo "  upload        - Upload package to PyPI (requires PYPI_TOKEN env var)"
	@echo "  upload-test   - Upload package to TestPyPI (requires TEST_PYPI_TOKEN env var)"
	@echo ""
	@echo "Documentation:"
	@echo "  docs          - Build documentation"
	@echo "  html          - Build HTML documentation"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean         - Clean build artifacts"
	@echo "  clean-docs    - Clean documentation build"
	@echo ""
	@if [ -n "$(UV)" ]; then \
		echo "Using uv for dependency management"; \
	else \
		echo "Using pip for dependency management (consider installing uv: curl -LsSf https://astral.sh/uv/install.sh | sh)"; \
	fi
	@echo ""
	@echo "Note: For active development, run 'make dev-install' (installs package + deps)."
	@echo "      For CI/tools only, run 'make setup-venv' (deps only, no package)."

setup-venv:
	@echo "Setting up virtual environment and installing dependencies (without installing package)..."
	@echo "This is useful for CI/CD, code review, or when you only need development tools."
	@if [ -n "$(UV)" ]; then \
		uv sync --group docs --no-install-project; \
		echo "✅ Virtual environment created and dependencies installed!"; \
		echo "   To install the package later, run: make install"; \
		echo "   Note: Some tests may fail without the package installed."; \
	else \
		echo "Error: uv is required for setup-venv. Install uv or use 'make dev-install' instead."; \
		exit 1; \
	fi

install:
	@if [ -n "$(UV)" ]; then \
		uv sync; \
	else \
		$(PIP_CMD) install -e .; \
	fi

dev-install:
	@echo "Installing package with all development dependencies..."
	@if [ -n "$(UV)" ]; then \
		uv sync --group docs; \
	else \
		$(PIP_CMD) install -e ".[dev]"; \
	fi
	@echo "✅ Package and dependencies installed! Ready for development."

test:
	$(PYTHON_CMD) -m pytest tests/ -v

test-cov:
	$(PYTHON_CMD) -m pytest tests/ --cov=certica --cov-report=html --cov-report=term

lint:
	$(PYTHON_CMD) -m flake8 certica/ tests/ examples/ --max-line-length=100 --extend-ignore=E203,W503,E501

format:
	$(PYTHON_CMD) -m black certica/ tests/ examples/

format-check:
	$(PYTHON_CMD) -m black --check certica/ tests/ examples/

check: lint format-check test
	@echo "All checks passed!"

build: clean
	@if [ -n "$(UV)" ]; then \
		uv sync --group docs; \
	fi
	$(PYTHON_CMD) -m build

sdist: clean
	@if [ -n "$(UV)" ]; then \
		uv sync --group docs; \
	fi
	$(PYTHON_CMD) -m build --sdist

wheel: clean
	@if [ -n "$(UV)" ]; then \
		uv sync --group docs; \
	fi
	$(PYTHON_CMD) -m build --wheel

check-package: build
	@echo "Checking package..."
	@if [ -n "$(UV)" ]; then \
		uv pip install twine; \
	else \
		$(PIP_CMD) install twine; \
	fi
	twine check dist/*

upload: check-package
	@echo "Uploading to PyPI..."
	@if [ -z "$$PYPI_TOKEN" ]; then \
		echo "Error: PYPI_TOKEN environment variable is not set."; \
		echo "Usage: PYPI_TOKEN=your-token make upload"; \
		exit 1; \
	fi
	@if [ -n "$(UV)" ]; then \
		uv pip install twine; \
	else \
		$(PIP_CMD) install twine; \
	fi
	twine upload dist/* \
		--username __token__ \
		--password $$PYPI_TOKEN

upload-test: check-package
	@echo "Uploading to TestPyPI..."
	@if [ -z "$$TEST_PYPI_TOKEN" ]; then \
		echo "Error: TEST_PYPI_TOKEN environment variable is not set."; \
		echo "Usage: TEST_PYPI_TOKEN=your-token make upload-test"; \
		exit 1; \
	fi
	@if [ -n "$(UV)" ]; then \
		uv pip install twine; \
	else \
		$(PIP_CMD) install twine; \
	fi
	twine upload dist/* \
		--repository testpypi \
		--username __token__ \
		--password $$TEST_PYPI_TOKEN

docs:
	@if [ -n "$(UV)" ]; then \
		uv sync --group docs; \
	fi
	cd docs && $(PYTHON_CMD) -m sphinx -M html source build

html:
	@if [ -n "$(UV)" ]; then \
		uv sync --group docs; \
	fi
	cd docs && $(PYTHON_CMD) -m sphinx -M html source build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@if [ -n "$(UV)" ]; then \
		echo "Note: To clean uv virtual environment, run: uv venv --clear"; \
	fi

clean-docs:
	@if [ -d "docs" ]; then \
		cd docs && make clean; \
	else \
		echo "Documentation directory not found. Skipping..."; \
	fi

