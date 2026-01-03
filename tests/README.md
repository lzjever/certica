# Tests

This directory contains tests for Certica.

## Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
pytest tests/test_i18n.py

# Run specific test
pytest tests/test_i18n.py::test_translation
```

## Test Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_*.py` - Test files (one per module)

## Writing Tests

- Use pytest fixtures from `conftest.py`
- Follow naming convention: `test_*.py` for files, `test_*` for functions
- Aim for good test coverage
- Test both success and failure cases

