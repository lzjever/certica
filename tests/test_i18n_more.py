"""
Additional tests for i18n module to cover remaining lines
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from certica.i18n import _load_translations, t, set_language


class TestI18nMore:
    """Additional tests for i18n module"""

    def test_load_translations_file_exists_but_json_error(self, tmp_path):
        """Test _load_translations when file exists but JSON load fails (covers line 39-40)"""
        # Create a locale file with invalid JSON
        locale_file = tmp_path / "test.json"
        locale_file.write_text("{ invalid json }")
        
        # Mock the Path(__file__).parent to return our test directory
        with patch("certica.i18n.Path") as mock_path:
            # Mock Path(__file__) to return a path with parent pointing to tmp_path
            mock_file_path = MagicMock()
            mock_file_path.parent = tmp_path
            mock_path.return_value = mock_file_path
            
            # Create locales directory
            (tmp_path / "locales").mkdir(exist_ok=True)
            (tmp_path / "locales" / "test.json").write_text("{ invalid json }")
            
            result = _load_translations("test")
            # Should return empty dict on exception
            assert result == {}

    def test_translation_format_exception_in_current_lang(self):
        """Test translation when format raises exception in current language (covers line 95-96)"""
        set_language("en")
        
        # Use a translation that exists but with invalid format args
        # This should trigger the exception handler at line 95-96
        result = t("ui.menu.title", invalid_arg="test")
        # Should return translation without formatting
        assert result == "🔒 CA Certificate Tool"

    def test_translation_format_exception_in_fallback(self):
        """Test translation when format raises exception in fallback (covers line 102-105)"""
        set_language("fr")  # French may not have all translations
        
        # Clear French translations to force fallback
        from certica.i18n import _translations
        original = _translations.get("fr", {}).copy()
        if "fr" in _translations:
            _translations["fr"] = {}
        
        try:
            # This should fall back to English and handle format exception
            result = t("ui.menu.title", invalid_arg="test")
            # Should return translation without formatting
            assert result  # Should not be empty
        finally:
            # Restore translations
            if original:
                _translations["fr"] = original
            set_language("en")

    def test_translation_key_format_with_kwargs_exception(self):
        """Test translation when key formatting with kwargs raises exception (covers line 111)"""
        set_language("en")
        
        # Use a key that doesn't exist and has invalid format
        result = t("key.{invalid", placeholder="value")
        # Should return key as-is on exception
        assert result == "key.{invalid"

