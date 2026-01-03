CA Manager
==========

The ``CAManager`` class handles creation and management of Certificate Authority (CA) certificates. 
This is the foundation of your certificate infrastructure.

Overview
--------

The CA Manager is responsible for:

- Creating root CA certificates
- Listing and retrieving CA information
- Managing relationships between CAs and their signed certificates
- Deleting CAs and their associated certificates

Initialization
--------------

.. code-block:: python

   from certica.ca_manager import CAManager
   
   # Initialize with default base directory
   ca_manager = CAManager()
   
   # Or specify a custom base directory
   ca_manager = CAManager(base_dir="/path/to/certificates")

**Parameters:**

- ``base_dir`` (str, optional): Base directory for storing CA certificates. Default: ``"output"``

.. note::

   The base directory structure is automatically created:
   - ``{base_dir}/ca/`` - CA certificates are stored here
   - ``{base_dir}/certs/`` - Signed certificates are stored here (managed by CertManager)

Methods
-------

create_root_ca
~~~~~~~~~~~~~~

Create a new root CA certificate.

.. code-block:: python

   result = ca_manager.create_root_ca(
       ca_name="myca",
       organization="My Company Inc.",
       country="US",
       state="California",
       city="San Francisco",
       validity_days=3650,
       key_size=2048
   )

**Parameters:**

- ``ca_name`` (str, optional): Name for the CA. Default: ``"myca"``
- ``organization`` (str, optional): Organization name. Default: ``"Development CA"``
- ``country`` (str, optional): Two-letter country code. Default: ``"CN"``
- ``state`` (str, optional): State or province. Default: ``"Beijing"``
- ``city`` (str, optional): City name. Default: ``"Beijing"``
- ``validity_days`` (int, optional): Validity period in days. Default: ``3650`` (10 years)
- ``key_size`` (int, optional): RSA key size in bits. Default: ``2048``

**Returns:**

Dictionary containing:
- ``ca_name``: Name of the created CA
- ``ca_key``: Path to the CA private key file
- ``ca_cert``: Path to the CA certificate file
- ``key_size``: Key size used
- ``validity_days``: Validity period

**Raises:**

- ``FileExistsError``: If a CA with the same name already exists
- ``Exception``: For other errors (OpenSSL failures, permission issues, etc.)

.. note::

   The CA private key is automatically set to permissions 600 (read/write for owner only) 
   for security. The certificate is set to 644 (readable by all).

.. warning::

   If a CA with the same name already exists, this method will raise ``FileExistsError``. 
   Use ``get_ca()`` to check if a CA exists before creating it.

**Example:**

.. code-block:: python

   try:
       result = ca_manager.create_root_ca(
           ca_name="production-ca",
           organization="My Company Inc.",
           country="US",
           validity_days=3650
       )
       print(f"CA created: {result['ca_cert']}")
   except FileExistsError:
       print("CA already exists!")
       ca_info = ca_manager.get_ca("production-ca")

list_cas
~~~~~~~~

List all available CA certificates.

.. code-block:: python

   cas = ca_manager.list_cas()

**Returns:**

List of dictionaries, each containing:
- ``name``: CA name
- ``key``: Path to CA private key
- ``cert``: Path to CA certificate

**Example:**

.. code-block:: python

   cas = ca_manager.list_cas()
   for ca in cas:
       print(f"CA: {ca['name']}")
       print(f"  Key: {ca['key']}")
       print(f"  Cert: {ca['cert']}")

.. note::

   Only complete CAs (with both key and certificate files) are returned. 
   Partial CAs from interrupted creation are automatically cleaned up.

get_ca
~~~~~~

Get information about a specific CA by name.

.. code-block:: python

   ca_info = ca_manager.get_ca("myca")

**Parameters:**

- ``ca_name`` (str): Name of the CA to retrieve

**Returns:**

Dictionary with CA information if found:
- ``name``: CA name
- ``key``: Path to CA private key
- ``cert``: Path to CA certificate

Returns ``None`` if the CA doesn't exist.

**Example:**

.. code-block:: python

   ca_info = ca_manager.get_ca("myca")
   if ca_info:
       print(f"Found CA: {ca_info['name']}")
   else:
       print("CA not found")

get_certs_by_ca
~~~~~~~~~~~~~~~~

Get all certificates signed by a specific CA.

.. code-block:: python

   certs = ca_manager.get_certs_by_ca("myca")

**Parameters:**

- ``ca_name`` (str): Name of the CA

**Returns:**

List of dictionaries, each containing:
- ``name``: Certificate name
- ``key``: Path to certificate private key
- ``cert``: Path to certificate file

**Example:**

.. code-block:: python

   certs = ca_manager.get_certs_by_ca("myca")
   print(f"Found {len(certs)} certificates signed by myca")
   for cert in certs:
       print(f"  - {cert['name']}")

.. note::

   Certificates are organized by CA in the directory structure: 
   ``{base_dir}/certs/{ca_name}/{cert_name}/``

delete_ca
~~~~~~~~~~

Delete a CA and all certificates signed by it.

.. code-block:: python

   success = ca_manager.delete_ca("myca")

**Parameters:**

- ``ca_name`` (str): Name of the CA to delete

**Returns:**

``True`` if deletion was successful, ``False`` otherwise.

.. warning::

   This operation **cannot be undone**. Deleting a CA will also delete:
   - The CA private key
   - The CA certificate
   - **All certificates signed by this CA**
   
   Make sure you have backups if needed!

**Example:**

.. code-block:: python

   if ca_manager.delete_ca("myca"):
       print("CA and all its certificates deleted")
   else:
       print("Failed to delete CA (may not exist)")

get_ca_info
~~~~~~~~~~~

Get detailed information about a CA certificate using OpenSSL.

.. code-block:: python

   info = ca_manager.get_ca_info("/path/to/ca.cert.pem")

**Parameters:**

- ``ca_cert_path`` (str): Path to the CA certificate file

**Returns:**

Dictionary containing:
- ``info``: Detailed certificate information (OpenSSL text output)

**Example:**

.. code-block:: python

   ca_info = ca_manager.get_ca("myca")
   if ca_info:
       details = ca_manager.get_ca_info(ca_info["cert"])
       print(details["info"])

.. note::

   This method uses OpenSSL's ``x509 -text -noout`` command to display certificate details, 
   including validity dates, subject, issuer, and extensions.

Complete Example
----------------

.. code-block:: python

   from certica.ca_manager import CAManager
   
   # Initialize
   ca_manager = CAManager(base_dir="output")
   
   # Check if CA exists
   ca_info = ca_manager.get_ca("myca")
   
   if not ca_info:
       # Create new CA
       print("Creating new CA...")
       result = ca_manager.create_root_ca(
           ca_name="myca",
           organization="My Company Inc.",
           country="US",
           validity_days=3650
       )
       ca_info = ca_manager.get_ca("myca")
   
   # List all CAs
   print("\nAll CAs:")
   for ca in ca_manager.list_cas():
       print(f"  - {ca['name']}")
   
   # Get certificates signed by this CA
   certs = ca_manager.get_certs_by_ca("myca")
   print(f"\nCertificates signed by myca: {len(certs)}")
   
   # Get CA details
   details = ca_manager.get_ca_info(ca_info["cert"])
   print("\nCA Details:")
   print(details["info"])


