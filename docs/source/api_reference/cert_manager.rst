Certificate Manager
===================

The ``CertManager`` class handles signing and management of certificates using existing CAs.

Overview
--------

The Certificate Manager is responsible for:

- Signing server and client certificates
- Listing all certificates
- Retrieving certificate information
- Deleting certificates

Initialization
--------------

.. code-block:: python

   from certica.cert_manager import CertManager
   
   # Initialize with default base directory
   cert_manager = CertManager()
   
   # Or specify a custom base directory
   cert_manager = CertManager(base_dir="/path/to/certificates")

**Parameters:**

- ``base_dir`` (str, optional): Base directory for storing certificates. Default: ``"output"``

.. note::

   Certificates are automatically organized by CA: ``{base_dir}/certs/{ca_name}/{cert_name}/``

Methods
-------

sign_certificate
~~~~~~~~~~~~~~~~

Sign a certificate using an existing CA.

.. code-block:: python

   result = cert_manager.sign_certificate(
       ca_key="/path/to/ca.key.pem",
       ca_cert="/path/to/ca.cert.pem",
       ca_name="myca",
       cert_name="web-server",
       cert_type="server",
       common_name="web-server.example.com",
       dns_names=["web-server.example.com", "www.example.com"],
       ip_addresses=["192.168.1.100"],
       organization="My Company Inc.",
       country="US",
       state="California",
       city="San Francisco",
       validity_days=365,
       key_size=2048
   )

**Parameters:**

- ``ca_key`` (str): Path to CA private key file (required)
- ``ca_cert`` (str): Path to CA certificate file (required)
- ``ca_name`` (str): Name of the CA (for directory organization) (required)
- ``cert_name`` (str): Name for the certificate (required)
- ``cert_type`` (str): Certificate type - ``"server"`` or ``"client"``. Default: ``"server"``
- ``common_name`` (str): Common Name (CN) for the certificate. Defaults to cert_name if empty
- ``dns_names`` (List[str], optional): List of DNS names for Subject Alternative Names
- ``ip_addresses`` (List[str], optional): List of IP addresses for Subject Alternative Names
- ``organization`` (str, optional): Organization name
- ``country`` (str, optional): Country code. Default: ``"CN"``
- ``state`` (str, optional): State/Province. Default: ``"Beijing"``
- ``city`` (str, optional): City. Default: ``"Beijing"``
- ``validity_days`` (int, optional): Validity period in days. Default: ``365``
- ``key_size`` (int, optional): RSA key size in bits. Default: ``2048``

**Returns:**

Dictionary containing:
- ``cert_name``: Name of the certificate
- ``key``: Path to the certificate private key file
- ``cert``: Path to the certificate file
- ``type``: Certificate type
- ``validity_days``: Validity period

**Raises:**

- ``Exception``: For various errors (OpenSSL failures, permission issues, etc.)

.. note::

   The ``common_name`` parameter is optional. If not provided, Certica will use:
   1. First DNS name (if available)
   2. First IP address (if available)
   3. Certificate name (as fallback)

.. warning::

   Always include all DNS names and IP addresses that will be used. Modern TLS 
   checks Subject Alternative Names (SANs), not just the Common Name.

**Example:**

.. code-block:: python

   from certica.ca_manager import CAManager
   from certica.cert_manager import CertManager
   
   ca_manager = CAManager()
   cert_manager = CertManager()
   
   # Get CA information
   ca_info = ca_manager.get_ca("myca")
   if not ca_info:
       print("CA not found!")
       exit(1)
   
   # Sign a server certificate
   result = cert_manager.sign_certificate(
       ca_key=ca_info["key"],
       ca_cert=ca_info["cert"],
       ca_name=ca_info["name"],
       cert_name="web-server",
       cert_type="server",
       dns_names=["example.com", "www.example.com"],
       ip_addresses=["127.0.0.1"],
       validity_days=365
   )
   
   print(f"Certificate created: {result['cert']}")

list_certificates
~~~~~~~~~~~~~~~~~

List all signed certificates.

.. code-block:: python

   certs = cert_manager.list_certificates()

**Returns:**

List of dictionaries, each containing:
- ``name``: Certificate name
- ``ca_name``: Name of the CA that signed it
- ``key``: Path to certificate private key
- ``cert``: Path to certificate file

**Example:**

.. code-block:: python

   certs = cert_manager.list_certificates()
   for cert in certs:
       print(f"{cert['name']} (signed by {cert['ca_name']})")

get_certificate_info
~~~~~~~~~~~~~~~~~~~~

Get detailed information about a certificate using OpenSSL.

.. code-block:: python

   info = cert_manager.get_certificate_info("/path/to/cert.pem")

**Parameters:**

- ``cert_path`` (str): Path to the certificate file

**Returns:**

Dictionary containing:
- ``info``: Detailed certificate information (OpenSSL text output)

**Example:**

.. code-block:: python

   cert_path = "output/certs/myca/web-server/cert.pem"
   info = cert_manager.get_certificate_info(cert_path)
   print(info["info"])

.. note::

   This method uses OpenSSL's ``x509 -text -noout`` command to display certificate details, 
   including validity dates, subject, issuer, SANs, and extensions.

delete_certificate
~~~~~~~~~~~~~~~~~~

Delete a specific certificate.

.. code-block:: python

   success = cert_manager.delete_certificate("myca", "web-server")

**Parameters:**

- ``ca_name`` (str): Name of the CA that signed the certificate
- ``cert_name`` (str): Name of the certificate to delete

**Returns:**

``True`` if deletion was successful, ``False`` otherwise.

**Example:**

.. code-block:: python

   if cert_manager.delete_certificate("myca", "web-server"):
       print("Certificate deleted")
   else:
       print("Certificate not found or deletion failed")

.. automodule:: certica.cert_manager
   :members:
   :undoc-members:
   :show-inheritance:

