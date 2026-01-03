"""
System Certificate Manager - Handles installation/removal of certificates from system
"""

import subprocess
import platform
import os
import getpass
from pathlib import Path
from typing import Optional, List, Tuple
from .i18n import t


class SystemCertManager:
    """Manages system certificate installation and removal"""

    def __init__(self):
        self.system = platform.system()
        self.distro_info = self._detect_linux_distro() if self.system == "Linux" else None
        self.sudo_password: Optional[str] = None

    def _detect_linux_distro(self) -> Optional[dict]:
        """Detect Linux distribution from /etc/os-release"""
        distro_info = {}

        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line:
                        key, value = line.split("=", 1)
                        # Remove quotes
                        value = value.strip('"').strip("'")
                        distro_info[key] = value

        return distro_info if distro_info else None

    def _get_linux_distro_id(self) -> Optional[str]:
        """Get Linux distribution ID"""
        if not self.distro_info:
            return None

        # Check ID first (e.g., ubuntu, debian, fedora, arch)
        distro_id = self.distro_info.get("ID", "").lower()

        # Check ID_LIKE for similar distributions
        id_like = self.distro_info.get("ID_LIKE", "").lower()

        # Map to known distributions
        if distro_id in ["ubuntu", "debian"] or "debian" in id_like:
            return "debian"
        elif (
            distro_id in ["fedora", "rhel", "centos", "rocky", "almalinux"]
            or "fedora" in id_like
            or "rhel" in id_like
        ):
            return "fedora"
        elif distro_id in ["arch", "manjaro"] or "arch" in id_like:
            return "arch"
        elif distro_id in ["opensuse", "sles", "suse"] or "suse" in id_like:
            return "suse"

        return distro_id if distro_id else None

    def _get_sudo_password(self, prompt: str = None) -> Optional[str]:
        """Get sudo password from user"""
        if self.sudo_password:
            return self.sudo_password

        if prompt is None:
            prompt = t("cli.install.password_prompt") + ": "

        try:
            password = getpass.getpass(prompt)
            return password if password else None
        except (KeyboardInterrupt, EOFError):
            return None

    def _run_sudo_command(
        self, command: List[str], password: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Run a sudo command with password support

        Returns:
            (success, error_message)
        """
        if password:
            # Use sudo -S to read password from stdin
            try:
                process = subprocess.Popen(
                    ["sudo", "-S"] + command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                stdout, stderr = process.communicate(input=password + "\n")

                if process.returncode == 0:
                    return True, ""
                else:
                    error_msg = (
                        stderr.strip()
                        if stderr
                        else f"Command failed with return code {process.returncode}"
                    )
                    return False, error_msg
            except Exception as e:
                return False, str(e)
        else:
            # Try without password (might work if user has passwordless sudo)
            try:
                result = subprocess.run(
                    ["sudo"] + command, check=True, capture_output=True, text=True
                )
                return True, ""
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip() if e.stderr else str(e)
                return False, error_msg
            except Exception as e:
                return False, str(e)

    def _get_certificate_fingerprint(self, cert_path: str) -> Optional[str]:
        """Get SHA256 fingerprint of a certificate"""
        try:
            result = subprocess.run(
                ["openssl", "x509", "-in", cert_path, "-fingerprint", "-noout", "-sha256"],
                capture_output=True,
                text=True,
                check=True,
            )
            # Extract fingerprint from output like "SHA256 Fingerprint=AA:BB:CC:..."
            fingerprint_line = result.stdout.strip()
            if "=" in fingerprint_line:
                return fingerprint_line.split("=", 1)[1].replace(":", "").upper()
            return None
        except Exception:
            return None

    def _verify_installation(
        self, source_cert_path: str, installed_cert_path: str, ca_name: str
    ) -> bool:
        """
        Verify that certificate was installed correctly

        Args:
            source_cert_path: Original certificate path
            installed_cert_path: Installed certificate path
            ca_name: CA name

        Returns:
            True if verification passes, False otherwise
        """
        print(t("system.verify.installing"))

        # 1. Check if installed file exists
        if not Path(installed_cert_path).exists():
            print(t("system.verify.file_not_exists", path=installed_cert_path))
            return False

        # 2. Compare fingerprints
        source_fp = self._get_certificate_fingerprint(source_cert_path)
        installed_fp = self._get_certificate_fingerprint(installed_cert_path)

        if not source_fp or not installed_fp:
            print(t("system.verify.fingerprint_skip"))
            # Continue with other checks
        elif source_fp != installed_fp:
            print(t("system.verify.fingerprint_mismatch"))
            print(t("system.verify.fingerprint_source", fp=source_fp[:16]))
            print(t("system.verify.fingerprint_installed", fp=installed_fp[:16]))
            return False
        else:
            print(t("system.verify.fingerprint_match", fp=source_fp[:16]))

        # 3. Try to verify certificate is readable
        try:
            result = subprocess.run(
                ["openssl", "x509", "-in", installed_cert_path, "-noout", "-subject"],
                capture_output=True,
                text=True,
                check=True,
            )
            print(t("system.verify.cert_readable", subject=result.stdout.strip()))
        except Exception as e:
            print(t("system.verify.cert_readable_error", error=str(e)))
            # Don't fail verification for this

        return True

    def _verify_removal(self, ca_name: str) -> bool:
        """
        Verify that certificate was removed correctly

        Args:
            ca_name: CA name

        Returns:
            True if verification passes, False otherwise
        """
        print(t("system.verify.removing"))

        distro_id = self._get_linux_distro_id()

        # Check all possible certificate locations
        check_paths = []

        if distro_id == "debian":
            check_paths.append(Path(f"/usr/local/share/ca-certificates/{ca_name}.crt"))
        elif distro_id == "fedora":
            check_paths.append(Path(f"/etc/pki/ca-trust/source/anchors/{ca_name}.crt"))
        elif distro_id == "arch":
            check_paths.extend(
                [
                    Path(f"/etc/ca-certificates/trust-source/anchors/{ca_name}.crt"),
                    Path(f"/usr/local/share/ca-certificates/{ca_name}.crt"),
                ]
            )
        elif distro_id == "suse":
            check_paths.append(Path(f"/etc/pki/trust/anchors/{ca_name}.crt"))
        else:
            # Check all common paths
            check_paths.extend(
                [
                    Path(f"/usr/local/share/ca-certificates/{ca_name}.crt"),
                    Path(f"/etc/pki/ca-trust/source/anchors/{ca_name}.crt"),
                    Path(f"/etc/ca-certificates/trust-source/anchors/{ca_name}.crt"),
                    Path(f"/etc/pki/trust/anchors/{ca_name}.crt"),
                ]
            )

        # Check if any certificate file still exists
        found_paths = [p for p in check_paths if p.exists()]

        if found_paths:
            print(t("system.verify.removal_failed"))
            for p in found_paths:
                print(f"    - {p}")
            return False

        print(t("system.verify.removal_success"))
        return True

    def install_ca_cert(
        self, ca_cert_path: str, ca_name: str, password: Optional[str] = None
    ) -> bool:
        """
        Install CA certificate to system trust store

        Args:
            ca_cert_path: Path to CA certificate file
            ca_name: Name of the CA
            password: Optional sudo password (if None, will prompt user)

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.system == "Linux":
                return self._install_linux(ca_cert_path, ca_name, password)
            elif self.system == "Darwin":  # macOS
                return self._install_macos(ca_cert_path, ca_name, password)
            elif self.system == "Windows":
                return self._install_windows(ca_cert_path, ca_name)
            else:
                print(t("system.unsupported", system=self.system))
                return False
        except Exception as e:
            print(t("system.error.install", error=str(e)))
            return False

    def remove_ca_cert(self, ca_name: str, password: Optional[str] = None) -> bool:
        """
        Remove CA certificate from system trust store

        Args:
            ca_name: Name of the CA
            password: Optional sudo password (if None, will prompt user)

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.system == "Linux":
                return self._remove_linux(ca_name, password)
            elif self.system == "Darwin":  # macOS
                return self._remove_macos(ca_name, password)
            elif self.system == "Windows":
                return self._remove_windows(ca_name)
            else:
                print(t("system.unsupported", system=self.system))
                return False
        except Exception as e:
            print(t("system.error.remove", error=str(e)))
            return False

    def _install_linux(
        self, ca_cert_path: str, ca_name: str, password: Optional[str] = None
    ) -> bool:
        """Install certificate on Linux - supports multiple distributions"""
        distro_id = self._get_linux_distro_id()

        # Try to get password if not provided
        if password is None:
            password = self._get_sudo_password()
            if password is None:
                print(t("system.install.linux.password_required"))
                return False

        # Define installation methods for different distributions
        install_methods = []

        if distro_id == "debian":
            # Debian/Ubuntu
            install_methods.append(
                {
                    "cert_dir": Path("/usr/local/share/ca-certificates"),
                    "update_cmd": ["update-ca-certificates"],
                    "name": "Debian/Ubuntu",
                }
            )
        elif distro_id == "fedora":
            # Fedora/RHEL/CentOS
            install_methods.append(
                {
                    "cert_dir": Path("/etc/pki/ca-trust/source/anchors"),
                    "update_cmd": ["update-ca-trust", "extract"],
                    "name": "Fedora/RHEL/CentOS",
                }
            )
        elif distro_id == "arch":
            # Arch/Manjaro - try both methods
            install_methods.append(
                {
                    "cert_dir": Path("/etc/ca-certificates/trust-source/anchors"),
                    "update_cmd": ["trust", "extract-compat"],
                    "name": "Arch/Manjaro (trust)",
                }
            )
            install_methods.append(
                {
                    "cert_dir": Path("/usr/local/share/ca-certificates"),
                    "update_cmd": ["update-ca-certificates"],
                    "name": "Arch/Manjaro (ca-certificates)",
                }
            )
        elif distro_id == "suse":
            # openSUSE/SLES
            install_methods.append(
                {
                    "cert_dir": Path("/etc/pki/trust/anchors"),
                    "update_cmd": ["update-ca-certificates"],
                    "name": "openSUSE/SLES",
                }
            )
        else:
            # Unknown distribution - try common methods
            install_methods.extend(
                [
                    {
                        "cert_dir": Path("/usr/local/share/ca-certificates"),
                        "update_cmd": ["update-ca-certificates"],
                        "name": "Debian/Ubuntu (fallback)",
                    },
                    {
                        "cert_dir": Path("/etc/pki/ca-trust/source/anchors"),
                        "update_cmd": ["update-ca-trust", "extract"],
                        "name": "Fedora/RHEL (fallback)",
                    },
                    {
                        "cert_dir": Path("/etc/ca-certificates/trust-source/anchors"),
                        "update_cmd": ["trust", "extract-compat"],
                        "name": "Arch (fallback)",
                    },
                    {
                        "cert_dir": Path("/etc/pki/trust/anchors"),
                        "update_cmd": ["update-ca-certificates"],
                        "name": "openSUSE (fallback)",
                    },
                ]
            )

        # Try each installation method
        for method in install_methods:
            cert_dir = method["cert_dir"]
            update_cmd = method["update_cmd"]
            method_name = method["name"]

            # Check if parent directory exists
            if not cert_dir.parent.exists():
                continue

            target_path = cert_dir / f"{ca_name}.crt"

            try:
                # Create directory if it doesn't exist
                if not cert_dir.exists():
                    success, error = self._run_sudo_command(
                        ["mkdir", "-p", str(cert_dir)], password
                    )
                    if not success:
                        continue

                    # Set proper permissions
                    self._run_sudo_command(["chmod", "755", str(cert_dir)], password)

                # Copy certificate
                success, error = self._run_sudo_command(
                    ["cp", ca_cert_path, str(target_path)], password
                )
                if not success:
                    print(t("system.install.linux.copy_failed", method=method_name, error=error))
                    continue

                # Set proper permissions
                self._run_sudo_command(["chmod", "644", str(target_path)], password)

                # Update CA certificates
                success, error = self._run_sudo_command(update_cmd, password)
                if not success:
                    print(t("system.install.linux.update_failed", method=method_name, error=error))
                    # Remove the copied file
                    self._run_sudo_command(["rm", str(target_path)], password)
                    continue

                # Verify installation
                if self._verify_installation(ca_cert_path, target_path, ca_name):
                    print(t("system.install.linux.success", method=method_name))
                    return True
                else:
                    print(t("system.install.linux.warning", method=method_name))
                    # Don't return False here, as the file is installed, just verification failed
                    return True

            except Exception as e:
                print(t("system.install.linux.error", method=method_name, error=str(e)))
                continue

        print(t("system.install.linux.no_method"))
        return False

    def _remove_linux(self, ca_name: str, password: Optional[str] = None) -> bool:
        """Remove certificate from Linux - supports multiple distributions"""
        distro_id = self._get_linux_distro_id()

        # Try to get password if not provided
        if password is None:
            password = self._get_sudo_password()
            if password is None:
                print(t("system.install.linux.password_required"))
                return False

        # Define removal methods for different distributions
        remove_methods = []

        if distro_id == "debian":
            remove_methods.append(
                {
                    "cert_path": Path(f"/usr/local/share/ca-certificates/{ca_name}.crt"),
                    "update_cmd": ["update-ca-certificates"],
                    "name": "Debian/Ubuntu",
                }
            )
        elif distro_id == "fedora":
            remove_methods.append(
                {
                    "cert_path": Path(f"/etc/pki/ca-trust/source/anchors/{ca_name}.crt"),
                    "update_cmd": ["update-ca-trust", "extract"],
                    "name": "Fedora/RHEL/CentOS",
                }
            )
        elif distro_id == "arch":
            remove_methods.append(
                {
                    "cert_path": Path(f"/etc/ca-certificates/trust-source/anchors/{ca_name}.crt"),
                    "update_cmd": ["trust", "extract-compat"],
                    "name": "Arch/Manjaro (trust)",
                }
            )
            remove_methods.append(
                {
                    "cert_path": Path(f"/usr/local/share/ca-certificates/{ca_name}.crt"),
                    "update_cmd": ["update-ca-certificates"],
                    "name": "Arch/Manjaro (ca-certificates)",
                }
            )
        elif distro_id == "suse":
            remove_methods.append(
                {
                    "cert_path": Path(f"/etc/pki/trust/anchors/{ca_name}.crt"),
                    "update_cmd": ["update-ca-certificates"],
                    "name": "openSUSE/SLES",
                }
            )
        else:
            # Unknown distribution - try all common paths
            remove_methods.extend(
                [
                    {
                        "cert_path": Path(f"/usr/local/share/ca-certificates/{ca_name}.crt"),
                        "update_cmd": ["update-ca-certificates"],
                        "name": "Debian/Ubuntu (fallback)",
                    },
                    {
                        "cert_path": Path(f"/etc/pki/ca-trust/source/anchors/{ca_name}.crt"),
                        "update_cmd": ["update-ca-trust", "extract"],
                        "name": "Fedora/RHEL (fallback)",
                    },
                    {
                        "cert_path": Path(
                            f"/etc/ca-certificates/trust-source/anchors/{ca_name}.crt"
                        ),
                        "update_cmd": ["trust", "extract-compat"],
                        "name": "Arch (fallback)",
                    },
                    {
                        "cert_path": Path(f"/etc/pki/trust/anchors/{ca_name}.crt"),
                        "update_cmd": ["update-ca-certificates"],
                        "name": "openSUSE (fallback)",
                    },
                ]
            )

        # Try each removal method
        for method in remove_methods:
            cert_path = method["cert_path"]
            update_cmd = method["update_cmd"]
            method_name = method["name"]

            if not cert_path.exists():
                continue

            try:
                # Remove certificate
                success, error = self._run_sudo_command(["rm", str(cert_path)], password)
                if not success:
                    continue

                # Update CA certificates
                success, error = self._run_sudo_command(update_cmd, password)
                if not success:
                    print(t("system.remove.linux.update_failed", method=method_name, error=error))
                    continue

                print(t("system.remove.linux.success", method=method_name))
                return True

            except Exception as e:
                continue

        print(t("system.remove.linux.no_method"))
        return False

    def _install_macos(
        self, ca_cert_path: str, ca_name: str, password: Optional[str] = None
    ) -> bool:
        """Install certificate on macOS"""
        if password is None:
            password = self._get_sudo_password()
            if password is None:
                print(t("system.install.macos.password_required"))
                return False

        try:
            success, error = self._run_sudo_command(
                [
                    "security",
                    "add-trusted-cert",
                    "-d",
                    "-r",
                    "trustRoot",
                    "-k",
                    "/Library/Keychains/System.keychain",
                    ca_cert_path,
                ],
                password,
            )

            if success:
                return True
            else:
                print(t("system.install.macos.error", error=error))
                return False
        except Exception as e:
            print(t("system.install.macos.error", error=str(e)))
            return False

    def _remove_macos(self, ca_name: str, password: Optional[str] = None) -> bool:
        """Remove certificate from macOS"""
        if password is None:
            password = self._get_sudo_password()
            if password is None:
                print(t("system.remove.macos.password_required"))
                return False

        try:
            # First check if certificate exists
            result = subprocess.run(
                [
                    "security",
                    "find-certificate",
                    "-c",
                    ca_name,
                    "-a",
                    "/Library/Keychains/System.keychain",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                success, error = self._run_sudo_command(
                    [
                        "security",
                        "delete-certificate",
                        "-c",
                        ca_name,
                        "/Library/Keychains/System.keychain",
                    ],
                    password,
                )

                if success:
                    return True
                else:
                    print(t("system.remove.macos.error", error=error))
                    return False
            return False
        except Exception as e:
            print(t("system.remove.macos.error", error=str(e)))
            return False

    def _install_windows(self, ca_cert_path: str, ca_name: str) -> bool:
        """Install certificate on Windows"""
        try:
            # Use certutil to add certificate to LocalMachine\Root store
            subprocess.run(
                ["certutil", "-addstore", "-f", "Root", ca_cert_path],
                check=True,
                capture_output=True,
                shell=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            print(t("system.install.windows.error", error=error_msg))
            return False

    def _remove_windows(self, ca_name: str) -> bool:
        """Remove certificate from Windows"""
        try:
            # Use certutil to remove certificate
            subprocess.run(
                ["certutil", "-delstore", "Root", ca_name],
                check=True,
                capture_output=True,
                shell=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False
