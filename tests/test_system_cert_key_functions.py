"""
Tests for key functions in System Cert Manager
"""

from unittest.mock import patch, MagicMock
from certica.system_cert import SystemCertManager


class TestSystemCertKeyFunctions:
    """Test key functions in SystemCertManager"""

    def test_install_ca_cert_basic(self, temp_dir):
        """Test install_ca_cert basic functionality"""
        manager = SystemCertManager()

        # Create a dummy cert file
        cert_path = temp_dir / "test.cert.pem"
        cert_path.write_text("-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----")

        # Mock the platform-specific install methods
        with patch.object(manager, "_install_linux", return_value=True):
            result = manager.install_ca_cert(str(cert_path), "test-ca", "password")
            assert result is True

    def test_install_ca_cert_verification_failure(self, temp_dir):
        """Test install_ca_cert when verification fails"""
        manager = SystemCertManager()

        cert_path = temp_dir / "test.cert.pem"
        cert_path.write_text("-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----")

        # Mock install to succeed but verification to fail
        # The implementation should return False when verification fails
        with patch.object(manager, "_install_linux", return_value=False):
            result = manager.install_ca_cert(str(cert_path), "test-ca", "password")
            assert result is False

    def test_remove_ca_cert_basic(self):
        """Test remove_ca_cert basic functionality"""
        manager = SystemCertManager()

        # Mock the platform-specific remove methods
        with patch.object(manager, "_remove_linux", return_value=True):
            result = manager.remove_ca_cert("test-ca", "password")
            assert result is True

    def test_remove_ca_cert_verification_failure(self):
        """Test remove_ca_cert when verification fails"""
        manager = SystemCertManager()

        # Mock remove to succeed but verification to fail
        # The implementation should return False when verification fails
        with patch.object(manager, "_remove_linux", return_value=False):
            result = manager.remove_ca_cert("test-ca", "password")
            assert result is False

    @patch("platform.system")
    def test_install_ca_cert_linux_success(self, mock_system, temp_dir):
        """Test install_ca_cert on Linux with successful installation and verification"""
        mock_system.return_value = "Linux"
        manager = SystemCertManager()

        cert_path = temp_dir / "test.cert.pem"
        cert_path.write_text("-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----")

        # Mock Linux-specific installation with successful verification
        with patch.object(manager, "_get_linux_distro_id", return_value="debian"):
            with patch.object(manager, "_run_sudo_command", return_value=(True, "")):
                with patch.object(manager, "_get_certificate_fingerprint", return_value="TEST123"):
                    with patch("os.path.exists", return_value=True):
                        with patch.object(manager, "_verify_installation", return_value=True):
                            result = manager._install_linux(str(cert_path), "test-ca", "password")
                            assert result is True

    @patch("platform.system")
    def test_install_ca_cert_linux_verification_fails(self, mock_system, temp_dir):
        """Test install_ca_cert on Linux when verification fails"""
        mock_system.return_value = "Linux"
        manager = SystemCertManager()

        cert_path = temp_dir / "test.cert.pem"
        cert_path.write_text("-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----")

        # Mock Linux-specific installation with failed verification
        with patch.object(manager, "_get_linux_distro_id", return_value="debian"):
            with patch.object(manager, "_run_sudo_command", return_value=(True, "")):
                with patch("os.path.exists", return_value=True):
                    with patch.object(manager, "_verify_installation", return_value=False):
                        result = manager._install_linux(str(cert_path), "test-ca", "password")
                        assert result is False

    @patch("platform.system")
    def test_install_ca_cert_macos_success(self, mock_system, temp_dir):
        """Test install_ca_cert on macOS with success"""
        mock_system.return_value = "Darwin"
        manager = SystemCertManager()

        cert_path = temp_dir / "test.cert.pem"
        cert_path.write_text("-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----")

        # Mock macOS-specific installation with success
        with patch.object(manager, "_run_sudo_command", return_value=(True, "")):
            result = manager._install_macos(str(cert_path), "test-ca", "password")
            assert result is True

    @patch("platform.system")
    def test_install_ca_cert_macos_failure(self, mock_system, temp_dir):
        """Test install_ca_cert on macOS with failure"""
        mock_system.return_value = "Darwin"
        manager = SystemCertManager()

        cert_path = temp_dir / "test.cert.pem"
        cert_path.write_text("-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----")

        # Mock macOS-specific installation with failure
        with patch.object(manager, "_run_sudo_command", return_value=(False, "Error")):
            result = manager._install_macos(str(cert_path), "test-ca", "password")
            assert result is False

    @patch("platform.system")
    def test_install_ca_cert_windows_success(self, mock_system, temp_dir):
        """Test install_ca_cert on Windows with success"""
        mock_system.return_value = "Windows"
        manager = SystemCertManager()

        cert_path = temp_dir / "test.cert.pem"
        cert_path.write_text("-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----")

        # Mock Windows-specific installation with success
        with patch("subprocess.run", return_value=MagicMock(returncode=0)):
            result = manager._install_windows(str(cert_path), "test-ca")
            assert result is True

    @patch("platform.system")
    def test_install_ca_cert_windows_failure(self, mock_system, temp_dir):
        """Test install_ca_cert on Windows with failure"""
        mock_system.return_value = "Windows"
        manager = SystemCertManager()

        cert_path = temp_dir / "test.cert.pem"
        cert_path.write_text("-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----")

        # Mock Windows-specific installation with failure
        import subprocess

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "certutil")):
            result = manager._install_windows(str(cert_path), "test-ca")
            assert result is False

    @patch("platform.system")
    def test_remove_ca_cert_linux_success(self, mock_system):
        """Test remove_ca_cert on Linux with successful removal and verification"""
        mock_system.return_value = "Linux"
        manager = SystemCertManager()

        # Mock Linux-specific removal with successful verification
        # Need to mock Path.exists() for the cert_path check
        from pathlib import Path

        with patch.object(manager, "_get_linux_distro_id", return_value="debian"):
            with patch.object(manager, "_run_sudo_command", return_value=(True, "")):
                with patch.object(Path, "exists", return_value=True):
                    with patch.object(manager, "_verify_removal", return_value=True):
                        result = manager._remove_linux("test-ca", "password")
                        assert result is True

    @patch("platform.system")
    def test_remove_ca_cert_linux_verification_fails(self, mock_system):
        """Test remove_ca_cert on Linux when verification fails"""
        mock_system.return_value = "Linux"
        manager = SystemCertManager()

        # Mock Linux-specific removal with failed verification
        with patch.object(manager, "_get_linux_distro_id", return_value="debian"):
            with patch.object(manager, "_run_sudo_command", return_value=(True, "")):
                with patch("os.path.exists", return_value=True):
                    with patch.object(manager, "_verify_removal", return_value=False):
                        result = manager._remove_linux("test-ca", "password")
                        assert result is False

    @patch("platform.system")
    def test_remove_ca_cert_macos_success(self, mock_system):
        """Test remove_ca_cert on macOS with success"""
        mock_system.return_value = "Darwin"
        manager = SystemCertManager()

        # Mock macOS-specific removal with success
        with patch("subprocess.run", return_value=MagicMock(returncode=0)):
            with patch.object(manager, "_run_sudo_command", return_value=(True, "")):
                result = manager._remove_macos("test-ca", "password")
                assert result is True

    @patch("platform.system")
    def test_remove_ca_cert_macos_not_found(self, mock_system):
        """Test remove_ca_cert on macOS when certificate not found"""
        mock_system.return_value = "Darwin"
        manager = SystemCertManager()

        # Mock macOS-specific removal when certificate not found
        with patch("subprocess.run", return_value=MagicMock(returncode=1)):
            result = manager._remove_macos("test-ca", "password")
            assert result is False

    @patch("platform.system")
    def test_remove_ca_cert_windows_success(self, mock_system):
        """Test remove_ca_cert on Windows with success"""
        mock_system.return_value = "Windows"
        manager = SystemCertManager()

        # Mock Windows-specific removal with success
        with patch("subprocess.run", return_value=MagicMock(returncode=0)):
            result = manager._remove_windows("test-ca")
            assert result is True

    @patch("platform.system")
    def test_remove_ca_cert_windows_failure(self, mock_system):
        """Test remove_ca_cert on Windows with failure"""
        mock_system.return_value = "Windows"
        manager = SystemCertManager()

        # Mock Windows-specific removal with failure
        import subprocess

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "certutil")):
            result = manager._remove_windows("test-ca")
            assert result is False
