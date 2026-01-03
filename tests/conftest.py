"""
Pytest configuration and fixtures for Certica tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_ca_config():
    """Sample CA configuration for testing"""
    return {
        "ca_name": "test-ca",
        "organization": "Test Organization",
        "country": "US",
        "state": "CA",
        "city": "San Francisco",
        "validity_days": 365,
        "key_size": 2048,
    }


@pytest.fixture
def sample_cert_config():
    """Sample certificate configuration for testing"""
    return {
        "cert_name": "test-cert",
        "cert_type": "server",
        "common_name": "test.example.com",
        "dns_names": ["test.example.com", "www.test.example.com"],
        "ip_addresses": ["127.0.0.1"],
        "organization": "Test Organization",
        "country": "US",
        "state": "CA",
        "city": "San Francisco",
        "validity_days": 365,
        "key_size": 2048,
    }
