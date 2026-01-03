"""
Tests for CA Manager cleanup code in exception handlers
"""

import pytest
import subprocess
from unittest.mock import patch
from pathlib import Path
from certica.ca_manager import CAManager


class TestCAManagerCleanup:
    """Test cleanup code in CA Manager exception handlers"""

    def test_create_ca_cleanup_cert_path_exists(self, temp_dir, monkeypatch):
        """Test cleanup when cert_path exists during exception"""
        manager = CAManager(base_dir=str(temp_dir))
        ca_subdir = manager.ca_dir / "test-ca"
        ca_subdir.mkdir(parents=True, exist_ok=True)
        
        key_path = ca_subdir / "test-ca.key.pem"
        cert_path = ca_subdir / "test-ca.cert.pem"
        
        # Create cert file to test cleanup
        cert_path.write_text("fake cert")
        
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
            manager.create_root_ca(
                ca_name="test-ca",
                organization="Test",
                country="US",
                state="CA",
                city="SF",
                validity_days=365,
                key_size=2048
            )
        
        # Verify both files are cleaned up
        assert not key_path.exists()
        assert not cert_path.exists()

