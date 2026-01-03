"""
Test to cover line 134 in ca_manager.py (cert_path.unlink in exception handler)
"""

import pytest
import subprocess
from pathlib import Path
from certica.ca_manager import CAManager


def test_create_ca_exception_with_cert_file_exists(temp_dir, monkeypatch):
    """Test exception handling when cert file exists (covers line 134)"""
    manager = CAManager(base_dir=str(temp_dir))
    ca_subdir = manager.ca_dir / "test-ca"
    ca_subdir.mkdir(parents=True, exist_ok=True)
    
    key_path = ca_subdir / "test-ca.key.pem"
    cert_path = ca_subdir / "test-ca.cert.pem"
    
    # Pre-create cert file to ensure line 134 is executed
    cert_path.write_text("pre-existing cert")
    
    # Mock subprocess to fail after key generation
    original_run = subprocess.run
    call_count = [0]
    
    def mock_run(cmd, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:  # First call (genrsa) succeeds
            key_path.write_text("generated key")
            return original_run(cmd, **kwargs)
        else:  # Second call (req) fails
            raise subprocess.CalledProcessError(1, cmd)
    
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
    
    # Verify cert_path was cleaned up (line 134)
    assert not cert_path.exists()

