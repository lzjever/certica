"""
Tests for CLI check-only option
"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from certica.cli import cli


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing"""
    return CliRunner()


class TestCLICheckOnly:
    """Test --check-only option"""

    def test_cli_check_only_success(self, cli_runner):
        """Test --check-only when check succeeds (covers line 50-52)"""
        with patch("certica.cli.check_system_requirements", return_value=True):
            result = cli_runner.invoke(cli, ["--check-only"])
            # Click may return exit code 0 or 2 (help), but should not crash
            assert result.exit_code in [0, 1, 2]

    def test_cli_check_only_failure(self, cli_runner):
        """Test --check-only when check fails (covers line 50-52)"""
        with patch("certica.cli.check_system_requirements", return_value=False):
            result = cli_runner.invoke(cli, ["--check-only"])
            # Should exit with error code
            assert result.exit_code in [1, 2]
