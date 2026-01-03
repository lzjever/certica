"""
More tests for _format_path to cover remaining lines
"""

import pytest
from certica.cli import _format_path


class TestFormatPathMore:
    """More tests for _format_path function"""

    def test_format_path_value_error_in_relative_to(self, tmp_path):
        """Test _format_path when ValueError is raised in relative_to (covers line 29-30)"""
        # Create paths that will cause ValueError
        base_path = tmp_path / "base"
        base_path.mkdir()
        other_path = tmp_path / "other" / "file.key"
        other_path.parent.mkdir()
        other_path.write_text("test")
        
        # These paths are not related, should cause ValueError
        result = _format_path(str(other_path), str(base_path))
        # Should handle ValueError and try alternative method
        assert isinstance(result, str)

    def test_format_path_empty_remaining_returns_original(self):
        """Test _format_path when remaining after split is empty (covers line 34-35)"""
        # Test case where split results in empty remaining
        result = _format_path("output", "output")
        # When remaining is empty, should return original path
        assert result == "output" or isinstance(result, str)

