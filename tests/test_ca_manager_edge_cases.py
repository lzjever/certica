"""
Edge cases and boundary condition tests for CA Manager
"""

import pytest
from certica.ca_manager import CAManager


class TestCAManagerEdgeCases:
    """Test edge cases and boundary conditions for CA Manager"""

    def test_create_ca_with_partial_key_file(self, temp_dir):
        """Test creating CA when only key file exists (partial creation cleanup)"""
        manager = CAManager(base_dir=str(temp_dir))
        ca_subdir = manager.ca_dir / "test-ca"
        ca_subdir.mkdir(parents=True, exist_ok=True)

        # Create only key file (simulating interrupted creation)
        key_path = ca_subdir / "test-ca.key.pem"
        key_path.write_text("fake key content")

        # Should clean up and create successfully
        result = manager.create_root_ca(
            ca_name="test-ca",
            organization="Test Org",
            country="US",
            state="CA",
            city="SF",
            validity_days=365,
            key_size=2048,
        )

        assert result["ca_name"] == "test-ca"
        assert key_path.exists()
        assert (ca_subdir / "test-ca.cert.pem").exists()

    def test_create_ca_with_partial_cert_file(self, temp_dir):
        """Test creating CA when only cert file exists (partial creation cleanup)"""
        manager = CAManager(base_dir=str(temp_dir))
        ca_subdir = manager.ca_dir / "test-ca"
        ca_subdir.mkdir(parents=True, exist_ok=True)

        # Create only cert file (simulating interrupted creation)
        cert_path = ca_subdir / "test-ca.cert.pem"
        cert_path.write_text("fake cert content")

        # Should clean up and create successfully
        result = manager.create_root_ca(
            ca_name="test-ca",
            organization="Test Org",
            country="US",
            state="CA",
            city="SF",
            validity_days=365,
            key_size=2048,
        )

        assert result["ca_name"] == "test-ca"
        assert (ca_subdir / "test-ca.key.pem").exists()
        assert cert_path.exists()

    def test_list_cas_with_incomplete_ca(self, temp_dir):
        """Test listing CAs when some directories have incomplete files"""
        manager = CAManager(base_dir=str(temp_dir))

        # Create complete CA
        manager.create_root_ca(ca_name="complete-ca", organization="Test")

        # Create incomplete CA (only key)
        incomplete_dir = manager.ca_dir / "incomplete-ca"
        incomplete_dir.mkdir(parents=True, exist_ok=True)
        (incomplete_dir / "incomplete-ca.key.pem").write_text("fake")

        # Should only list complete CA
        cas = manager.list_cas()
        assert len(cas) == 1
        assert cas[0]["name"] == "complete-ca"

    def test_get_ca_not_found(self, temp_dir):
        """Test getting non-existent CA"""
        manager = CAManager(base_dir=str(temp_dir))
        result = manager.get_ca("nonexistent")
        assert result is None

    def test_get_ca_with_incomplete_files(self, temp_dir):
        """Test getting CA when files are incomplete"""
        manager = CAManager(base_dir=str(temp_dir))
        ca_subdir = manager.ca_dir / "incomplete-ca"
        ca_subdir.mkdir(parents=True, exist_ok=True)
        (ca_subdir / "incomplete-ca.key.pem").write_text("fake")

        result = manager.get_ca("incomplete-ca")
        assert result is None

    def test_get_certs_by_ca_nonexistent(self, temp_dir):
        """Test getting certificates for non-existent CA"""
        manager = CAManager(base_dir=str(temp_dir))
        certs = manager.get_certs_by_ca("nonexistent")
        assert certs == []

    def test_get_certs_by_ca_empty(self, temp_dir):
        """Test getting certificates for CA with no certificates"""
        manager = CAManager(base_dir=str(temp_dir))
        manager.create_root_ca(ca_name="empty-ca", organization="Test")
        certs = manager.get_certs_by_ca("empty-ca")
        assert certs == []

    def test_delete_ca_nonexistent(self, temp_dir):
        """Test deleting non-existent CA"""
        manager = CAManager(base_dir=str(temp_dir))
        result = manager.delete_ca("nonexistent")
        assert result is False

    def test_get_ca_info_invalid_cert(self, temp_dir):
        """Test getting info from invalid certificate file"""
        manager = CAManager(base_dir=str(temp_dir))
        invalid_cert = temp_dir / "invalid.cert.pem"
        invalid_cert.write_text("not a valid certificate")

        result = manager.get_ca_info(str(invalid_cert))
        assert "Failed to read certificate" in result["info"]

    def test_create_ca_cleanup_on_exception(self, temp_dir, monkeypatch):
        """Test that partial files are cleaned up when creation fails"""
        manager = CAManager(base_dir=str(temp_dir))
        ca_subdir = manager.ca_dir / "test-ca"

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

        with pytest.raises(Exception):
            manager.create_root_ca(
                ca_name="test-ca",
                organization="Test",
                country="US",
                state="CA",
                city="SF",
                validity_days=365,
                key_size=2048,
            )

        # Verify cleanup
        key_path = ca_subdir / "test-ca.key.pem"
        cert_path = ca_subdir / "test-ca.cert.pem"
        assert not key_path.exists()
        assert not cert_path.exists()

    def test_list_cas_with_non_directory_files(self, temp_dir):
        """Test listing CAs when ca_dir contains non-directory files"""
        manager = CAManager(base_dir=str(temp_dir))

        # Create a file (not directory) in ca_dir
        (manager.ca_dir / "not-a-dir.txt").write_text("test")

        # Create a valid CA
        manager.create_root_ca(ca_name="valid-ca", organization="Test")

        # Should only list valid CA, ignore the file
        cas = manager.list_cas()
        assert len(cas) == 1
        assert cas[0]["name"] == "valid-ca"

    def test_get_certs_by_ca_with_incomplete_certs(self, temp_dir):
        """Test getting certificates when some cert directories are incomplete"""
        manager = CAManager(base_dir=str(temp_dir))
        manager.create_root_ca(ca_name="test-ca", organization="Test")

        # Create incomplete cert directory (only key)
        cert_dir = manager.certs_dir / "test-ca" / "incomplete-cert"
        cert_dir.mkdir(parents=True, exist_ok=True)
        (cert_dir / "key.pem").write_text("fake key")

        # Should not list incomplete cert
        certs = manager.get_certs_by_ca("test-ca")
        assert len(certs) == 0
