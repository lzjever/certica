"""
Internationalization (i18n) module for Certica
Supports multiple languages with fallback to English
"""

import json
from pathlib import Path
from typing import Dict

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "zh": "Chinese",
    "fr": "French",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
}

# Default language
DEFAULT_LANGUAGE = "en"

# Current language
_current_language = DEFAULT_LANGUAGE
_translations: Dict[str, Dict[str, str]] = {}


def _load_translations(lang: str) -> Dict[str, str]:
    """Load translations for a specific language"""
    # Get the directory where this file is located
    base_dir = Path(__file__).parent
    lang_dir = base_dir / "locales"
    lang_file = lang_dir / f"{lang}.json"

    if lang_file.exists():
        try:
            with open(lang_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return {}


def set_language(lang: str) -> bool:
    """
    Set the current language

    Args:
        lang: Language code (e.g., 'en', 'zh', 'fr')

    Returns:
        True if language is supported and loaded, False otherwise
    """
    global _current_language, _translations

    # Normalize language code (e.g., 'zh-CN' -> 'zh')
    lang = lang.lower().split("-")[0]

    if lang not in SUPPORTED_LANGUAGES:
        return False

    _current_language = lang
    _translations[lang] = _load_translations(lang)

    # Always load English as fallback
    if lang != DEFAULT_LANGUAGE:
        _translations[DEFAULT_LANGUAGE] = _load_translations(DEFAULT_LANGUAGE)

    return True


def get_language() -> str:
    """Get the current language code"""
    return _current_language


def t(key: str, **kwargs) -> str:
    """
    Translate a key to the current language

    Args:
        key: Translation key (e.g., 'ui.menu.title')
        **kwargs: Format arguments for the translation string

    Returns:
        Translated string, or key if translation not found
    """
    # Try current language first
    if _current_language in _translations:
        translation = _translations[_current_language].get(key)
        if translation:
            try:
                return translation.format(**kwargs) if kwargs else translation
            except Exception:
                return translation

    # Fallback to English
    if DEFAULT_LANGUAGE in _translations:
        translation = _translations[DEFAULT_LANGUAGE].get(key)
        if translation:
            try:
                return translation.format(**kwargs) if kwargs else translation
            except Exception:
                return translation

    # If still not found, return key (or formatted key if kwargs provided)
    if kwargs:
        try:
            return key.format(**kwargs)
        except Exception:
            return key

    return key


def get_supported_languages() -> Dict[str, str]:
    """Get dictionary of supported language codes and names"""
    return SUPPORTED_LANGUAGES.copy()


# Initialize with default language
set_language(DEFAULT_LANGUAGE)
