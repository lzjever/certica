"""
Edge cases for Template Manager
"""

import pytest
from pathlib import Path
from certica.template_manager import TemplateManager


class TestTemplateManagerEdgeCases:
    """Test edge cases for Template Manager"""

    def test_delete_template_nonexistent(self, temp_dir):
        """Test deleting non-existent template"""
        manager = TemplateManager(base_dir=str(temp_dir))
        result = manager.delete_template("nonexistent")
        assert result is False

    def test_load_template_nonexistent_returns_defaults(self, temp_dir):
        """Test loading non-existent template returns default values"""
        manager = TemplateManager(base_dir=str(temp_dir))
        template = manager.load_template("nonexistent")
        
        assert template["organization"] == "Development"
        assert template["country"] == "CN"
        assert template["state"] == "Beijing"
        assert template["city"] == "Beijing"
        assert template["default_validity_days"] == 365
        assert template["default_key_size"] == 2048

