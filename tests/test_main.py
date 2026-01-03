"""
Tests for main entry point
"""

import sys
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path to import main
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_main_calls_cli():
    """Test that main calls cli"""
    # Import main from project root
    import main

    with patch("main.cli") as mock_cli:
        # Click may raise SystemExit, but we catch it
        mock_cli.side_effect = SystemExit(0)

        try:
            main.main()
        except SystemExit:
            pass  # Expected

        mock_cli.assert_called_once()
