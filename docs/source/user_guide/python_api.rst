Python API Guide
================

This guide shows you how to use Certica programmatically through its Python API. 
This is perfect for automation, integration with other tools, or building custom workflows.

Why Use the Python API?
------------------------

While the CLI is great for manual operations, the Python API allows you to:

- **Automate certificate generation** in deployment scripts
- **Integrate with configuration management** tools (Ansible, Puppet, etc.)
- **Build custom workflows** that combine certificate management with other operations
- **Create web interfaces** or APIs that manage certificates
- **Implement certificate rotation** and renewal automation

Getting Started
---------------

Import the necessary modules:

.. code-block:: python

   from certica.ca_manager import CAManager
   from certica.cert_manager import CertManager
   from certica.template_manager import TemplateManager
   from certica.system_cert import SystemCertManager

Initialize the managers:

.. code-block:: python

   # All managers use the same base directory
   base_dir = "output"  # or any custom path
   
   ca_manager = CAManager(base_dir)
   cert_manager = CertManager(base_dir)
   template_manager = TemplateManager(base_dir)
   system_cert_manager = SystemCertManager()

.. note::

   All managers share the same base directory structure. Certificates are automatically 
   organized by CA, making it easy to manage relationships between CAs and their certificates.

Working with CAs
----------------

Creating a CA
~~~~~~~~~~~~~

Create a root CA certificate:

.. code-block:: python

   try:
       result = ca_manager.create_root_ca(
           ca_name="myca",
           organization="My Company Inc.",
           country="US",
           state="California",
           city="San Francisco",
           validity_days=3650,  # 10 years
           key_size=2048
       )
       
       print(f"CA created successfully!")
       print(f"Key: {result['ca_key']}")
       print(f"Cert: {result['ca_cert']}")
   except FileExistsError:
       print("CA already exists!")
   except Exception as e:
       print(f"Error creating CA: {e}")

**Return Value:**

The method returns a dictionary with:
- ``ca_name``: Name of the CA
- ``ca_key``: Path to the private key file
- ``ca_cert``: Path to the certificate file
- ``key_size``: Key size used
- ``validity_days``: Validity period

Listing CAs
~~~~~~~~~~~

Get a list of all available CAs:

.. code-block:: python

   cas = ca_manager.list_cas()
   
   for ca in cas:
       print(f"CA: {ca['name']}")
       print(f"  Key: {ca['key']}")
       print(f"  Cert: {ca['cert']}")

**Return Value:**

Returns a list of dictionaries, each containing:
- ``name``: CA name
- ``key``: Path to private key
- ``cert``: Path to certificate

Getting CA Information
~~~~~~~~~~~~~~~~~~~~~~~

Get information about a specific CA:

.. code-block:: python

   ca_info = ca_manager.get_ca("myca")
   
   if ca_info:
       print(f"Found CA: {ca_info['name']}")
       print(f"Key: {ca_info['key']}")
       print(f"Cert: {ca_info['cert']}")
   else:
       print("CA not found")

Getting CA Details
~~~~~~~~~~~~~~~~~~

Get detailed information about a CA certificate:

.. code-block:: python

   ca_info = ca_manager.get_ca("myca")
   if ca_info:
       details = ca_manager.get_ca_info(ca_info['cert'])
       print(details['info'])  # OpenSSL certificate text output

Getting Certificates by CA
~~~~~~~~~~~~~~~~~~~~~~~~~~~

List all certificates signed by a specific CA:

.. code-block:: python

   certs = ca_manager.get_certs_by_ca("myca")
   
   for cert in certs:
       print(f"Certificate: {cert['name']}")
       print(f"  Key: {cert['key']}")
       print(f"  Cert: {cert['cert']}")

Deleting a CA
~~~~~~~~~~~~~

Delete a CA and all its certificates:

.. code-block:: python

   if ca_manager.delete_ca("myca"):
       print("CA and all its certificates deleted successfully")
   else:
       print("Failed to delete CA")

.. warning::

   Deleting a CA will also delete **all certificates** signed by that CA. 
   This operation cannot be undone. Make sure you have backups if needed.

Working with Certificates
--------------------------

