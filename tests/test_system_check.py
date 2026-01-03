"""
Tests for System Check
"""

from certica.system_check import SystemChecker, check_system_requirements


def test_system_checker_init():
    """Test SystemChecker initialization"""
    checker = SystemChecker()
    assert checker.system is not None
    assert hasattr(checker, "required_tools")


def test_check_command():
    """Test checking a command"""
    checker = SystemChecker()

    # Check openssl (should be available)
    available, error = checker.check_command(["openssl", "version"])
    # Should return tuple with (bool, Optional[str])
    assert isinstance(available, bool)
    assert error is None or isinstance(error, str)


def test_find_command():
    """Test finding a command"""
    checker = SystemChecker()

    # Find openssl (should be available on most systems)
    path = checker.find_command("openssl")
    # Should return None or a string path
    assert path is None or isinstance(path, str)
    # If openssl is available, path should not be None
    # (This test may fail on systems without openssl, but that's acceptable)


def test_check_tool():
    """Test checking a tool"""
    checker = SystemChecker()

    result = checker.check_tool("openssl")
    assert isinstance(result, dict)
    assert "available" in result
    assert "path" in result
    assert "required" in result


def test_check_all():
    """Test checking all tools"""
    checker = SystemChecker()

    results = checker.check_all()
    assert isinstance(results, dict)
    assert "openssl" in results


def test_check_system_requirements():
    """Test check_system_requirements function"""
    # This will print to stdout, but should return a boolean
    result = check_system_requirements()
    # Should return True if all required tools are available, False otherwise
    assert result is True or result is False
