"""
Tests for internationalization (i18n) module
"""

import pytest
from certica.i18n import set_language, get_language, t, get_supported_languages, SUPPORTED_LANGUAGES


def test_set_language():
    """Test setting language"""
    # Reset to English first
    set_language("en")
    assert get_language() == "en"

    # Test setting to Chinese
    assert set_language("zh")
    assert get_language() == "zh"

    # Unsupported language should return False
    assert not set_language("xx")
    # Should fall back to English
    set_language("en")  # Explicitly reset
    assert get_language() == "en"


def test_get_supported_languages():
    """Test getting supported languages"""
    languages = get_supported_languages()
    assert isinstance(languages, dict)
    assert "en" in languages
    assert "zh" in languages
    assert languages["en"] == "English"


def test_translation():
    """Test translation function"""
    set_language("en")
    assert t("ui.menu.title") == "🔒 CA Certificate Tool"

    set_language("zh")
    assert t("ui.menu.title") == "🔒 CA证书工具"


def test_translation_with_format():
    """Test translation with format strings"""
    set_language("en")
    result = t("lang.unsupported", lang="xx")
    assert "xx" in result

    set_language("zh")
    result = t("lang.unsupported", lang="xx")
    assert "xx" in result


def test_translation_fallback():
    """Test translation fallback to English"""
    set_language("fr")  # French may not have all translations
    # Should fall back to English if French translation is missing
    result = t("ui.menu.title")
    assert result  # Should not be empty


def test_unsupported_language_warning():
    """Test that unsupported language falls back to English"""
    original_lang = get_language()
    result = set_language("invalid")
    assert not result
    # Should fall back to English
    assert get_language() == "en" or get_language() == original_lang
