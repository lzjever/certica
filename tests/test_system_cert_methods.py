"""
Tests for System Cert Manager methods
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock, mock_open
from certica.system_cert import SystemCertManager


class TestSystemCertManagerMethods:
    """Test SystemCertManager methods"""

    @patch("subprocess.Popen")
    def test_run_sudo_command_with_password_success(self, mock_popen):
        """Test _run_sudo_command with password and success"""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("stdout", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        manager = SystemCertManager()
        success, error = manager._run_sudo_command(["test", "command"], "password")
        assert success is True
        assert error == ""

    @patch("subprocess.Popen")
    def test_run_sudo_command_with_password_failure(self, mock_popen):
        """Test _run_sudo_command with password and failure"""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("", "error message")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        manager = SystemCertManager()
        success, error = manager._run_sudo_command(["test", "command"], "password")
        assert success is False
        assert "error" in error.lower() or len(error) > 0

    @patch("subprocess.run")
    def test_run_sudo_command_without_password_success(self, mock_run):
        """Test _run_sudo_command without password and success"""
        mock_run.return_value = MagicMock(returncode=0)
        
        manager = SystemCertManager()
        success, error = manager._run_sudo_command(["test", "command"], None)
        assert success is True
        assert error == ""

    @patch("subprocess.run")
    def test_run_sudo_command_without_password_failure(self, mock_run):
        """Test _run_sudo_command without password and failure"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "test")
        
        manager = SystemCertManager()
        success, error = manager._run_sudo_command(["test", "command"], None)
        assert success is False
        assert len(error) > 0

    @patch("subprocess.run")
    def test_get_certificate_fingerprint_success(self, mock_run):
        """Test _get_certificate_fingerprint with success"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="SHA256 Fingerprint=AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99",
        )
        
        manager = SystemCertManager()
        fingerprint = manager._get_certificate_fingerprint("/path/to/cert.pem")
        assert fingerprint is not None
        assert "AA:BB" in fingerprint or len(fingerprint) > 0

    @patch("subprocess.run")
    def test_get_certificate_fingerprint_failure(self, mock_run):
        """Test _get_certificate_fingerprint with failure"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "openssl")
        
        manager = SystemCertManager()
        fingerprint = manager._get_certificate_fingerprint("/path/to/cert.pem")
        assert fingerprint is None

    @patch("subprocess.run")
    def test_get_certificate_fingerprint_no_match(self, mock_run):
        """Test _get_certificate_fingerprint when no fingerprint in output"""
        mock_run.return_value = MagicMock(returncode=0, stdout="No fingerprint here")
        
        manager = SystemCertManager()
        fingerprint = manager._get_certificate_fingerprint("/path/to/cert.pem")
        assert fingerprint is None

