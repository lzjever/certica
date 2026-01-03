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
    result = checker.check_command(["openssl", "version"])
    # Result depends on system, but should not crash
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_find_command():
    """Test finding a command"""
    checker = SystemChecker()

    # Find openssl
    path = checker.find_command("openssl")
    # May be None if not found, but should not crash
    assert path is None or isinstance(path, str)


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
    # This will print to stdout, but should not crash
    result = check_system_requirements()
    assert isinstance(result, bool)
