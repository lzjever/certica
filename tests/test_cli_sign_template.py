"""
Tests for CLI sign command with template
"""

import pytest
from click.testing import CliRunner
from certica.cli import cli
from certica.ca_manager import CAManager
from certica.template_manager import TemplateManager


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing"""
    return CliRunner()


class TestCLISignTemplate:
    """Test sign command with template"""

    def test_cli_sign_with_template_overrides(self, cli_runner, temp_dir):
        """Test sign command with template that overrides defaults (covers line 144-151)"""
        # Create CA and template
        ca_manager = CAManager(base_dir=str(temp_dir))
        ca_manager.create_root_ca(ca_name="testca")

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
                "sign",
                "--ca",
                "testca",
                "--name",
                "testcert",
                "--template",
                "testtemplate",
            ],
        )

        assert result.exit_code == 0
        assert "signed successfully" in result.output.lower()
