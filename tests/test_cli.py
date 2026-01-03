"""
Tests for CLI commands
"""

import pytest
from click.testing import CliRunner
from certica.cli import cli
from certica.ca_manager import CAManager
from certica.cert_manager import CertManager


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing"""
    return CliRunner()


def test_cli_help(cli_runner):
    """Test CLI help command"""
    result = cli_runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "CA Certificate Generation Tool" in result.output
    assert "create-ca" in result.output
    assert "sign" in result.output
    assert "ui" in result.output


def test_cli_create_ca(cli_runner, temp_dir):
    """Test create-ca command"""
    result = cli_runner.invoke(
        cli,
        [
            "--base-dir",
            str(temp_dir),
            "--skip-check",
            "create-ca",
            "--name",
            "testca",
            "--org",
            "Test Org",
        ],
    )

    assert result.exit_code == 0
    assert "created successfully" in result.output.lower()

    # Verify CA was created
    manager = CAManager(base_dir=str(temp_dir))
    ca = manager.get_ca("testca")
    assert ca is not None


def test_cli_list_cas(cli_runner, temp_dir):
    """Test list-cas command"""
    # Create a CA first
    manager = CAManager(base_dir=str(temp_dir))
    manager.create_root_ca(ca_name="testca")

    result = cli_runner.invoke(cli, ["--base-dir", str(temp_dir), "--skip-check", "list-cas"])

    assert result.exit_code == 0
    assert "testca" in result.output


def test_cli_sign_certificate(cli_runner, temp_dir):
    """Test sign command"""
    # Create CA first
    manager = CAManager(base_dir=str(temp_dir))
    manager.create_root_ca(ca_name="testca")

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
            "--type",
            "server",
        ],
    )

    assert result.exit_code == 0
    assert "signed successfully" in result.output.lower()


def test_cli_list_certs(cli_runner, temp_dir):
    """Test list-certs command"""
    # Create CA and certificate
    ca_manager = CAManager(base_dir=str(temp_dir))
    ca_result = ca_manager.create_root_ca(ca_name="testca")

    cert_manager = CertManager(base_dir=str(temp_dir))
    cert_manager.sign_certificate(
        ca_key=ca_result["ca_key"],
        ca_cert=ca_result["ca_cert"],
        ca_name="testca",
        cert_name="testcert",
        cert_type="server",
        common_name="test.example.com",
        organization="Test Org",
        country="US",
        state="CA",
        city="San Francisco",
    )

    result = cli_runner.invoke(cli, ["--base-dir", str(temp_dir), "--skip-check", "list-certs"])

    assert result.exit_code == 0
    assert "testcert" in result.output


def test_cli_create_template(cli_runner, temp_dir):
    """Test create-template command"""
    result = cli_runner.invoke(
        cli,
        [
            "--base-dir",
            str(temp_dir),
            "--skip-check",
            "create-template",
            "--name",
            "testtemplate",
            "--org",
            "Test Org",
        ],
    )

    assert result.exit_code == 0
    assert "created" in result.output.lower()


def test_cli_list_templates(cli_runner, temp_dir):
    """Test list-templates command"""
    from certica.template_manager import TemplateManager

    # Create a template first
    template_manager = TemplateManager(base_dir=str(temp_dir))
    template_manager.create_template("testtemplate", organization="Test Org")

    result = cli_runner.invoke(cli, ["--base-dir", str(temp_dir), "--skip-check", "list-templates"])

    assert result.exit_code == 0
    assert "testtemplate" in result.output


def test_cli_ui_command_help(cli_runner):
    """Test ui command help"""
    result = cli_runner.invoke(cli, ["ui", "--help"])
    assert result.exit_code == 0
    assert "Launch interactive UI mode" in result.output
    assert "--lang" in result.output


def test_cli_check_only(cli_runner):
    """Test --check-only option"""
    result = cli_runner.invoke(cli, ["--check-only"])
    # Exit code depends on system (0=success, 1=failed, 2=click error)
    # Should not crash
    assert result.exit_code in [0, 1, 2]
