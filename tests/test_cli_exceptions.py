"""
Tests for CLI exception handling
"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from certica.cli import cli
from certica.ca_manager import CAManager


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing"""
    return CliRunner()


class TestCLIExceptions:
    """Test CLI exception handling"""

    def test_cli_create_ca_file_exists_error(self, cli_runner, temp_dir):
        """Test create-ca with FileExistsError (covers line 108-109)"""
        # Create CA first
        manager = CAManager(base_dir=str(temp_dir))
        manager.create_root_ca(ca_name="testca")

        result = cli_runner.invoke(
            cli,
            [
                "--base-dir",
                str(temp_dir),
                "--skip-check",
                "create-ca",
                "--name",
                "testca",
            ],
        )

        assert "error" in result.output.lower() or "already exists" in result.output.lower()

    def test_cli_create_ca_generic_exception(self, cli_runner, temp_dir, monkeypatch):
        """Test create-ca with generic exception (covers line 110-111)"""
        # Mock create_root_ca to raise generic exception
        with patch("certica.cli.CAManager") as mock_ca_manager:
            mock_instance = MagicMock()
            mock_instance.create_root_ca.side_effect = Exception("Test error")
            mock_ca_manager.return_value = mock_instance

            result = cli_runner.invoke(
                cli,
                [
                    "--base-dir",
                    str(temp_dir),
                    "--skip-check",
                    "create-ca",
                    "--name",
                    "testca",
                ],
            )

            assert "error" in result.output.lower() or "failed" in result.output.lower()

    def test_cli_sign_exception_handling(self, cli_runner, temp_dir, monkeypatch):
        """Test sign command exception handling (covers line 174-175)"""
        # Create CA first
        manager = CAManager(base_dir=str(temp_dir))
        manager.create_root_ca(ca_name="testca")

        # Mock sign_certificate to raise exception
        with patch("certica.cli.CertManager") as mock_cert_manager:
            mock_instance = MagicMock()
            mock_instance.sign_certificate.side_effect = Exception("Sign error")
            mock_cert_manager.return_value = mock_instance

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
                ],
            )

            assert "error" in result.output.lower() or "failed" in result.output.lower()

    def test_cli_install_password_prompt_empty(self, cli_runner, temp_dir):
        """Test install command with empty password prompt (covers line 288-291)"""
        # Create CA first
        manager = CAManager(base_dir=str(temp_dir))
        manager.create_root_ca(ca_name="testca")

        # Mock click.prompt to return empty string
        with patch("click.prompt", return_value=""):
            result = cli_runner.invoke(
                cli,
                [
                    "--base-dir",
                    str(temp_dir),
                    "--skip-check",
                    "install",
                    "--ca",
                    "testca",
                ],
                input="\n",  # Empty input
            )

            assert "password" in result.output.lower() or "required" in result.output.lower()

    def test_cli_remove_password_prompt_empty(self, cli_runner, temp_dir):
        """Test remove command with empty password prompt (covers line 309-312)"""
        # Mock click.prompt to return empty string
        with patch("click.prompt", return_value=""):
            result = cli_runner.invoke(
                cli,
                [
                    "--base-dir",
                    str(temp_dir),
                    "--skip-check",
                    "remove",
                    "--ca",
                    "testca",
                ],
                input="\n",  # Empty input
            )

            assert "password" in result.output.lower() or "required" in result.output.lower()
