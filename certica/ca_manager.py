"""
CA Manager - Core functionality for creating and managing CA certificates
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict


class CAManager:
    """Manages CA certificate creation and operations"""

    def __init__(self, base_dir: str = "output"):
        self.base_dir = Path(base_dir).resolve()
        self.ca_dir = self.base_dir / "ca"
        self.certs_dir = self.base_dir / "certs"
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Ensure all necessary directories exist"""
        self.ca_dir.mkdir(parents=True, exist_ok=True)
        self.certs_dir.mkdir(parents=True, exist_ok=True)

    def create_root_ca(
        self,
        ca_name: str = "myca",
        organization: str = "Development CA",
        country: str = "CN",
        state: str = "Beijing",
        city: str = "Beijing",
        validity_days: int = 3650,
        key_size: int = 2048,
    ) -> Dict[str, str]:
        """
        Create a root CA certificate

        Returns:
            Dict with paths to ca_key and ca_cert
        """
        # Store CA in its own directory: ca/{ca_name}/
        ca_subdir = self.ca_dir / ca_name
        ca_subdir.mkdir(parents=True, exist_ok=True)

        ca_key_path = ca_subdir / f"{ca_name}.key.pem"
        ca_cert_path = ca_subdir / f"{ca_name}.cert.pem"

        if ca_key_path.exists() or ca_cert_path.exists():
            raise FileExistsError(f"CA {ca_name} already exists")

        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cnf", delete=False) as f:
            config_path = f.name
            f.write(
                f"""[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[req_distinguished_name]
C = {country}
ST = {state}
L = {city}
O = {organization}
CN = {organization} Root CA

[v3_ca]
basicConstraints = critical,CA:TRUE
keyUsage = critical, keyCertSign, cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer:always
"""
            )

        try:
            # Generate private key
            subprocess.run(
                ["openssl", "genrsa", "-out", str(ca_key_path), str(key_size)],
                check=True,
                capture_output=True,
            )

            # Generate self-signed certificate
            subprocess.run(
                [
                    "openssl",
                    "req",
                    "-new",
                    "-x509",
                    "-key",
                    str(ca_key_path),
                    "-out",
                    str(ca_cert_path),
                    "-days",
                    str(validity_days),
                    "-config",
                    config_path,
                ],
                check=True,
                capture_output=True,
            )

            # Set permissions
            os.chmod(ca_key_path, 0o600)
            os.chmod(ca_cert_path, 0o644)

            return {
                "ca_name": ca_name,
                "ca_key": str(ca_key_path),
                "ca_cert": str(ca_cert_path),
                "key_size": key_size,
                "validity_days": validity_days,
            }
        except (KeyboardInterrupt, Exception):
            # Clean up partial files if creation was interrupted or failed
            if ca_key_path.exists():
                ca_key_path.unlink()
            if ca_cert_path.exists():
                ca_cert_path.unlink()
            # Remove empty directory if both files are gone
            if ca_subdir.exists() and not any(ca_subdir.iterdir()):
                ca_subdir.rmdir()
            raise
        finally:
            os.unlink(config_path)

    def list_cas(self) -> List[Dict[str, str]]:
        """List all available CA certificates"""
        cas = []
        # Look for CA directories: ca/{ca_name}/
        for ca_subdir in self.ca_dir.iterdir():
            if ca_subdir.is_dir():
                ca_name = ca_subdir.name
                key_file = ca_subdir / f"{ca_name}.key.pem"
                cert_file = ca_subdir / f"{ca_name}.cert.pem"
                if key_file.exists() and cert_file.exists():
                    cas.append({"name": ca_name, "key": str(key_file), "cert": str(cert_file)})
        return cas

    def get_ca(self, ca_name: str) -> Optional[Dict[str, str]]:
        """Get CA information by name"""
        ca_subdir = self.ca_dir / ca_name
        key_path = ca_subdir / f"{ca_name}.key.pem"
        cert_path = ca_subdir / f"{ca_name}.cert.pem"

        if key_path.exists() and cert_path.exists():
            return {"name": ca_name, "key": str(key_path), "cert": str(cert_path)}
        return None

    def get_certs_by_ca(self, ca_name: str) -> List[Dict[str, str]]:
        """Get all certificates signed by a specific CA"""
        # Certificates are now organized by CA: certs/{ca_name}/{cert_name}/
        certs = []
        ca_certs_dir = self.certs_dir / ca_name

        if not ca_certs_dir.exists():
            return certs

        # List all certificate directories under this CA
        for cert_dir in ca_certs_dir.iterdir():
            if cert_dir.is_dir():
                key_path = cert_dir / "key.pem"
                cert_path = cert_dir / "cert.pem"
                if key_path.exists() and cert_path.exists():
                    certs.append(
                        {"name": cert_dir.name, "key": str(key_path), "cert": str(cert_path)}
                    )

        return certs

    def delete_ca(self, ca_name: str) -> bool:
        """Delete a CA certificate and all its issued certificates"""
        ca_subdir = self.ca_dir / ca_name
        ca_certs_dir = self.certs_dir / ca_name

        if not ca_subdir.exists():
            return False

        try:
            # Delete CA directory (contains key and cert)
            import shutil

            if ca_subdir.exists():
                shutil.rmtree(ca_subdir)

            # Delete all certificates issued by this CA
            if ca_certs_dir.exists():
                shutil.rmtree(ca_certs_dir)

            return True
        except Exception:
            return False

    def get_ca_info(self, ca_cert_path: str) -> Dict[str, str]:
        """Get information about a CA certificate"""
        try:
            result = subprocess.run(
                ["openssl", "x509", "-in", ca_cert_path, "-text", "-noout"],
                capture_output=True,
                text=True,
                check=True,
            )
            return {"info": result.stdout}
        except subprocess.CalledProcessError:
            return {"info": "Failed to read certificate"}
