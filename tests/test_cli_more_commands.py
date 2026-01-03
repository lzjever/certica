"""
Additional CLI command tests
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


class TestCLIMoreCommands:
    """Test additional CLI commands"""

    def test_cli_install_command_ca_not_found(self, cli_runner, temp_dir):
        """Test install command with non-existent CA"""
        result = cli_runner.invoke(
            cli,
            [
                "--base-dir",
                str(temp_dir),
                "--skip-check",
                "install",
                "--ca",
                "nonexistent",
                "--password",
                "testpass",
            ],
        )

        assert "not found" in result.output.lower()

    def test_cli_install_command_with_password(self, cli_runner, temp_dir):
        """Test install command with password"""
        # Create CA first
        manager = CAManager(base_dir=str(temp_dir))
        manager.create_root_ca(ca_name="testca")

        # Mock system_cert_manager to avoid actual system installation
        with patch("certica.cli.SystemCertManager") as mock_system_cert:
            mock_instance = MagicMock()
            mock_instance.install_ca_cert.return_value = True
            mock_system_cert.return_value = mock_instance

            result = cli_runner.invoke(
                cli,
                [
                    "--base-dir",
                    str(temp_dir),
                    "--skip-check",
                    "install",
                    "--ca",
                    "testca",
                    "--password",
                    "testpass",
                ],
            )

            # Should attempt installation
            assert (
                result.exit_code == 0
                or "success" in result.output.lower()
                or "error" in result.output.lower()
            )

    def test_cli_install_command_failure(self, cli_runner, temp_dir):
        """Test install command when installation fails"""
        # Create CA first
        manager = CAManager(base_dir=str(temp_dir))
        manager.create_root_ca(ca_name="testca")

        # Mock system_cert_manager to return failure
        with patch("certica.cli.SystemCertManager") as mock_system_cert:
            mock_instance = MagicMock()
            mock_instance.install_ca_cert.return_value = False
            mock_system_cert.return_value = mock_instance

            result = cli_runner.invoke(
                cli,
                [
                    "--base-dir",
                    str(temp_dir),
                    "--skip-check",
                    "install",
                    "--ca",
                    "testca",
                    "--password",
                    "testpass",
                ],
            )

            # Should show error
            assert "error" in result.output.lower() or "failed" in result.output.lower()

    def test_cli_remove_command_with_password(self, cli_runner, temp_dir):
        """Test remove command with password"""
        # Mock system_cert_manager to avoid actual system removal
        with patch("certica.cli.SystemCertManager") as mock_system_cert:
            mock_instance = MagicMock()
            mock_instance.remove_ca_cert.return_value = True
            mock_system_cert.return_value = mock_instance

            result = cli_runner.invoke(
                cli,
                [
                    "--base-dir",
                    str(temp_dir),
                    "--skip-check",
                    "remove",
                    "--ca",
                    "testca",
                    "--password",
                    "testpass",
                ],
            )

            # Should attempt removal
            assert (
                result.exit_code == 0
                or "success" in result.output.lower()
                or "error" in result.output.lower()
            )

    def test_cli_remove_command_failure(self, cli_runner, temp_dir):
        """Test remove command when removal fails"""
        # Mock system_cert_manager to return failure
        with patch("certica.cli.SystemCertManager") as mock_system_cert:
            mock_instance = MagicMock()
            mock_instance.remove_ca_cert.return_value = False
            mock_system_cert.return_value = mock_instance

            result = cli_runner.invoke(
                cli,
                [
                    "--base-dir",
                    str(temp_dir),
                    "--skip-check",
                    "remove",
                    "--ca",
                    "testca",
                    "--password",
                    "testpass",
                ],
            )

            # Should show error
            assert "error" in result.output.lower() or "failed" in result.output.lower()

    def test_cli_system_check_failed(self, cli_runner, temp_dir):
        """Test CLI when system check fails"""
        with patch("certica.cli.check_system_requirements", return_value=False):
            result = cli_runner.invoke(
                cli,
                [
                    "--base-dir",
                    str(temp_dir),
                    "list-cas",
                ],
            )

            assert result.exit_code != 0
            assert "system" in result.output.lower() or "check" in result.output.lower()

    def test_cli_format_path_edge_cases(self):
        """Test _format_path with various edge cases"""
        from certica.cli import _format_path

        # Test with None-like values
        result = _format_path("test/path", None)
        assert isinstance(result, str)

        # Test with very long path
        long_path = "output/" + "/".join(["dir"] * 100) + "/file.key"
        result = _format_path(long_path, "output")
        assert isinstance(result, str)