Signing a Certificate
~~~~~~~~~~~~~~~~~~~~~

Sign a certificate using an existing CA:

.. code-block:: python

   # First, get the CA information
   ca_info = ca_manager.get_ca("myca")
   if not ca_info:
       print("CA not found!")
       exit(1)
   
   # Sign a server certificate
   try:
       result = cert_manager.sign_certificate(
           ca_key=ca_info["key"],
           ca_cert=ca_info["cert"],
           ca_name=ca_info["name"],
           cert_name="web-server",
           cert_type="server",  # or "client"
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
       
       print(f"Certificate signed successfully!")
       print(f"Key: {result['key']}")
       print(f"Cert: {result['cert']}")
   except Exception as e:
       print(f"Error signing certificate: {e}")

**Parameters:**

- ``ca_key``: Path to CA private key (required)
- ``ca_cert``: Path to CA certificate (required)
- ``ca_name``: Name of the CA (for directory organization)
- ``cert_name``: Name for the certificate (required)
- ``cert_type``: ``"server"`` or ``"client"`` (default: ``"server"``)
- ``common_name``: Common Name for the certificate (defaults to cert_name if empty)
- ``dns_names``: List of DNS names (optional)
- ``ip_addresses``: List of IP addresses (optional)
- ``organization``: Organization name (optional)
- ``country``: Country code (default: ``"CN"``)
- ``state``: State/Province (default: ``"Beijing"``)
- ``city``: City (default: ``"Beijing"``)
- ``validity_days``: Validity in days (default: ``365``)
- ``key_size``: Key size in bits (default: ``2048``)

**Return Value:**

Returns a dictionary with:
- ``cert_name``: Name of the certificate
- ``key``: Path to the private key file
- ``cert``: Path to the certificate file
- ``type``: Certificate type
- ``validity_days``: Validity period

.. note::

   The ``common_name`` parameter is optional. If not provided, Certica will use:
   1. First DNS name (if available)
   2. First IP address (if available)
   3. Certificate name (as fallback)

Listing Certificates
~~~~~~~~~~~~~~~~~~~~~

List all certificates:

.. code-block:: python

   certs = cert_manager.list_certificates()
   
   for cert in certs:
       print(f"Certificate: {cert['name']}")
       print(f"  CA: {cert['ca_name']}")
       print(f"  Key: {cert['key']}")
       print(f"  Cert: {cert['cert']}")

**Return Value:**

Returns a list of dictionaries, each containing:
- ``name``: Certificate name
- ``ca_name``: Name of the CA that signed it
- ``key``: Path to private key
- ``cert``: Path to certificate

Getting Certificate Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get detailed information about a certificate:

.. code-block:: python

   cert_path = "output/certs/myca/web-server/cert.pem"
   info = cert_manager.get_certificate_info(cert_path)
   print(info['info'])  # OpenSSL certificate text output

Deleting a Certificate
~~~~~~~~~~~~~~~~~~~~~~~

Delete a specific certificate:

.. code-block:: python

   if cert_manager.delete_certificate("myca", "web-server"):
       print("Certificate deleted successfully")
   else:
       print("Failed to delete certificate")

Working with Templates
-----------------------

Creating Templates
~~~~~~~~~~~~~~~~~~

Create a template for reuse:

.. code-block:: python

   template_path = template_manager.create_template(
       template_name="myorg",
       organization="My Company Inc.",
       country="US",
       state="California",
       city="San Francisco",
       default_validity_days=730,  # 2 years
       default_key_size=2048
   )
   
   print(f"Template created: {template_path}")

Loading Templates
~~~~~~~~~~~~~~~~~

Load a template to get default values:

.. code-block:: python

   template_data = template_manager.load_template("myorg")
   
   print(f"Organization: {template_data['organization']}")
   print(f"Country: {template_data['country']}")
   print(f"Default validity: {template_data['default_validity_days']} days")

.. note::

   If a template doesn't exist, ``load_template()`` returns default values instead 
   of raising an error. This makes it safe to use templates that may not exist yet.

Listing Templates
~~~~~~~~~~~~~~~~~

List all available templates:

.. code-block:: python

   templates = template_manager.list_templates()
   
   for template in templates:
       print(f"Template: {template}")

Deleting Templates
~~~~~~~~~~~~~~~~~~~

Delete a template:

.. code-block:: python

   if template_manager.delete_template("myorg"):
       print("Template deleted successfully")
   else:
       print("Template not found")

System Certificate Management
------------------------------

Installing CAs to System
~~~~~~~~~~~~~~~~~~~~~~~~~

Install a CA certificate to the system trust store:

.. code-block:: python

   ca_info = ca_manager.get_ca("myca")
   if not ca_info:
       print("CA not found!")
       exit(1)
   
   # Get sudo password (you might want to use getpass or environment variable)
   import getpass
   password = getpass.getpass("Enter sudo password: ")
   
   if system_cert_manager.install_ca_cert(
       ca_cert_path=ca_info["cert"],
       ca_name=ca_info["name"],
       password=password
   ):
       print("CA installed to system successfully!")
   else:
       print("Failed to install CA")

.. note::

   The ``SystemCertManager`` automatically detects your Linux distribution and uses 
   the appropriate installation method. It supports:
   
   - Debian/Ubuntu
   - Fedora/RHEL/CentOS
   - Arch/Manjaro
   - openSUSE/SLES

Removing CAs from System
~~~~~~~~~~~~~~~~~~~~~~~~

Remove a CA certificate from the system trust store:

.. code-block:: python

   import getpass
   password = getpass.getpass("Enter sudo password: ")
   
   if system_cert_manager.remove_ca_cert("myca", password):
       print("CA removed from system successfully!")
   else:
       print("Failed to remove CA")

Complete Examples
-----------------

Example 1: Automated Certificate Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a script that generates certificates for multiple services:

.. code-block:: python

   from certica.ca_manager import CAManager
   from certica.cert_manager import CertManager
   
   base_dir = "output"
   ca_manager = CAManager(base_dir)
   cert_manager = CertManager(base_dir)
   
   # Create or get CA
   ca_name = "production-ca"
   ca_info = ca_manager.get_ca(ca_name)
   
   if not ca_info:
       print(f"Creating CA: {ca_name}")
       result = ca_manager.create_root_ca(
           ca_name=ca_name,
           organization="My Company Inc.",
           country="US",
           validity_days=3650
       )
       ca_info = ca_manager.get_ca(ca_name)
   
   # Services to create certificates for
   services = [
       {"name": "api", "dns": ["api.example.com"]},
       {"name": "www", "dns": ["www.example.com", "example.com"]},
       {"name": "admin", "dns": ["admin.example.com"]},
   ]
   
   # Generate certificates
   for service in services:
       print(f"Creating certificate for {service['name']}...")
       try:
           result = cert_manager.sign_certificate(
               ca_key=ca_info["key"],
               ca_cert=ca_info["cert"],
               ca_name=ca_info["name"],
               cert_name=service["name"],
               cert_type="server",
               dns_names=service["dns"],
               organization="My Company Inc.",
               validity_days=365
           )
           print(f"  ✓ Created: {result['cert']}")
       except Exception as e:
           print(f"  ✗ Error: {e}")

Example 2: Certificate Rotation Script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a script that checks certificate expiration and rotates them:

.. code-block:: python

   from certica.cert_manager import CertManager
   from certica.ca_manager import CAManager
   from datetime import datetime
   import subprocess
   
   base_dir = "output"
   cert_manager = CertManager(base_dir)
   ca_manager = CAManager(base_dir)
   
   def get_cert_expiry(cert_path):
       """Get certificate expiration date"""
       result = subprocess.run(
           ["openssl", "x509", "-in", cert_path, "-noout", "-enddate"],
           capture_output=True,
           text=True
       )
       # Parse the date from output like "notAfter=Dec 31 23:59:59 2024 GMT"
       if result.returncode == 0:
           date_str = result.stdout.split("=")[1].strip()
           return datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z")
       return None
   
   # Check all certificates
   certs = cert_manager.list_certificates()
   today = datetime.now()
   
   for cert in certs:
       expiry = get_cert_expiry(cert["cert"])
       if expiry:
           days_until_expiry = (expiry - today).days
           if days_until_expiry < 30:  # Less than 30 days
               print(f"⚠ Certificate {cert['name']} expires in {days_until_expiry} days")
               # Add rotation logic here

Example 3: Integration with Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create certificates and update configuration files:

.. code-block:: python

   from certica.ca_manager import CAManager
   from certica.cert_manager import CertManager
   import json
   
   base_dir = "output"
   ca_manager = CAManager(base_dir)
   cert_manager = CertManager(base_dir)
   
   # Create certificate
   ca_info = ca_manager.get_ca("myca")
   result = cert_manager.sign_certificate(
       ca_key=ca_info["key"],
       ca_cert=ca_info["cert"],
       ca_name=ca_info["name"],
       cert_name="nginx-server",
       cert_type="server",
       dns_names=["example.com"]
   )
   
   # Update nginx configuration
   nginx_config = {
       "ssl_certificate": result["cert"],
       "ssl_certificate_key": result["key"]
   }
   
   # Save to configuration file
   with open("nginx_ssl_config.json", "w") as f:
       json.dump(nginx_config, f, indent=2)
   
   print("Certificate created and configuration updated!")

Best Practices
--------------

Error Handling
~~~~~~~~~~~~~~

Always handle exceptions properly:

.. code-block:: python

   try:
       result = ca_manager.create_root_ca(ca_name="myca")
   except FileExistsError:
       print("CA already exists - using existing one")
       ca_info = ca_manager.get_ca("myca")
   except Exception as e:
       print(f"Unexpected error: {e}")
       raise

Resource Cleanup
~~~~~~~~~~~~~~~~

Certica automatically cleans up partial files if operations fail, but you should 
still handle errors gracefully:

.. code-block:: python

   try:
       result = cert_manager.sign_certificate(...)
   except KeyboardInterrupt:
       print("Operation cancelled by user")
       # Certica will clean up partial files automatically
   except Exception as e:
       print(f"Error: {e}")
       # Check if partial files need manual cleanup

Security Considerations
~~~~~~~~~~~~~~~~~~~~~~~

- **Never commit private keys** to version control
- **Use proper file permissions** (Certica sets these automatically)
- **Protect CA keys** - they can sign any certificate
- **Use separate CAs** for different environments (dev, staging, production)
- **Rotate certificates** regularly
- **Monitor expiration dates** and set up alerts

.. warning::

   The CA private key is the most sensitive file. If compromised, an attacker can 
   create trusted certificates for any domain. Always:
   
   - Store CA keys securely
   - Use strong file permissions (Certica sets 600 automatically)
   - Consider encrypting CA keys at rest
   - Limit access to CA keys

Common Pitfalls
---------------

Forgetting to Check if CA Exists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Always check if a CA exists before using it:

.. code-block:: python

   # ❌ Bad: May fail if CA doesn't exist
   ca_info = ca_manager.get_ca("myca")
   result = cert_manager.sign_certificate(
       ca_key=ca_info["key"],  # This will fail if ca_info is None
       ...
   )
   
   # ✅ Good: Check first
   ca_info = ca_manager.get_ca("myca")
   if not ca_info:
       print("CA not found! Create it first.")
       exit(1)
   result = cert_manager.sign_certificate(
       ca_key=ca_info["key"],
       ...
   )

Not Including All DNS Names
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Always include all DNS names and IPs that will be used:

.. code-block:: python

   # ❌ Bad: Missing www subdomain
   cert_manager.sign_certificate(
       ...,
       dns_names=["example.com"]  # Missing www.example.com
   )
   
   # ✅ Good: Include all variations
   cert_manager.sign_certificate(
       ...,
       dns_names=["example.com", "www.example.com", "api.example.com"]
   )

Ignoring Return Values
~~~~~~~~~~~~~~~~~~~~~~

Always check return values:

.. code-block:: python

   # ❌ Bad: Not checking if operation succeeded
   system_cert_manager.install_ca_cert(...)
   
   # ✅ Good: Check return value
   if system_cert_manager.install_ca_cert(...):
       print("Installation successful")
   else:
       print("Installation failed - check logs")

