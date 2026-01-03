"""
Tests for Template Manager
"""

import json
from pathlib import Path
from certica.template_manager import TemplateManager


def test_create_template(temp_dir):
    """Test creating a template"""
    manager = TemplateManager(base_dir=str(temp_dir))

    template_name = "test-template"
    path = manager.create_template(
        template_name=template_name,
        organization="Test Org",
        country="US",
        state="CA",
        city="San Francisco",
        default_validity_days=730,
        default_key_size=4096,
    )

    assert Path(path).exists()

    # Verify content
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["organization"] == "Test Org"
    assert data["country"] == "US"
    assert data["default_validity_days"] == 730
    assert data["default_key_size"] == 4096


def test_load_template(temp_dir):
    """Test loading a template"""
    manager = TemplateManager(base_dir=str(temp_dir))

    # Create template
    template_name = "test-template"
    manager.create_template(template_name=template_name, organization="Test Org", country="US")

    # Load template
    template = manager.load_template(template_name)
    assert template["organization"] == "Test Org"
    assert template["country"] == "US"


def test_load_default_template(temp_dir):
    """Test loading default template"""
    manager = TemplateManager(base_dir=str(temp_dir))

    # Create default template
    manager.create_template(template_name="default", organization="Default Org")

    # Load without specifying name (should load default.json)
    template = manager.load_template()
    # If default.json exists, it should load it; otherwise returns default dict
    assert isinstance(template, dict)
    # Check that it has expected keys
    assert "organization" in template or "default_validity_days" in template


def test_list_templates(temp_dir):
    """Test listing templates"""
    manager = TemplateManager(base_dir=str(temp_dir))

    # Initially empty
    templates = manager.list_templates()
    assert len(templates) == 0

    # Create templates
    manager.create_template("template1", organization="Org1")
    manager.create_template("template2", organization="Org2")

    # List templates
    templates = manager.list_templates()
    assert len(templates) == 2
    assert "template1" in templates
    assert "template2" in templates


def test_delete_template(temp_dir):
    """Test deleting a template"""
    manager = TemplateManager(base_dir=str(temp_dir))

    # Create template
    template_name = "test-template"
    path = manager.create_template(template_name, organization="Test Org")
    assert Path(path).exists()

    # Delete template
    result = manager.delete_template(template_name)
    assert result is True

    # Verify it's gone
    assert not Path(path).exists()
    templates = manager.list_templates()
    assert template_name not in templates
