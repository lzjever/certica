# Internationalization (i18n) Guide

This guide explains how to add or improve translations for Certica.

## Overview

Certica uses a JSON-based translation system. All user-facing strings are stored in translation files located in `certica/locales/`.

## Supported Languages

Currently supported languages:
- `en` - English (default)
- `zh` - Chinese (中文)
- `fr` - French (Français)
- `ru` - Russian (Русский)
- `ja` - Japanese (日本語)
- `ko` - Korean (한국어)

## Translation File Structure

Translation files are JSON files with a flat key-value structure. Keys use dot notation to organize translations:

```json
{
  "ui.menu.title": "🔒 CERTICA — CERTs In a Click, Always.",
  "ui.menu.select_operation": "Select operation:",
  "cli.create_ca.success": "✓ Root CA created successfully!",
  "system.verify.installing": "  Verifying installation..."
}
```

## Adding a New Language

### Step 1: Create Translation File

Create a new file `certica/locales/{lang_code}.json` where `{lang_code}` is the ISO 639-1 language code (e.g., `es` for Spanish, `de` for German).

### Step 2: Add Language to Supported List

Edit `certica/i18n.py` and add your language:

```python
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'zh': 'Chinese',
    'fr': 'French',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'es': 'Spanish',  # Add your language here
}
```

### Step 3: Copy Base Translation

Copy `certica/locales/en.json` as a starting point, or copy from a similar language if available.

### Step 4: Translate All Keys

Translate all keys in the JSON file. You can:
- Translate all keys at once
- Translate incrementally (missing keys will fall back to English)

### Step 5: Test Your Translation

```bash
# Test with your language code
certica --lang es

# Or in Python
python -c "from certica.i18n import set_language, t; set_language('es'); print(t('ui.menu.title'))"
```

## Improving Existing Translations

### Finding Translation Keys

1. **In code**: Look for `t('key.name')` calls
2. **In translation files**: Check `certica/locales/*.json`
3. **Missing translations**: Will automatically fall back to English

### Updating Translations

1. Edit the appropriate language file in `certica/locales/`
2. Update the value for the key
3. Test your changes:
   ```bash
   certica --lang {lang_code}
   ```

## Translation Key Naming Convention

Keys are organized by component:

- `ui.*` - User interface strings (interactive mode)
- `cli.*` - Command-line interface strings
- `system.*` - System integration messages
- `check.*` - System check messages
- `main.*` - Main entry point messages
- `lang.*` - Language-related messages

## Format Strings

Some translations use format strings with placeholders:

```json
{
  "ui.create_ca.success_content": "**CA Name:** {ca_name}\n**Key Path:** {key_path}..."
}
```

When translating, preserve the placeholders (`{ca_name}`, `{key_path}`, etc.) but translate the surrounding text.

## Best Practices

1. **Consistency**: Use consistent terminology throughout
2. **Context**: Consider the context where the string appears
3. **Length**: Keep UI strings concise
4. **Emojis**: Preserve emojis in translations (they're universal)
5. **Testing**: Always test your translations in the actual UI

## Testing Translations

### Interactive Mode

```bash
certica --lang {lang_code}
```

### CLI Mode

```bash
certica --lang {lang_code} create-ca --name test
```

### Python API

```python
from certica.i18n import set_language, t

set_language('es')
print(t('ui.menu.title'))
```

## Common Issues

### Missing Translation

If a key is missing, the system will:
1. Try to use English translation
2. If English is also missing, return the key itself

### Format String Errors

If a format string has wrong placeholders, it will raise an error. Make sure to:
- Preserve all placeholders from the English version
- Use the same placeholder names

### Language Not Recognized

If you see "Language not supported" warning:
- Check that the language code is in `SUPPORTED_LANGUAGES`
- Use ISO 639-1 codes (2 letters, lowercase)

## Contributing Translations

We welcome contributions! To contribute a translation:

1. Fork the repository
2. Create or update the translation file
3. Add the language to `SUPPORTED_LANGUAGES` if it's new
4. Test your translation
5. Submit a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## Questions?

If you have questions about translations:
- Open an issue on GitHub
- Check existing translation files for examples
- Look at the English version for context

