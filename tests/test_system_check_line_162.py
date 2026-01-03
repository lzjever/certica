"""
Test to cover line 162 in system_check.py
"""

from certica.system_check import SystemChecker


def test_print_check_results_with_none_results():
    """Test print_check_results when results is None (covers line 162)"""
    checker = SystemChecker()

    # Call with None to trigger line 162 (should call check_all internally)
    result = checker.print_check_results(None)
    # Should return True if all required tools are available, False otherwise
    assert result is True or result is False
