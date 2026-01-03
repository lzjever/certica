"""
Tests for CLI ui command
"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from certica.cli import cli


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing"""
    return CliRunner()


class TestCLIUI:
    """Test UI command"""

    def test_cli_ui_unsupported_language(self, cli_runner, temp_dir):
        """Test ui command with unsupported language (covers line 338-340)"""
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
                        "xx",  # Unsupported language
                    ],
                )
                
                # Should warn and fall back to English
                assert result.exit_code == 0 or "unsupported" in result.output.lower()

    def test_cli_ui_keyboard_interrupt(self, cli_runner, temp_dir):
        """Test ui command with KeyboardInterrupt (covers line 353-355)"""
        with patch("certica.cli.check_system_requirements", return_value=True):
            with patch("certica.ui.CAUITool") as mock_ui:
                mock_instance = MagicMock()
                mock_instance.run.side_effect = KeyboardInterrupt()
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
                
                # Should handle KeyboardInterrupt gracefully
                assert result.exit_code == 0

    def test_cli_ui_system_check_failed(self, cli_runner, temp_dir):
        """Test ui command when system check fails (covers line 343-346)"""
        with patch("certica.cli.check_system_requirements", return_value=False):
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
            
            # Should exit with error
            assert result.exit_code != 0

