"""
Exception handling tests for Cert Manager
"""

import pytest
import subprocess
from unittest.mock import patch
from pathlib import Path
from certica.cert_manager import CertManager
from certica.ca_manager import CAManager


class TestCertManagerExceptions:
    """Test exception handling in Cert Manager"""

    def test_sign_cert_keyboard_interrupt_cleanup(self, temp_dir, sample_ca_config, monkeypatch):
        """Test that KeyboardInterrupt during cert signing cleans up files"""
        ca_manager = CAManager(base_dir=str(temp_dir))
        cert_manager = CertManager(base_dir=str(temp_dir))
        
        ca_result = ca_manager.create_root_ca(**sample_ca_config)
        
        cert_output_dir = cert_manager.certs_dir / ca_result["ca_name"] / "test-cert"
        key_path = cert_output_dir / "key.pem"
        cert_path = cert_output_dir / "cert.pem"
        csr_path = cert_output_dir / "csr.pem"
        
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
            cert_manager.sign_certificate(
                ca_key=ca_result["ca_key"],
                ca_cert=ca_result["ca_cert"],
                ca_name=ca_result["ca_name"],
                cert_name="test-cert",
                cert_type="server",
                common_name="test.example.com",
                organization="Test Org",
                country="US",
                state="CA",
                city="SF",
                validity_days=365,
                key_size=2048
            )
        
        # Verify cleanup
        assert not key_path.exists()
        assert not cert_path.exists()
        assert not csr_path.exists()

    def test_sign_cert_exception_cleanup(self, temp_dir, sample_ca_config, monkeypatch):
        """Test that generic exception during cert signing cleans up files"""
        ca_manager = CAManager(base_dir=str(temp_dir))
        cert_manager = CertManager(base_dir=str(temp_dir))
        
        ca_result = ca_manager.create_root_ca(**sample_ca_config)
        
        cert_output_dir = cert_manager.certs_dir / ca_result["ca_name"] / "test-cert"
        key_path = cert_output_dir / "key.pem"
        
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
            cert_manager.sign_certificate(
                ca_key=ca_result["ca_key"],
                ca_cert=ca_result["ca_cert"],
                ca_name=ca_result["ca_name"],
                cert_name="test-cert",
                cert_type="server",
                common_name="test.example.com",
                organization="Test Org",
                country="US",
                state="CA",
                city="SF",
                validity_days=365,
                key_size=2048
            )
        
        # Verify cleanup
        assert not key_path.exists()

    def test_get_certificate_info_called_process_error(self, temp_dir):
        """Test get_certificate_info with CalledProcessError"""
        cert_manager = CertManager(base_dir=str(temp_dir))
        invalid_cert = temp_dir / "invalid.cert.pem"
        invalid_cert.write_text("not a valid certificate")
        
        result = cert_manager.get_certificate_info(str(invalid_cert))
        assert "Failed to read certificate" in result["info"]

    def test_delete_certificate_exception_handling(self, temp_dir, sample_ca_config, sample_cert_config):
        """Test delete_certificate exception handling"""
        ca_manager = CAManager(base_dir=str(temp_dir))
        cert_manager = CertManager(base_dir=str(temp_dir))
        
        ca_result = ca_manager.create_root_ca(**sample_ca_config)
        cert_result = cert_manager.sign_certificate(
            ca_key=ca_result["ca_key"],
            ca_cert=ca_result["ca_cert"],
            ca_name=sample_ca_config["ca_name"],
            cert_name=sample_cert_config["cert_name"],
            cert_type=sample_cert_config["cert_type"],
            common_name=sample_cert_config["common_name"],
            dns_names=sample_cert_config.get("dns_names", []),
            ip_addresses=sample_cert_config.get("ip_addresses", []),
            organization=sample_cert_config.get("organization", "Test Organization"),
            country=sample_cert_config.get("country", "US"),
            state=sample_cert_config.get("state", "CA"),
            city=sample_cert_config.get("city", "San Francisco"),
            validity_days=sample_cert_config["validity_days"],
            key_size=sample_cert_config["key_size"],
        )
        
        # Mock shutil.rmtree to raise exception
        with patch("shutil.rmtree", side_effect=Exception("Delete failed")):
            result = cert_manager.delete_certificate(
                sample_ca_config["ca_name"], sample_cert_config["cert_name"]
            )
            assert result is False

    def test_list_certificates_empty_directory(self, temp_dir):
        """Test list_certificates with empty directory"""
        cert_manager = CertManager(base_dir=str(temp_dir))
        certs = cert_manager.list_certificates()
        assert isinstance(certs, list)
        assert len(certs) == 0

