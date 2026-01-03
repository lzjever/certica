"""
Exception handling tests for CA Manager
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path
from certica.ca_manager import CAManager


class TestCAManagerExceptions:
    """Test exception handling in CA Manager"""

    def test_create_ca_keyboard_interrupt_cleanup(self, temp_dir, monkeypatch):
        """Test that KeyboardInterrupt during CA creation cleans up files"""
        manager = CAManager(base_dir=str(temp_dir))
        ca_subdir = manager.ca_dir / "test-ca"
        
        # Mock subprocess to raise KeyboardInterrupt after key generation
        original_run = subprocess.run
        call_count = [0]
        
        def mock_run(cmd, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:  # First call (genrsa) succeeds
                return original_run(cmd, **kwargs)
            else:  # Second call (req) raises KeyboardInterrupt
                raise KeyboardInterrupt()
        
        monkeypatch.setattr("subprocess.run", mock_run)
        
        with pytest.raises(KeyboardInterrupt):
            manager.create_root_ca(
                ca_name="test-ca",
                organization="Test",
                country="US",
                state="CA",
                city="SF",
                validity_days=365,
                key_size=2048
            )
        
        # Verify cleanup
        key_path = ca_subdir / "test-ca.key.pem"
        cert_path = ca_subdir / "test-ca.cert.pem"
        assert not key_path.exists()
        assert not cert_path.exists()

    def test_create_ca_exception_cleanup(self, temp_dir, monkeypatch):
        """Test that generic exception during CA creation cleans up files"""
        manager = CAManager(base_dir=str(temp_dir))
        ca_subdir = manager.ca_dir / "test-ca"
        
        # Mock subprocess to raise exception after key generation
        original_run = subprocess.run
        call_count = [0]
        
        def mock_run(cmd, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:  # First call (genrsa) succeeds
                return original_run(cmd, **kwargs)
            else:  # Second call (req) raises exception
                raise Exception("Test exception")
        
        monkeypatch.setattr("subprocess.run", mock_run)
        
        with pytest.raises(Exception):
            manager.create_root_ca(
                ca_name="test-ca",
                organization="Test",
                country="US",
                state="CA",
                city="SF",
                validity_days=365,
                key_size=2048
            )
        
        # Verify cleanup
        key_path = ca_subdir / "test-ca.key.pem"
        cert_path = ca_subdir / "test-ca.cert.pem"
        assert not key_path.exists()
        assert not cert_path.exists()

    def test_get_ca_info_called_process_error(self, temp_dir):
        """Test get_ca_info with CalledProcessError"""
        manager = CAManager(base_dir=str(temp_dir))
        invalid_cert = temp_dir / "invalid.cert.pem"
        invalid_cert.write_text("not a valid certificate")
        
        result = manager.get_ca_info(str(invalid_cert))
        assert "Failed to read certificate" in result["info"]

    def test_delete_ca_exception_handling(self, temp_dir, monkeypatch):
        """Test delete_ca exception handling"""
        manager = CAManager(base_dir=str(temp_dir))
        manager.create_root_ca(ca_name="test-ca", organization="Test")
        
        # Mock shutil.rmtree to raise exception
        with patch("shutil.rmtree", side_effect=Exception("Delete failed")):
            result = manager.delete_ca("test-ca")
            assert result is False

    def test_list_cas_with_exception_in_iterdir(self, temp_dir, monkeypatch):
        """Test list_cas when iterdir raises exception"""
        manager = CAManager(base_dir=str(temp_dir))
        
        # Mock iterdir to raise exception
        with patch.object(manager.ca_dir, "iterdir", side_effect=PermissionError("Access denied")):
            # Should handle exception gracefully
            cas = manager.list_cas()
            # Result depends on implementation, but should not crash
            assert isinstance(cas, list)

