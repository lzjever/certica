"""
More tests for CLI ui command to cover remaining lines
"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from certica.cli import cli


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing"""
    return CliRunner()


class TestCLIUIMore:
    """More tests for UI command"""

    def test_cli_ui_successful_launch(self, cli_runner, temp_dir):
        """Test ui command successful launch (covers line 349-352)"""
        with patch("certica.cli.check_system_requirements", return_value=True):
            with patch("certica.ui.CAUITool") as mock_ui:
                mock_instance = MagicMock()
                mock_instance.run = MagicMock()
                mock_ui.return_value = mock_instance
                
                result = cli_runner.invoke(
                    cli,
                    [
                        "--base-dir",
                        str(temp_dir),
                        "--skip-check",
                        "ui",
                        "--lang",
                        "en",
                    ],
                )
                
                # Should launch UI
                assert result.exit_code == 0
                mock_instance.run.assert_called_once()

