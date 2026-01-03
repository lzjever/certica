"""
Tests for CA Manager
"""

import pytest
from pathlib import Path
from certica.ca_manager import CAManager


def test_create_root_ca(temp_dir, sample_ca_config):
    """Test creating a root CA certificate"""
    manager = CAManager(base_dir=str(temp_dir))

    result = manager.create_root_ca(**sample_ca_config)

    assert "ca_key" in result
    assert "ca_cert" in result
    assert Path(result["ca_key"]).exists()
    assert Path(result["ca_cert"]).exists()

    # Check directory structure
    ca_dir = temp_dir / "ca" / sample_ca_config["ca_name"]
    assert ca_dir.exists()
    assert (ca_dir / f"{sample_ca_config['ca_name']}.key.pem").exists()
    assert (ca_dir / f"{sample_ca_config['ca_name']}.cert.pem").exists()


def test_create_root_ca_duplicate(temp_dir, sample_ca_config):
    """Test that creating duplicate CA raises FileExistsError"""
    manager = CAManager(base_dir=str(temp_dir))

    # Create first CA
    manager.create_root_ca(**sample_ca_config)

    # Try to create duplicate
    with pytest.raises(FileExistsError):
        manager.create_root_ca(**sample_ca_config)


def test_list_cas(temp_dir, sample_ca_config):
    """Test listing CA certificates"""
    manager = CAManager(base_dir=str(temp_dir))

    # Initially empty
    cas = manager.list_cas()
    assert len(cas) == 0

    # Create a CA
    manager.create_root_ca(**sample_ca_config)

    # List CAs
    cas = manager.list_cas()
    assert len(cas) == 1
    assert cas[0]["name"] == sample_ca_config["ca_name"]
    assert "key" in cas[0]
    assert "cert" in cas[0]


def test_get_ca(temp_dir, sample_ca_config):
    """Test getting a specific CA"""
    manager = CAManager(base_dir=str(temp_dir))

    # Create CA
    manager.create_root_ca(**sample_ca_config)

    # Get CA
    ca = manager.get_ca(sample_ca_config["ca_name"])
    assert ca is not None
    assert ca["name"] == sample_ca_config["ca_name"]
    assert Path(ca["key"]).exists()
    assert Path(ca["cert"]).exists()

    # Get non-existent CA
    assert manager.get_ca("nonexistent") is None


def test_get_ca_info(temp_dir, sample_ca_config):
    """Test getting CA certificate information"""
    manager = CAManager(base_dir=str(temp_dir))

    # Create CA
    manager.create_root_ca(**sample_ca_config)

    # Get CA info
    ca = manager.get_ca(sample_ca_config["ca_name"])
    info = manager.get_ca_info(ca["cert"])

    assert "info" in info
    assert len(info["info"]) > 0


def test_delete_ca(temp_dir, sample_ca_config):
    """Test deleting a CA"""
    manager = CAManager(base_dir=str(temp_dir))

    # Create CA
    manager.create_root_ca(**sample_ca_config)

    # Verify it exists
    ca = manager.get_ca(sample_ca_config["ca_name"])
    assert ca is not None

    # Delete CA
    result = manager.delete_ca(sample_ca_config["ca_name"])
    assert result is True

    # Verify it's gone
    assert manager.get_ca(sample_ca_config["ca_name"]) is None


def test_get_certs_by_ca(temp_dir, sample_ca_config):
    """Test getting certificates by CA"""
    manager = CAManager(base_dir=str(temp_dir))

    # Create CA
    manager.create_root_ca(**sample_ca_config)

    # Initially no certificates
    certs = manager.get_certs_by_ca(sample_ca_config["ca_name"])
    assert len(certs) == 0
