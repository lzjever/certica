"""
Tests for Certificate Manager
"""

from pathlib import Path
from certica.ca_manager import CAManager
from certica.cert_manager import CertManager


def test_sign_certificate(temp_dir, sample_ca_config, sample_cert_config):
    """Test signing a certificate"""
    # Create CA first
    ca_manager = CAManager(base_dir=str(temp_dir))
    ca_result = ca_manager.create_root_ca(**sample_ca_config)

    # Sign certificate - ensure all required fields are provided
    cert_manager = CertManager(base_dir=str(temp_dir))
    result = cert_manager.sign_certificate(
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

    assert "key" in result
    assert "cert" in result
    assert Path(result["key"]).exists()
    assert Path(result["cert"]).exists()

    # Check directory structure
    cert_dir = temp_dir / "certs" / sample_ca_config["ca_name"] / sample_cert_config["cert_name"]
    assert cert_dir.exists()
    assert (cert_dir / "key.pem").exists()
    assert (cert_dir / "cert.pem").exists()


def test_sign_server_certificate(temp_dir, sample_ca_config):
    """Test signing a server certificate"""
    ca_manager = CAManager(base_dir=str(temp_dir))
    ca_result = ca_manager.create_root_ca(**sample_ca_config)

    cert_manager = CertManager(base_dir=str(temp_dir))
    result = cert_manager.sign_certificate(
        ca_key=ca_result["ca_key"],
        ca_cert=ca_result["ca_cert"],
        ca_name=sample_ca_config["ca_name"],
        cert_name="server-cert",
        cert_type="server",
        common_name="server.example.com",
        dns_names=["server.example.com", "www.server.example.com"],
        ip_addresses=["127.0.0.1", "::1"],
        organization="Test Org",
        validity_days=365,
        key_size=2048,
    )

    assert Path(result["key"]).exists()
    assert Path(result["cert"]).exists()


def test_sign_client_certificate(temp_dir, sample_ca_config):
    """Test signing a client certificate"""
    ca_manager = CAManager(base_dir=str(temp_dir))
    ca_result = ca_manager.create_root_ca(**sample_ca_config)

    cert_manager = CertManager(base_dir=str(temp_dir))
    result = cert_manager.sign_certificate(
        ca_key=ca_result["ca_key"],
        ca_cert=ca_result["ca_cert"],
        ca_name=sample_ca_config["ca_name"],
        cert_name="client-cert",
        cert_type="client",
        common_name="client.example.com",
        organization="Test Org",
        validity_days=365,
        key_size=2048,
    )

    assert Path(result["key"]).exists()
    assert Path(result["cert"]).exists()


def test_list_certificates(temp_dir, sample_ca_config, sample_cert_config):
    """Test listing certificates"""
    # Create CA and certificate
    ca_manager = CAManager(base_dir=str(temp_dir))
    ca_result = ca_manager.create_root_ca(**sample_ca_config)

    cert_manager = CertManager(base_dir=str(temp_dir))
    cert_manager.sign_certificate(
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

    # List certificates
    certs = cert_manager.list_certificates()
    assert len(certs) >= 1
    assert any(c["name"] == sample_cert_config["cert_name"] for c in certs)


def test_get_certificate_info(temp_dir, sample_ca_config, sample_cert_config):
    """Test getting certificate information"""
    # Create CA and certificate
    ca_manager = CAManager(base_dir=str(temp_dir))
    ca_result = ca_manager.create_root_ca(**sample_ca_config)

    cert_manager = CertManager(base_dir=str(temp_dir))
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

    # Get certificate info
    info = cert_manager.get_certificate_info(cert_result["cert"])
    assert "info" in info
    assert len(info["info"]) > 0


def test_delete_certificate(temp_dir, sample_ca_config, sample_cert_config):
    """Test deleting a certificate"""
    # Create CA and certificate
    ca_manager = CAManager(base_dir=str(temp_dir))
    ca_result = ca_manager.create_root_ca(**sample_ca_config)

    cert_manager = CertManager(base_dir=str(temp_dir))
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

    # Verify it exists
    assert Path(cert_result["cert"]).exists()

    # Delete certificate
    result = cert_manager.delete_certificate(
        sample_ca_config["ca_name"], sample_cert_config["cert_name"]
    )
    assert result is True

    # Verify it's gone
    assert not Path(cert_result["cert"]).exists()
    assert not Path(cert_result["key"]).exists()
