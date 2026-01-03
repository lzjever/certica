"""
Edge cases and boundary condition tests for Cert Manager
"""

import pytest
from pathlib import Path
from certica.cert_manager import CertManager
from certica.ca_manager import CAManager


class TestCertManagerEdgeCases:
    """Test edge cases and boundary conditions for Cert Manager"""

    def test_sign_cert_with_empty_dns_and_ip(self, temp_dir, sample_ca_config):
        """Test signing certificate with empty DNS and IP lists"""
        ca_manager = CAManager(base_dir=str(temp_dir))
        cert_manager = CertManager(base_dir=str(temp_dir))

        ca_result = ca_manager.create_root_ca(**sample_ca_config)

        result = cert_manager.sign_certificate(
            ca_key=ca_result["ca_key"],
            ca_cert=ca_result["ca_cert"],
            ca_name=ca_result["ca_name"],
            cert_name="test-cert",
            cert_type="server",
            common_name="test.example.com",
            dns_names=[],
            ip_addresses=[],
            organization="Test Org",
            country="US",
            state="CA",
            city="SF",
            validity_days=365,
            key_size=2048,
        )

        assert result["cert_name"] == "test-cert"
        assert Path(result["key"]).exists()
        assert Path(result["cert"]).exists()

    def test_sign_cert_common_name_from_dns(self, temp_dir, sample_ca_config):
        """Test that common_name defaults to first DNS name when not provided"""
        ca_manager = CAManager(base_dir=str(temp_dir))
        cert_manager = CertManager(base_dir=str(temp_dir))

        ca_result = ca_manager.create_root_ca(**sample_ca_config)

        result = cert_manager.sign_certificate(
            ca_key=ca_result["ca_key"],
            ca_cert=ca_result["ca_cert"],
            ca_name=ca_result["ca_name"],
            cert_name="test-cert",
            cert_type="server",
            common_name="",  # Empty, should use first DNS
            dns_names=["example.com", "www.example.com"],
            ip_addresses=[],
            organization="Test Org",
            country="US",
            state="CA",
            city="SF",
            validity_days=365,
            key_size=2048,
        )

        assert result["cert_name"] == "test-cert"
        assert Path(result["key"]).exists()
        assert Path(result["cert"]).exists()

    def test_sign_cert_common_name_from_ip(self, temp_dir, sample_ca_config):
        """Test that common_name defaults to first IP when no DNS and not provided"""
        ca_manager = CAManager(base_dir=str(temp_dir))
        cert_manager = CertManager(base_dir=str(temp_dir))

        ca_result = ca_manager.create_root_ca(**sample_ca_config)

        result = cert_manager.sign_certificate(
            ca_key=ca_result["ca_key"],
            ca_cert=ca_result["ca_cert"],
            ca_name=ca_result["ca_name"],
            cert_name="test-cert",
            cert_type="server",
            common_name="",  # Empty, no DNS, should use first IP
            dns_names=[],
            ip_addresses=["127.0.0.1", "192.168.1.1"],
            organization="Test Org",
            country="US",
            state="CA",
            city="SF",
            validity_days=365,
            key_size=2048,
        )

        assert result["cert_name"] == "test-cert"
        assert Path(result["key"]).exists()
        assert Path(result["cert"]).exists()

    def test_sign_cert_common_name_from_cert_name(self, temp_dir, sample_ca_config):
        """Test that common_name defaults to cert_name when nothing else provided"""
        ca_manager = CAManager(base_dir=str(temp_dir))
        cert_manager = CertManager(base_dir=str(temp_dir))

        ca_result = ca_manager.create_root_ca(**sample_ca_config)

        result = cert_manager.sign_certificate(
            ca_key=ca_result["ca_key"],
            ca_cert=ca_result["ca_cert"],
            ca_name=ca_result["ca_name"],
            cert_name="my-cert",
            cert_type="server",
            common_name="",  # Empty, no DNS, no IP, should use cert_name
            dns_names=[],
            ip_addresses=[],
            organization="Test Org",
            country="US",
            state="CA",
            city="SF",
            validity_days=365,
            key_size=2048,
        )

        assert result["cert_name"] == "my-cert"
        assert Path(result["key"]).exists()
        assert Path(result["cert"]).exists()

    def test_sign_cert_with_multiple_dns_and_ips(self, temp_dir, sample_ca_config):
        """Test signing certificate with multiple DNS names and IP addresses"""
        ca_manager = CAManager(base_dir=str(temp_dir))
        cert_manager = CertManager(base_dir=str(temp_dir))

        ca_result = ca_manager.create_root_ca(**sample_ca_config)

        result = cert_manager.sign_certificate(
            ca_key=ca_result["ca_key"],
            ca_cert=ca_result["ca_cert"],
            ca_name=ca_result["ca_name"],
            cert_name="test-cert",
            cert_type="server",
            common_name="example.com",
            dns_names=["example.com", "www.example.com", "api.example.com"],
            ip_addresses=["127.0.0.1", "192.168.1.1", "10.0.0.1"],
            organization="Test Org",
            country="US",
            state="CA",
            city="SF",
            validity_days=365,
            key_size=2048,
        )

        assert result["cert_name"] == "test-cert"
        assert Path(result["key"]).exists()
        assert Path(result["cert"]).exists()

    def test_sign_client_cert(self, temp_dir, sample_ca_config):
        """Test signing client certificate"""
        ca_manager = CAManager(base_dir=str(temp_dir))
        cert_manager = CertManager(base_dir=str(temp_dir))

        ca_result = ca_manager.create_root_ca(**sample_ca_config)

        result = cert_manager.sign_certificate(
            ca_key=ca_result["ca_key"],
            ca_cert=ca_result["ca_cert"],
            ca_name=ca_result["ca_name"],
            cert_name="client-cert",
            cert_type="client",
            common_name="client.example.com",
            dns_names=[],
            ip_addresses=[],
            organization="Test Org",
            country="US",
            state="CA",
            city="SF",
            validity_days=365,
            key_size=2048,
        )

        assert result["cert_name"] == "client-cert"
        assert result["type"] == "client"
        assert Path(result["key"]).exists()
        assert Path(result["cert"]).exists()

    def test_list_certificates_with_incomplete_certs(self, temp_dir, sample_ca_config):
        """Test listing certificates when some cert directories are incomplete"""
        ca_manager = CAManager(base_dir=str(temp_dir))
        cert_manager = CertManager(base_dir=str(temp_dir))

        ca_result = ca_manager.create_root_ca(**sample_ca_config)

        # Create complete cert
        cert_manager.sign_certificate(
            ca_key=ca_result["ca_key"],
            ca_cert=ca_result["ca_cert"],
            ca_name=ca_result["ca_name"],
            cert_name="complete-cert",
            cert_type="server",
            common_name="complete.example.com",
            organization="Test Org",
            country="US",
            state="CA",
            city="SF",
            validity_days=365,
            key_size=2048,
        )

        # Create incomplete cert (only key)
        incomplete_dir = cert_manager.certs_dir / ca_result["ca_name"] / "incomplete-cert"
        incomplete_dir.mkdir(parents=True, exist_ok=True)
        (incomplete_dir / "key.pem").write_text("fake key")

        # Should only list complete cert
        certs = cert_manager.list_certificates()
        assert len(certs) == 1
        assert certs[0]["name"] == "complete-cert"

    def test_list_certificates_with_non_directory_files(self, temp_dir, sample_ca_config):
        """Test listing certificates when directories contain non-directory files"""
        ca_manager = CAManager(base_dir=str(temp_dir))
        cert_manager = CertManager(base_dir=str(temp_dir))

        ca_result = ca_manager.create_root_ca(**sample_ca_config)

        # Ensure directory exists
        ca_certs_dir = cert_manager.certs_dir / ca_result["ca_name"]
        ca_certs_dir.mkdir(parents=True, exist_ok=True)

        # Create a file (not directory) in ca_certs_dir
        (ca_certs_dir / "not-a-dir.txt").write_text("test")

        # Create valid cert
        cert_manager.sign_certificate(
            ca_key=ca_result["ca_key"],
            ca_cert=ca_result["ca_cert"],
            ca_name=ca_result["ca_name"],
            cert_name="valid-cert",
            cert_type="server",
            common_name="valid.example.com",
            organization="Test Org",
            country="US",
            state="CA",
            city="SF",
            validity_days=365,
            key_size=2048,
        )

        # Should only list valid cert, ignore the file
        certs = cert_manager.list_certificates()
        assert len(certs) == 1
        assert certs[0]["name"] == "valid-cert"

    def test_get_certificate_info_invalid_cert(self, temp_dir):
        """Test getting info from invalid certificate file"""
        cert_manager = CertManager(base_dir=str(temp_dir))
        invalid_cert = temp_dir / "invalid.cert.pem"
        invalid_cert.write_text("not a valid certificate")

        result = cert_manager.get_certificate_info(str(invalid_cert))
        assert "Failed to read certificate" in result["info"]

    def test_delete_certificate_nonexistent(self, temp_dir):
        """Test deleting non-existent certificate"""
        cert_manager = CertManager(base_dir=str(temp_dir))
        result = cert_manager.delete_certificate("nonexistent-ca", "nonexistent-cert")
        assert result is False

    def test_sign_cert_cleanup_on_exception(self, temp_dir, sample_ca_config, monkeypatch):
        """Test that partial files are cleaned up when signing fails"""
        ca_manager = CAManager(base_dir=str(temp_dir))
        cert_manager = CertManager(base_dir=str(temp_dir))

        ca_result = ca_manager.create_root_ca(**sample_ca_config)

        # Mock subprocess to fail after key generation
        original_run = __import__("subprocess").run
        call_count = [0]

        def mock_run(cmd, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:  # First call (genrsa) succeeds
                return original_run(cmd, **kwargs)
            else:  # Second call (req) fails
                raise __import__("subprocess").CalledProcessError(1, cmd)

        monkeypatch.setattr("subprocess.run", mock_run)

        cert_output_dir = cert_manager.certs_dir / ca_result["ca_name"] / "test-cert"
        key_path = cert_output_dir / "key.pem"

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
                key_size=2048,
            )

        # Verify cleanup
        assert not key_path.exists()
