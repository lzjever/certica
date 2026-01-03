"""
Edge cases and additional tests for i18n module
"""

from unittest.mock import patch
from certica.i18n import set_language, get_language, t, _load_translations, SUPPORTED_LANGUAGES


class TestI18nEdgeCases:
    """Test edge cases for i18n module"""

    def test_load_translations_nonexistent_file(self):
        """Test loading translations from non-existent file"""
        result = _load_translations("nonexistent")
        assert result == {}

    def test_load_translations_invalid_json(self, tmp_path):
        """Test loading translations from invalid JSON file"""
        # Create a temporary locale file with invalid JSON
        locale_file = tmp_path / "invalid.json"
        locale_file.write_text("{ invalid json }")

        # Mock the locale directory
        with patch("certica.i18n.Path") as mock_path:
            mock_path.return_value.parent = tmp_path
            result = _load_translations("invalid")
            # Should return empty dict on error
            assert result == {}

    def test_set_language_with_locale_code(self):
        """Test setting language with locale code (e.g., zh-CN -> zh)"""
        set_language("zh-CN")
        assert get_language() == "zh"

        set_language("en-US")
        assert get_language() == "en"

        set_language("fr-FR")
        assert get_language() == "fr"

    def test_set_language_case_insensitive(self):
        """Test that language codes are case insensitive"""
        set_language("ZH")
        assert get_language() == "zh"

        set_language("EN")
        assert get_language() == "en"

    def test_translation_with_format_exception(self):
        """Test translation with format string that raises exception"""
        set_language("en")
        # Use a key that exists but with invalid format args
        result = t("ui.menu.title", invalid_arg="test")
        # Should return the translation without formatting
        assert result == "🔒 CA Certificate Tool"

    def test_translation_key_not_found(self):
        """Test translation when key is not found"""
        set_language("en")
        result = t("nonexistent.key")
        assert result == "nonexistent.key"

    def test_translation_key_not_found_with_format(self):
        """Test translation when key is not found but has format args"""
        set_language("en")
        result = t("nonexistent.key", arg1="value1")
        # Should try to format the key itself
        assert result == "nonexistent.key"  # Key doesn't have format placeholders

    def test_translation_key_with_format_placeholders(self):
        """Test translation when key itself has format placeholders"""
        set_language("en")
        # Use a key that doesn't exist but has format placeholders
        result = t("key.with.{placeholder}", placeholder="value")
        # Should try to format the key
        assert result == "key.with.value"

    def test_translation_key_format_exception(self):
        """Test translation when key formatting raises exception"""
        set_language("en")
        # Use a key that doesn't exist and has invalid format
        result = t("key.with.{invalid", placeholder="value")
        # Should return the key as-is on exception
        assert result == "key.with.{invalid"

    def test_translation_fallback_when_current_lang_not_loaded(self):
        """Test translation fallback when current language translations not loaded"""
        # Set language but don't load translations
        set_language("en")
        # Clear translations to simulate not loaded
        from certica.i18n import _translations

        original = _translations.copy()
        _translations.clear()

        try:
            result = t("ui.menu.title")
            # Should return the key since no translations loaded
            assert result == "ui.menu.title"
        finally:
            # Restore translations
            _translations.update(original)
            set_language("en")

    def test_translation_fallback_to_english(self):
        """Test that translation falls back to English when current language missing"""
        set_language("fr")
        # French may not have all translations, should fall back to English
        result = t("ui.menu.title")
        assert result  # Should not be empty
        assert "CA" in result or "Certificate" in result

    def test_translation_empty_string(self):
        """Test translation with empty string key"""
        set_language("en")
        result = t("")
        assert result == ""

    def test_set_language_all_supported(self):
        """Test setting all supported languages"""
        for lang_code in SUPPORTED_LANGUAGES.keys():
            assert set_language(lang_code)
            assert get_language() == lang_code

    def test_translation_with_none_kwargs(self):
        """Test translation with None in kwargs"""
        set_language("en")
        result = t("lang.unsupported", lang=None)
        # Should handle None gracefully
        assert result  # Should not crash

    def test_translation_with_complex_format(self):
        """Test translation with complex format string"""
        set_language("en")
        result = t("ui.create_ca.error_exists", error="Test error message")
        assert "error" in result.lower() or "Test error message" in result
