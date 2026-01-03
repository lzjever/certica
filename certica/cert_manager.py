"""
Certificate Manager - Handles certificate signing operations
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict


class CertManager:
    """Manages certificate signing operations"""

    def __init__(self, base_dir: str = "output"):
        self.base_dir = Path(base_dir).resolve()
        self.certs_dir = self.base_dir / "certs"
        self.certs_dir.mkdir(parents=True, exist_ok=True)

    def sign_certificate(
        self,
        ca_key: str,
        ca_cert: str,
        ca_name: str,
        cert_name: str,
        cert_type: str = "server",  # "server" or "client"
        common_name: str = "",
        dns_names: List[str] = None,
        ip_addresses: List[str] = None,
        organization: str = "",
        country: str = "CN",
        state: str = "Beijing",
        city: str = "Beijing",
        validity_days: int = 365,
        key_size: int = 2048,
    ) -> Dict[str, str]:
        """
        Sign a certificate using the specified CA

        Args:
            ca_key: Path to CA private key
            ca_cert: Path to CA certificate
            ca_name: Name of the CA (for directory organization)
            cert_name: Name for the certificate
            cert_type: "server" or "client"
            common_name: Common name for the certificate
            dns_names: List of DNS names
            ip_addresses: List of IP addresses
            organization: Organization name
            country: Country code
            state: State/Province
            city: City
            validity_days: Certificate validity in days
            key_size: Key size in bits

        Returns:
            Dict with paths to generated files
        """
        if dns_names is None:
            dns_names = []
        if ip_addresses is None:
            ip_addresses = []

        if not common_name:
            if dns_names:
                common_name = dns_names[0]
            elif ip_addresses:
                common_name = ip_addresses[0]
            else:
                common_name = cert_name

        # Create output directory organized by CA: certs/{ca_name}/{cert_name}/
        ca_certs_dir = self.certs_dir / ca_name
        cert_output_dir = ca_certs_dir / cert_name
        cert_output_dir.mkdir(parents=True, exist_ok=True)

        key_path = cert_output_dir / "key.pem"
        cert_path = cert_output_dir / "cert.pem"

        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cnf", delete=False) as f:
            config_path = f.name
            self._write_cert_config(
                f,
                cert_type,
                common_name,
                dns_names,
                ip_addresses,
                organization,
                country,
                state,
                city,
            )

        try:
            # Generate private key
            subprocess.run(
                ["openssl", "genrsa", "-out", str(key_path), str(key_size)],
                check=True,
                capture_output=True,
            )

            # Generate certificate signing request
            csr_path = cert_output_dir / "csr.pem"
            subprocess.run(
                [
                    "openssl",
                    "req",
                    "-new",
                    "-key",
                    str(key_path),
                    "-out",
                    str(csr_path),
                    "-config",
                    config_path,
                ],
                check=True,
                capture_output=True,
            )

            # Sign certificate
            subprocess.run(
                [
                    "openssl",
                    "x509",
                    "-req",
                    "-in",
                    str(csr_path),
                    "-CA",
                    ca_cert,
                    "-CAkey",
                    ca_key,
                    "-CAcreateserial",
                    "-out",
                    str(cert_path),
                    "-days",
                    str(validity_days),
                    "-extensions",
                    "v3_req",
                    "-extfile",
                    config_path,
                ],
                check=True,
                capture_output=True,
            )

            # Set permissions
            os.chmod(key_path, 0o600)
            os.chmod(cert_path, 0o644)

            # Clean up CSR
            csr_path.unlink()

            return {
                "cert_name": cert_name,
                "key": str(key_path),
                "cert": str(cert_path),
                "type": cert_type,
                "validity_days": validity_days,
            }
        except (KeyboardInterrupt, Exception):
            # Clean up partial files if creation was interrupted or failed
            if key_path.exists():
                key_path.unlink()
            if cert_path.exists():
                cert_path.unlink()
            if csr_path.exists():
                csr_path.unlink()
            # Remove empty directories if all files are gone
            if cert_output_dir.exists() and not any(cert_output_dir.iterdir()):
                cert_output_dir.rmdir()
            if ca_certs_dir.exists() and not any(ca_certs_dir.iterdir()):
                ca_certs_dir.rmdir()
            raise
        finally:
            os.unlink(config_path)

    def _write_cert_config(
        self,
        f,
        cert_type: str,
        common_name: str,
        dns_names: List[str],
        ip_addresses: List[str],
        organization: str,
        country: str,
        state: str,
        city: str,
    ):
        """Write OpenSSL configuration for certificate"""
        f.write(
            f"""[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name
prompt = no

[req_distinguished_name]
C = {country}
ST = {state}
L = {city}
O = {organization}
CN = {common_name}

[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
"""
        )

        if cert_type == "server":
            f.write("extendedKeyUsage = serverAuth, clientAuth\n")
        else:
            f.write("extendedKeyUsage = clientAuth\n")

        # Add Subject Alternative Names
        if dns_names or ip_addresses:
            f.write("subjectAltName = @alt_names\n\n")
            f.write("[alt_names]\n")

            dns_count = 1
            for dns in dns_names:
                f.write(f"DNS.{dns_count} = {dns}\n")
                dns_count += 1

            ip_count = 1
            for ip in ip_addresses:
                f.write(f"IP.{ip_count} = {ip}\n")
                ip_count += 1

    def list_certificates(self) -> List[Dict[str, str]]:
        """List all signed certificates"""
        certs = []
        # Certificates are organized by CA: certs/{ca_name}/{cert_name}/
        for ca_dir in self.certs_dir.iterdir():
            if ca_dir.is_dir():
                ca_name = ca_dir.name
                for cert_dir in ca_dir.iterdir():
                    if cert_dir.is_dir():
                        key_path = cert_dir / "key.pem"
                        cert_path = cert_dir / "cert.pem"
                        if key_path.exists() and cert_path.exists():
                            certs.append(
                                {
                                    "name": cert_dir.name,
                                    "ca_name": ca_name,
                                    "key": str(key_path),
                                    "cert": str(cert_path),
                                }
                            )
        return certs

    def get_certificate_info(self, cert_path: str) -> Dict[str, str]:
        """Get information about a certificate"""
        try:
            result = subprocess.run(
                ["openssl", "x509", "-in", cert_path, "-text", "-noout"],
                capture_output=True,
                text=True,
                check=True,
            )
            return {"info": result.stdout}
        except subprocess.CalledProcessError:
            return {"info": "Failed to read certificate"}

    def delete_certificate(self, ca_name: str, cert_name: str) -> bool:
        """Delete a certificate"""
        cert_dir = self.certs_dir / ca_name / cert_name
        if not cert_dir.exists():
            return False

        try:
            import shutil

            shutil.rmtree(cert_dir)
            return True
        except Exception:
            return False
