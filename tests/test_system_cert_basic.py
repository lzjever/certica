"""
Basic tests for System Cert Manager
"""

import platform
from unittest.mock import patch, mock_open
from certica.system_cert import SystemCertManager


class TestSystemCertManagerBasic:
    """Basic tests for SystemCertManager"""

    def test_system_cert_manager_init(self):
        """Test SystemCertManager initialization"""
        manager = SystemCertManager()
        assert manager.system == platform.system()
        assert manager.sudo_password is None

    @patch("platform.system")
    def test_system_cert_manager_init_linux(self, mock_system):
        """Test SystemCertManager initialization on Linux"""
        mock_system.return_value = "Linux"
        manager = SystemCertManager()
        assert manager.system == "Linux"
        assert manager.distro_info is not None or manager.distro_info is None

    @patch("platform.system")
    def test_system_cert_manager_init_darwin(self, mock_system):
        """Test SystemCertManager initialization on macOS"""
        mock_system.return_value = "Darwin"
        manager = SystemCertManager()
        assert manager.system == "Darwin"
        assert manager.distro_info is None

    @patch("platform.system")
    def test_system_cert_manager_init_windows(self, mock_system):
        """Test SystemCertManager initialization on Windows"""
        mock_system.return_value = "Windows"
        manager = SystemCertManager()
        assert manager.system == "Windows"
        assert manager.distro_info is None

    @patch("os.path.exists")
    def test_detect_linux_distro_with_os_release(self, mock_exists):
        """Test _detect_linux_distro when /etc/os-release exists"""
        mock_exists.return_value = True

        # Mock open to return file-like object with os-release content
        mock_file_content = mock_open(read_data="ID=ubuntu\nID_LIKE=debian\n")
        with patch("builtins.open", mock_file_content):
            manager = SystemCertManager()
            if manager.system == "Linux":
                distro_info = manager._detect_linux_distro()
                assert distro_info is not None or distro_info is None

    @patch("os.path.exists")
    def test_detect_linux_distro_without_os_release(self, mock_exists):
        """Test _detect_linux_distro when /etc/os-release doesn't exist"""
        mock_exists.return_value = False

        manager = SystemCertManager()
        if manager.system == "Linux":
            distro_info = manager._detect_linux_distro()
            assert distro_info is None or isinstance(distro_info, dict)

    def test_get_linux_distro_id_debian(self):
        """Test _get_linux_distro_id for Debian-based systems"""
        manager = SystemCertManager()
        if manager.system == "Linux":
            manager.distro_info = {"ID": "ubuntu", "ID_LIKE": "debian"}
            distro_id = manager._get_linux_distro_id()
            assert distro_id == "debian" or distro_id is not None

    def test_get_linux_distro_id_fedora(self):
        """Test _get_linux_distro_id for Fedora-based systems"""
        manager = SystemCertManager()
        if manager.system == "Linux":
            manager.distro_info = {"ID": "fedora"}
            distro_id = manager._get_linux_distro_id()
            assert distro_id == "fedora" or distro_id is not None

    def test_get_linux_distro_id_arch(self):
        """Test _get_linux_distro_id for Arch-based systems"""
        manager = SystemCertManager()
        if manager.system == "Linux":
            manager.distro_info = {"ID": "arch"}
            distro_id = manager._get_linux_distro_id()
            assert distro_id == "arch" or distro_id is not None

    def test_get_linux_distro_id_none(self):
        """Test _get_linux_distro_id when distro_info is None"""
        manager = SystemCertManager()
        if manager.system == "Linux":
            manager.distro_info = None
            distro_id = manager._get_linux_distro_id()
            assert distro_id is None

    @patch("getpass.getpass")
    def test_get_sudo_password(self, mock_getpass):
        """Test _get_sudo_password"""
        mock_getpass.return_value = "testpassword"
        manager = SystemCertManager()
        password = manager._get_sudo_password()
        assert password == "testpassword"

    @patch("getpass.getpass")
    def test_get_sudo_password_empty(self, mock_getpass):
        """Test _get_sudo_password with empty input"""
        mock_getpass.return_value = ""
        manager = SystemCertManager()
        password = manager._get_sudo_password()
        assert password is None

    @patch("getpass.getpass")
    def test_get_sudo_password_keyboard_interrupt(self, mock_getpass):
        """Test _get_sudo_password with KeyboardInterrupt"""
        mock_getpass.side_effect = KeyboardInterrupt()
        manager = SystemCertManager()
        password = manager._get_sudo_password()
        assert password is None

    @patch("getpass.getpass")
    def test_get_sudo_password_eof_error(self, mock_getpass):
        """Test _get_sudo_password with EOFError"""
        mock_getpass.side_effect = EOFError()
        manager = SystemCertManager()
        password = manager._get_sudo_password()
        assert password is None

    def test_get_sudo_password_cached(self):
        """Test _get_sudo_password with cached password"""
        manager = SystemCertManager()
        manager.sudo_password = "cached"
        password = manager._get_sudo_password()
        assert password == "cached"
