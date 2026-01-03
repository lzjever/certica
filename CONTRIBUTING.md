# Contributing to Certica

Thank you for your interest in contributing to Certica!

## Development Setup

### Quick Start

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set up development environment**:
   ```bash
   make dev-install
   ```

3. **Run tests**:
   ```bash
   make test
   ```

That's it! You're ready to contribute.

For detailed setup instructions, see [SETUP.md](SETUP.md).

## Development Workflow

### Standard Development

For active development where you need to import and use certica:

```bash
make dev-install  # Installs package + all dependencies
make test         # Run tests
make lint         # Check code quality
make format       # Format code
```

### CI/CD or Code Review

If you only need development tools (linting, formatting) without installing the package:

```bash
make setup-venv   # Only installs dependencies, not the package
make lint         # Can still run linting
make format-check # Can still check formatting
```

## Code Style

- **Formatting**: We use `black` with 100 character line length
- **Linting**: We use `flake8` with specific ignore rules
- **Type Checking**: We use `mypy` (optional, not strict)
- **Testing**: We use `pytest`

Run all checks:
```bash
make check
```

## Adding New Languages (i18n)

Certica supports multiple languages through the i18n system. To add a new language:

1. **Create translation file**: Create `certica/locales/{lang_code}.json`
   - Use ISO 639-1 language codes (e.g., `es` for Spanish, `de` for German)
   - Copy the structure from `en.json` or `zh.json`

2. **Add language to supported list**: Update `certica/i18n.py`:
   ```python
   SUPPORTED_LANGUAGES = {
       'en': 'English',
       'zh': 'Chinese',
       # ... add your language
       'es': 'Spanish',  # Example
   }
   ```

3. **Translate all keys**: Translate all translation keys from `en.json`
   - Missing translations will fall back to English
   - Use the same key structure as English

4. **Test your translation**: 
   ```bash
   certica --lang es  # Test with your language code
   ```

5. **Update documentation**: 
   - Update `README.md` to list the new language
   - Update this file if needed

See [I18N_GUIDE.md](I18N_GUIDE.md) for detailed instructions.

## Testing

### Running Tests

```bash
make test          # Run all tests
make test-cov      # Run tests with coverage
```

### Writing Tests

- Place tests in `tests/` directory
- Test files should start with `test_`
- Use pytest fixtures from `tests/conftest.py`
- Aim for good test coverage

## Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Run checks**: `make check`
5. **Commit your changes**: Use clear commit messages
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Create a Pull Request**

## Pull Request Guidelines

- **Clear description**: Describe what and why
- **Reference issues**: Link to related issues
- **Tests**: Include tests for new features
- **Documentation**: Update docs if needed
- **Pass checks**: All CI checks must pass

## Code of Conduct

Be respectful and inclusive. We welcome contributions from everyone.

## Questions?

Open an issue or start a discussion. We're happy to help!

