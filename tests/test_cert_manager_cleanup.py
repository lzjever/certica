"""
Tests for Cert Manager cleanup code in exception handlers
"""

import pytest
import subprocess
from certica.cert_manager import CertManager
from certica.ca_manager import CAManager


class TestCertManagerCleanup:
    """Test cleanup code in Cert Manager exception handlers"""

    def test_sign_cert_cleanup_cert_path_exists(self, temp_dir, sample_ca_config, monkeypatch):
        """Test cleanup when cert_path exists during exception"""
        ca_manager = CAManager(base_dir=str(temp_dir))
        cert_manager = CertManager(base_dir=str(temp_dir))

        ca_result = ca_manager.create_root_ca(**sample_ca_config)

        cert_output_dir = cert_manager.certs_dir / ca_result["ca_name"] / "test-cert"
        cert_output_dir.mkdir(parents=True, exist_ok=True)

        key_path = cert_output_dir / "key.pem"
        cert_path = cert_output_dir / "cert.pem"
        csr_path = cert_output_dir / "csr.pem"

        # Create cert and csr files to test cleanup
        cert_path.write_text("fake cert")
        csr_path.write_text("fake csr")

        # Mock subprocess to fail after creating key
        original_run = subprocess.run
        call_count = [0]

        def mock_run(cmd, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:  # First call (genrsa) succeeds
                key_path.write_text("fake key")
                return original_run(cmd, **kwargs)
            else:  # Second call (req) fails
                raise subprocess.CalledProcessError(1, cmd)

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
                key_size=2048,
            )

        # Verify all files are cleaned up
        assert not key_path.exists()
        assert not cert_path.exists()
        assert not csr_path.exists()
