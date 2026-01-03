"""
Edge cases and additional tests for CLI module
"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from certica.cli import cli, _format_path
from certica.ca_manager import CAManager
from certica.cert_manager import CertManager


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing"""
    return CliRunner()


class TestCLIEdgeCases:
    """Test edge cases for CLI module"""

    def test_format_path_with_base_dir_prefix(self):
        """Test _format_path with base_dir prefix"""
        result = _format_path("output/ca/test-ca/test-ca.key.pem", "output")
        assert result == "ca/test-ca/test-ca.key.pem"

    def test_format_path_with_base_dir_prefix_windows(self):
        """Test _format_path with Windows-style path"""
        result = _format_path("output\\ca\\test-ca\\test-ca.key.pem", "output")
        # Result may have backslashes on Windows, normalize
        assert "ca" in result and "test-ca" in result and "test-ca.key.pem" in result

    def test_format_path_with_absolute_path(self, tmp_path):
        """Test _format_path with absolute path"""
        base_dir = tmp_path / "output"
        base_dir.mkdir()
        test_file = base_dir / "ca" / "test.key"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("test")
        
        result = _format_path(str(test_file), str(base_dir))
        assert "ca/test.key" in result

    def test_format_path_with_exception(self):
        """Test _format_path when exception occurs"""
        # Use invalid path that might cause exception
        result = _format_path("", "")
        # Should return empty string or handle gracefully
        assert isinstance(result, str)

    def test_cli_skip_check(self, cli_runner, temp_dir):
        """Test --skip-check option"""
        result = cli_runner.invoke(
            cli,
            [
                "--base-dir",
                str(temp_dir),
                "--skip-check",
                "list-cas",
            ],
        )
        assert result.exit_code == 0

    def test_cli_create_ca_with_template(self, cli_runner, temp_dir):
        """Test create-ca with template"""
        from certica.template_manager import TemplateManager
        
        # Create template first
        template_manager = TemplateManager(base_dir=str(temp_dir))
        template_manager.create_template("testtemplate", organization="Template Org")
        
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

    def test_cli_create_ca_with_all_options(self, cli_runner, temp_dir):
        """Test create-ca with all options"""
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
                "--country",
                "US",
                "--state",
                "CA",
                "--city",
                "San Francisco",
                "--validity",
                "730",
                "--key-size",
                "4096",
            ],
        )
        
        assert result.exit_code == 0
        assert "created successfully" in result.output.lower()

    def test_cli_sign_with_all_options(self, cli_runner, temp_dir):
        """Test sign command with all options"""
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
                "--cn",
                "example.com",
                "--dns",
                "example.com",
                "--dns",
                "www.example.com",
                "--ip",
                "127.0.0.1",
                "--ip",
                "::1",
                "--org",
                "Test Org",
                "--country",
                "US",
                "--state",
                "CA",
                "--city",
                "SF",
                "--validity",
                "365",
                "--key-size",
                "2048",
            ],
        )
        
        assert result.exit_code == 0
        assert "signed successfully" in result.output.lower()

    def test_cli_sign_with_template(self, cli_runner, temp_dir):
        """Test sign command with template"""
        from certica.template_manager import TemplateManager
        
        # Create CA and template
        manager = CAManager(base_dir=str(temp_dir))
        manager.create_root_ca(ca_name="testca")
        
        template_manager = TemplateManager(base_dir=str(temp_dir))
        template_manager.create_template("testtemplate", organization="Template Org")
        
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

    def test_cli_sign_client_cert(self, cli_runner, temp_dir):
        """Test sign command for client certificate"""
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
                "clientcert",
                "--type",
                "client",
            ],
        )
        
        assert result.exit_code == 0
        assert "signed successfully" in result.output.lower()

    def test_cli_list_certs_with_ca_filter(self, cli_runner, temp_dir):
        """Test list-certs with CA filter"""
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
        )
        
        result = cli_runner.invoke(
            cli,
            [
                "--base-dir",
                str(temp_dir),
                "--skip-check",
                "list-certs",
                "--ca",
                "testca",
            ],
        )
        
        assert result.exit_code == 0
        assert "testcert" in result.output

    def test_cli_list_certs_empty(self, cli_runner, temp_dir):
        """Test list-certs when no certificates exist"""
        result = cli_runner.invoke(
            cli,
            [
                "--base-dir",
                str(temp_dir),
                "--skip-check",
                "list-certs",
            ],
        )
        
        assert result.exit_code == 0
        assert "No certificates found" in result.output

    def test_cli_list_certs_empty_for_ca(self, cli_runner, temp_dir):
        """Test list-certs for CA with no certificates"""
        # Create CA but no certificates
        manager = CAManager(base_dir=str(temp_dir))
        manager.create_root_ca(ca_name="testca")
        
        result = cli_runner.invoke(
            cli,
            [
                "--base-dir",
                str(temp_dir),
                "--skip-check",
                "list-certs",
                "--ca",
                "testca",
            ],
        )
        
        assert result.exit_code == 0
        assert "No certificates found" in result.output

    def test_cli_list_certs_ca_not_found(self, cli_runner, temp_dir):
        """Test list-certs with non-existent CA"""
        result = cli_runner.invoke(
            cli,
            [
                "--base-dir",
                str(temp_dir),
                "--skip-check",
                "list-certs",
                "--ca",
                "nonexistent",
            ],
        )
        
        # May return 0 with error message or non-zero exit code
        assert "not found" in result.output.lower() or result.exit_code != 0

    def test_cli_info_command(self, cli_runner, temp_dir):
        """Test info command"""
        # Create CA and certificate
        ca_manager = CAManager(base_dir=str(temp_dir))
        ca_result = ca_manager.create_root_ca(ca_name="testca")
        
        result = cli_runner.invoke(
            cli,
            [
                "--base-dir",
                str(temp_dir),
                "--skip-check",
                "info",
                "--cert",
                ca_result["ca_cert"],
            ],
        )
        
        assert result.exit_code == 0
        assert "Certificate" in result.output or "Subject" in result.output

    def test_cli_info_invalid_cert(self, cli_runner, temp_dir):
        """Test info command with invalid certificate"""
        invalid_cert = temp_dir / "invalid.cert"
        invalid_cert.write_text("not a certificate")
        
        result = cli_runner.invoke(
            cli,
            [
                "--base-dir",
                str(temp_dir),
                "--skip-check",
                "info",
                "--cert",
                str(invalid_cert),
            ],
        )
        
        assert result.exit_code == 0
        assert "Failed" in result.output or "error" in result.output.lower()

    def test_cli_create_ca_duplicate_error(self, cli_runner, temp_dir):
        """Test create-ca with duplicate name"""
        # Create first CA
        result1 = cli_runner.invoke(
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
        assert result1.exit_code == 0
        
        # Try to create duplicate
        result2 = cli_runner.invoke(
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
        
        # May return 0 with error message or non-zero exit code
        assert "already exists" in result2.output.lower() or result2.exit_code != 0

    def test_cli_sign_ca_not_found(self, cli_runner, temp_dir):
        """Test sign command with non-existent CA"""
        result = cli_runner.invoke(
            cli,
            [
                "--base-dir",
                str(temp_dir),
                "--skip-check",
                "sign",
                "--ca",
                "nonexistent",
                "--name",
                "testcert",
            ],
        )
        
        # May return 0 with error message or non-zero exit code
        assert "not found" in result.output.lower() or result.exit_code != 0

    def test_cli_create_template_with_all_options(self, cli_runner, temp_dir):
        """Test create-template with all options"""
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
                "--country",
                "US",
                "--state",
                "CA",
                "--city",
                "SF",
                "--validity",
                "365",
                "--key-size",
                "2048",
            ],
        )
        
        assert result.exit_code == 0
        assert "created" in result.output.lower()

    def test_cli_list_templates_empty(self, cli_runner, temp_dir):
        """Test list-templates when no templates exist"""
        result = cli_runner.invoke(
            cli,
            [
                "--base-dir",
                str(temp_dir),
                "--skip-check",
                "list-templates",
            ],
        )
        
        assert result.exit_code == 0
        assert "No templates found" in result.output

