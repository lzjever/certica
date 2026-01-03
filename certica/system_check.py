"""
System tools and dependencies checker
Checks if required system tools and console commands are available
"""

import shutil
import subprocess
import sys
import platform
from typing import Dict, List, Tuple, Optional
from .i18n import t


class SystemChecker:
    """Checks availability of required system tools"""

    def __init__(self):
        self.system = platform.system()
        self.required_tools = {
            "openssl": {
                "commands": ["openssl"],
                "test_command": ["openssl", "version"],
                "required": True,
                "description": "OpenSSL - Required for certificate generation",
            }
        }

        # Platform-specific optional tools
        if self.system == "Linux":
            self.required_tools.update(
                {
                    "update-ca-certificates": {
                        "commands": ["update-ca-certificates"],
                        "test_command": ["update-ca-certificates", "--version"],
                        "required": False,
                        "description": "update-ca-certificates - For Debian/Ubuntu certificate management",
                    },
                    "update-ca-trust": {
                        "commands": ["update-ca-trust"],
                        "test_command": ["update-ca-trust", "extract", "--help"],
                        "required": False,
                        "description": "update-ca-trust - For Fedora/RHEL certificate management",
                    },
                    "trust": {
                        "commands": ["trust"],
                        "test_command": ["trust", "--version"],
                        "required": False,
                        "description": "trust - For Arch/Manjaro certificate management",
                    },
                    "sudo": {
                        "commands": ["sudo"],
                        "test_command": ["sudo", "--version"],
                        "required": False,
                        "description": "sudo - For system certificate installation (optional)",
                    },
                }
            )
        elif self.system == "Darwin":  # macOS
            self.required_tools.update(
                {
                    "security": {
                        "commands": ["security"],
                        "test_command": ["security", "--version"],
                        "required": False,
                        "description": "security - For macOS certificate management",
                    },
                    "sudo": {
                        "commands": ["sudo"],
                        "test_command": ["sudo", "--version"],
                        "required": False,
                        "description": "sudo - For system certificate installation (optional)",
                    },
                }
            )
        elif self.system == "Windows":
            self.required_tools.update(
                {
                    "certutil": {
                        "commands": ["certutil"],
                        "test_command": ["certutil", "-?"],
                        "required": False,
                        "description": "certutil - For Windows certificate management",
                    }
                }
            )

    def check_command(self, command: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Check if a command is available and executable

        Returns:
            (is_available, error_message)
        """
        try:
            subprocess.run(command, capture_output=True, text=True, timeout=5)
            # Command exists if we can run it (even if it returns non-zero)
            return True, None
        except FileNotFoundError:
            return False, f"Command not found: {command[0]}"
        except subprocess.TimeoutExpired:
            return False, f"Command timeout: {command[0]}"
        except Exception as e:
            return False, f"Error checking command: {str(e)}"

    def find_command(self, command_name: str) -> Optional[str]:
        """Find the full path to a command"""
        return shutil.which(command_name)

    def check_tool(self, tool_name: str) -> Dict:
        """
        Check if a tool is available

        Returns:
            Dict with 'available', 'path', 'error' keys
        """
        tool_info = self.required_tools.get(tool_name)
        if not tool_info:
            return {
                "available": False,
                "path": None,
                "error": f"Unknown tool: {tool_name}",
                "required": False,
            }

        # Check if any of the command variants exist
        for cmd_name in tool_info["commands"]:
            path = self.find_command(cmd_name)
            if path:
                # Test if command actually works
                is_available, error = self.check_command(tool_info["test_command"])
                return {
                    "available": is_available,
                    "path": path,
                    "error": error,
                    "required": tool_info["required"],
                    "description": tool_info["description"],
                }

        return {
            "available": False,
            "path": None,
            "error": f"Command not found: {', '.join(tool_info['commands'])}",
            "required": tool_info["required"],
            "description": tool_info["description"],
        }

    def check_all(self) -> Dict[str, Dict]:
        """Check all required tools"""
        results = {}
        for tool_name in self.required_tools:
            results[tool_name] = self.check_tool(tool_name)
        return results

    def print_check_results(self, results: Optional[Dict[str, Dict]] = None) -> bool:
        """
        Print check results and return True if all required tools are available

        Returns:
            True if all required tools are available, False otherwise
        """
        if results is None:
            results = self.check_all()

        all_required_available = True

        print("=" * 60)
        print(t("check.title"))
        print("=" * 60)
        print()

        # Check required tools first
        required_tools = {k: v for k, v in results.items() if v.get("required", False)}
        optional_tools = {k: v for k, v in results.items() if not v.get("required", False)}

        if required_tools:
            print(t("check.required_tools"))
            print("-" * 60)
            for tool_name, info in required_tools.items():
                if info["available"]:
                    print(
                        t(
                            "check.tool_available",
                            tool_name=tool_name,
                            description=info["description"],
                        )
                    )
                    print(t("check.tool_path", path=info["path"]))
                else:
                    print(
                        t(
                            "check.tool_unavailable",
                            tool_name=tool_name,
                            description=info["description"],
                        )
                    )
                    print(t("check.tool_error", error=info["error"]))
                    all_required_available = False
            print()

        if optional_tools:
            print(t("check.optional_tools"))
            print("-" * 60)
            for tool_name, info in optional_tools.items():
                if info["available"]:
                    print(
                        t(
                            "check.tool_available",
                            tool_name=tool_name,
                            description=info["description"],
                        )
                    )
                    print(t("check.tool_path", path=info["path"]))
                else:
                    print(
                        t(
                            "check.tool_warning",
                            tool_name=tool_name,
                            description=info["description"],
                        )
                    )
                    print(t("check.tool_warning_msg", error=info["error"]))
            print()

        if all_required_available:
            print(t("check.all_available"))
        else:
            print(t("check.some_missing"))
            print()
            print(t("check.install_hint"))
            if self.system == "Linux":
                print(f"\n{t('check.install_suggestions')}")
                print(t("check.install.openssl"))
                print(t("check.install.debian"))
                print(t("check.install.fedora"))
                print(t("check.install.arch"))

        print("=" * 60)
        print()

        return all_required_available


def check_system_requirements() -> bool:
    """
    Convenience function to check system requirements

    Returns:
        True if all required tools are available
    """
    checker = SystemChecker()
    results = checker.check_all()
    return checker.print_check_results(results)


if __name__ == "__main__":
    # Allow running as standalone script for testing
    success = check_system_requirements()
    sys.exit(0 if success else 1)
