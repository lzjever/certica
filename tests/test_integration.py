"""
Integration tests for Certica
"""

import pytest
from pathlib import Path
from certica.ca_manager import CAManager
from certica.cert_manager import CertManager
from certica.template_manager import TemplateManager


def test_full_workflow(temp_dir):
    """Test complete workflow: create CA, sign cert, list, delete"""
    # Create CA
    ca_manager = CAManager(base_dir=str(temp_dir))
    ca_result = ca_manager.create_root_ca(
        ca_name="testca", organization="Test Org", validity_days=365
    )

    assert Path(ca_result["ca_key"]).exists()
    assert Path(ca_result["ca_cert"]).exists()

    # List CAs
    cas = ca_manager.list_cas()
    assert len(cas) == 1
    assert cas[0]["name"] == "testca"

    # Sign certificate
    cert_manager = CertManager(base_dir=str(temp_dir))
    cert_result = cert_manager.sign_certificate(
        ca_key=ca_result["ca_key"],
        ca_cert=ca_result["ca_cert"],
        ca_name="testca",
        cert_name="testcert",
        cert_type="server",
        common_name="test.example.com",
        dns_names=["test.example.com"],
        ip_addresses=["127.0.0.1"],
        organization="Test Org",
        validity_days=365,
    )

    assert Path(cert_result["key"]).exists()
    assert Path(cert_result["cert"]).exists()

    # List certificates
    certs = cert_manager.list_certificates()
    assert len(certs) >= 1

    # Get certificate info
    info = cert_manager.get_certificate_info(cert_result["cert"])
    assert "info" in info

    # Delete certificate
    cert_manager.delete_certificate("testca", "testcert")
    assert not Path(cert_result["cert"]).exists()

    # Delete CA
    ca_manager.delete_ca("testca")
    assert ca_manager.get_ca("testca") is None


def test_template_workflow(temp_dir):
    """Test template workflow"""
    # Create template
    template_manager = TemplateManager(base_dir=str(temp_dir))
    template_path = template_manager.create_template(
        template_name="testtemplate",
        organization="Template Org",
        country="US",
        default_validity_days=730,
    )

    assert Path(template_path).exists()

    # Load template
    template = template_manager.load_template("testtemplate")
    assert template["organization"] == "Template Org"

    # Use template to create CA
    ca_manager = CAManager(base_dir=str(temp_dir))
    ca_result = ca_manager.create_root_ca(
        ca_name="templateca",
        organization=template["organization"],
        country=template["country"],
        validity_days=template["default_validity_days"],
    )

    assert Path(ca_result["ca_key"]).exists()

    # Delete template
    template_manager.delete_template("testtemplate")
    assert not Path(template_path).exists()


def test_multiple_cas(temp_dir):
    """Test managing multiple CAs"""
    ca_manager = CAManager(base_dir=str(temp_dir))

    # Create multiple CAs
    ca1 = ca_manager.create_root_ca(ca_name="ca1", organization="Org1")
    ca2 = ca_manager.create_root_ca(ca_name="ca2", organization="Org2")

    # List all CAs
    cas = ca_manager.list_cas()
    assert len(cas) == 2

    # Sign certificates with different CAs
    cert_manager = CertManager(base_dir=str(temp_dir))

    cert1 = cert_manager.sign_certificate(
        ca_key=ca1["ca_key"],
        ca_cert=ca1["ca_cert"],
        ca_name="ca1",
        cert_name="cert1",
        cert_type="server",
        common_name="cert1.example.com",
        organization="Org1",
        country="US",
        state="CA",
        city="San Francisco",
    )

    cert2 = cert_manager.sign_certificate(
        ca_key=ca2["ca_key"],
        ca_cert=ca2["ca_cert"],
        ca_name="ca2",
        cert_name="cert2",
        cert_type="server",
        common_name="cert2.example.com",
        organization="Org2",
        country="US",
        state="CA",
        city="San Francisco",
    )

    # Verify certificates are in correct directories
    assert (temp_dir / "certs" / "ca1" / "cert1").exists()
    assert (temp_dir / "certs" / "ca2" / "cert2").exists()

    # List certificates by CA
    certs_ca1 = ca_manager.get_certs_by_ca("ca1")
    assert len(certs_ca1) == 1
    assert certs_ca1[0]["name"] == "cert1"

    certs_ca2 = ca_manager.get_certs_by_ca("ca2")
    assert len(certs_ca2) == 1
    assert certs_ca2[0]["name"] == "cert2"
