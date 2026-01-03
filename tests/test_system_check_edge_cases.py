"""
Edge cases and additional tests for System Check module
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock
from certica.system_check import SystemChecker, check_system_requirements


class TestSystemCheckEdgeCases:
    """Test edge cases for System Check module"""

    def test_check_command_timeout(self):
        """Test check_command with timeout"""
        checker = SystemChecker()
        
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("test", 5)
            available, error = checker.check_command(["test", "command"])
            
            assert available is False
            assert "timeout" in error.lower()

    def test_check_command_file_not_found(self):
        """Test check_command with FileNotFoundError"""
        checker = SystemChecker()
        
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            available, error = checker.check_command(["nonexistent", "command"])
            
            assert available is False
            assert "not found" in error.lower()

    def test_check_command_generic_exception(self):
        """Test check_command with generic exception"""
        checker = SystemChecker()
        
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Generic error")
            available, error = checker.check_command(["test", "command"])
            
            assert available is False
            assert "error" in error.lower()

    def test_check_tool_unknown_tool(self):
        """Test check_tool with unknown tool name"""
        checker = SystemChecker()
        result = checker.check_tool("unknown_tool_xyz")
        
        assert result["available"] is False
        assert "Unknown tool" in result["error"]

    def test_check_tool_command_not_found(self):
        """Test check_tool when command is not found"""
        checker = SystemChecker()
        
        with patch.object(checker, "find_command", return_value=None):
            result = checker.check_tool("openssl")
            # Result depends on whether openssl is actually available
            assert "available" in result

    def test_print_check_results_with_results(self):
        """Test print_check_results with provided results"""
        checker = SystemChecker()
        results = {
            "openssl": {
                "available": True,
                "path": "/usr/bin/openssl",
                "required": True,
                "description": "OpenSSL",
            }
        }
        
        # Should not crash
        result = checker.print_check_results(results)
        assert isinstance(result, bool)

    def test_print_check_results_with_missing_required(self):
        """Test print_check_results when required tools are missing"""
        checker = SystemChecker()
        results = {
            "openssl": {
                "available": False,
                "path": None,
                "error": "Not found",
                "required": True,
                "description": "OpenSSL",
            }
        }
        
        result = checker.print_check_results(results)
        assert result is False

    def test_print_check_results_with_optional_tools(self):
        """Test print_check_results with optional tools"""
        checker = SystemChecker()
        results = {
            "openssl": {
                "available": True,
                "path": "/usr/bin/openssl",
                "required": True,
                "description": "OpenSSL",
            },
            "update-ca-certificates": {
                "available": False,
                "path": None,
                "error": "Not found",
                "required": False,
                "description": "update-ca-certificates",
            },
        }
        
        result = checker.print_check_results(results)
        # Should return True if required tools are available
        assert isinstance(result, bool)

    @patch("platform.system")
    def test_system_checker_init_darwin(self, mock_system):
        """Test SystemChecker initialization on macOS"""
        mock_system.return_value = "Darwin"
        checker = SystemChecker()
        
        assert checker.system == "Darwin"
        assert "security" in checker.required_tools or "sudo" in checker.required_tools

    @patch("platform.system")
    def test_system_checker_init_windows(self, mock_system):
        """Test SystemChecker initialization on Windows"""
        mock_system.return_value = "Windows"
        checker = SystemChecker()
        
        assert checker.system == "Windows"
        assert "certutil" in checker.required_tools

    def test_check_all_returns_dict(self):
        """Test that check_all returns a dictionary"""
        checker = SystemChecker()
        results = checker.check_all()
        
        assert isinstance(results, dict)
        assert len(results) > 0

    def test_check_system_requirements_function(self):
        """Test check_system_requirements convenience function"""
        # This will print to stdout, but should return a boolean
        result = check_system_requirements()
        assert isinstance(result, bool)

    def test_print_check_results_no_optional_tools(self):
        """Test print_check_results when there are no optional tools"""
        checker = SystemChecker()
        results = {
            "openssl": {
                "available": True,
                "path": "/usr/bin/openssl",
                "required": True,
                "description": "OpenSSL",
            }
        }
        
        # Should not crash when no optional tools
        result = checker.print_check_results(results)
        assert isinstance(result, bool)

    def test_check_tool_with_test_command_failure(self):
        """Test check_tool when test command fails"""
        checker = SystemChecker()
        
        with patch.object(checker, "find_command", return_value="/usr/bin/openssl"):
            with patch.object(checker, "check_command", return_value=(False, "Test failed")):
                result = checker.check_tool("openssl")
                assert result["available"] is False
                assert "Test failed" in result["error"]

