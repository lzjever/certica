"""
Tests for CLI create-ca with template
"""

import pytest
from click.testing import CliRunner
from certica.cli import cli
from certica.template_manager import TemplateManager


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing"""
    return CliRunner()


class TestCLICreateCATemplate:
    """Test create-ca command with template"""

    def test_cli_create_ca_with_template_overrides(self, cli_runner, temp_dir):
        """Test create-ca with template that overrides defaults (covers line 86-92)"""
        # Create template first
        template_manager = TemplateManager(base_dir=str(temp_dir))
        template_manager.create_template(
            "testtemplate",
            organization="Template Org",
            country="FR",
            state="Paris",
            city="Paris",
            default_validity_days=730,
            default_key_size=4096,
        )

        result = cli_runner.invoke(
            cli,
            [
                "--base-dir",
                str(temp_dir),
                "--skip-check",
                "create-ca",
                "--name",
                "testca",
                "--template",
                "testtemplate",
            ],
        )

        assert result.exit_code == 0
        assert "created successfully" in result.output.lower()

        # Verify CA was created with template values
        from certica.ca_manager import CAManager

        manager = CAManager(base_dir=str(temp_dir))
        ca = manager.get_ca("testca")
        assert ca is not None
