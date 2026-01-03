CLI Reference
=============

This comprehensive guide covers all command-line options and usage patterns for Certica. 
Perfect for IT system operators who want to automate certificate management tasks.

Global Options
--------------

All Certica commands support these global options:

.. code-block:: bash

   certica [GLOBAL_OPTIONS] <command> [COMMAND_OPTIONS]

**Global Options:**

- ``--base-dir <directory>``: Base directory for output files (default: ``output``)
- ``--skip-check``: Skip system requirements check (useful for automation)
- ``--check-only``: Only check system requirements and exit (useful for validation)

.. note::

   The ``--base-dir`` option is particularly useful when you need to manage certificates 
   in different locations or for different projects. For example, you might use 
   ``--base-dir /var/certs/production`` for production certificates and 
   ``--base-dir /var/certs/staging`` for staging certificates.

.. warning::

   Using ``--skip-check`` bypasses important system validation. Only use this if you're 
   certain your system has all required tools (OpenSSL) installed and configured correctly.

Commands
--------

create-ca
~~~~~~~~~

Create a root Certificate Authority (CA) certificate.

**Syntax:**

.. code-block:: bash

   certica create-ca [OPTIONS]

**Options:**

- ``--name <name>``: CA name (default: ``myca``)
- ``--org <organization>``: Organization name (default: ``Development CA``)
- ``--country <code>``: Country code, 2 letters (default: ``CN``)
- ``--state <state>``: State or Province (default: ``Beijing``)
- ``--city <city>``: City name (default: ``Beijing``)
- ``--validity <days>``: Validity period in days (default: ``3650``, ~10 years)
- ``--key-size <bits>``: Key size in bits (default: ``2048``)
- ``--template <name>``: Template file to use for defaults

**Examples:**

Create a basic CA with default settings:

.. code-block:: bash

   certica create-ca

Create a CA with custom organization and validity:

.. code-block:: bash

   certica create-ca --name company-ca \
       --org "My Company Inc." \
       --country US \
       --state "California" \
       --city "San Francisco" \
       --validity 7300

Create a CA using a template:

.. code-block:: bash

   certica create-ca --template myorg --name production-ca

.. note::

   CA names must be unique. If you try to create a CA with a name that already exists, 
   Certica will return an error. Use ``list-cas`` to see existing CAs before creating new ones.

.. warning::

   The CA private key (``.key.pem``) is extremely sensitive. If it's compromised, 
   anyone can issue certificates that will be trusted by your system. Always protect 
   the CA key file with proper file permissions (Certica sets this automatically to 600).

sign
~~~~

Sign a certificate using an existing CA.

**Syntax:**

.. code-block:: bash

   certica sign --ca <ca_name> --name <cert_name> [OPTIONS]

**Required Options:**

- ``--ca <name>``: Name of the CA to use for signing (required)
- ``--name <name>``: Name for the certificate (required)

**Options:**

- ``--type <type>``: Certificate type - ``server`` or ``client`` (default: ``server``)
- ``--cn <name>``: Common Name (defaults to certificate name if not specified)
- ``--dns <name>``: DNS name (can be specified multiple times)
- ``--ip <address>``: IP address (can be specified multiple times)
- ``--org <organization>``: Organization name (default: ``Development``)
- ``--country <code>``: Country code (default: ``CN``)
- ``--state <state>``: State/Province (default: ``Beijing``)
- ``--city <city>``: City (default: ``Beijing``)
- ``--validity <days>``: Validity in days (default: ``365``, 1 year)
- ``--key-size <bits>``: Key size in bits (default: ``2048``)
- ``--template <name>``: Template file to use for defaults

**Examples:**

Sign a server certificate for localhost:

.. code-block:: bash

   certica sign --ca myca --name localhost-server \
       --type server \
       --dns localhost \
       --dns localhost.localdomain \
       --ip 127.0.0.1

Sign a certificate for a web server with multiple domains:

.. code-block:: bash

   certica sign --ca company-ca --name web-server \
       --type server \
       --dns example.com \
       --dns www.example.com \
       --dns api.example.com \
       --ip 192.168.1.100

Sign a client certificate:

.. code-block:: bash

   certica sign --ca myca --name client1 --type client

Sign a certificate using a template:

.. code-block:: bash

   certica sign --ca myca --name server1 \
       --template myorg \
       --type server \
       --dns server1.example.com

.. note::

   When signing server certificates, always include all DNS names and IP addresses 
   that the server will use. Browsers and clients will reject certificates if the 
   hostname doesn't match exactly. Common mistakes include:
   
   - Forgetting to include ``localhost`` when testing locally
   - Not including both ``example.com`` and ``www.example.com``
   - Missing IP addresses when accessing by IP

.. warning::

   The Common Name (CN) field is less important in modern TLS. The Subject Alternative 
   Names (SANs) specified with ``--dns`` and ``--ip`` are what browsers actually check. 
   However, it's still good practice to set a meaningful CN.

list-cas
~~~~~~~~

List all available CA certificates.

**Syntax:**

.. code-block:: bash

   certica list-cas

**Example Output:**

.. code-block:: text

   Available CA Certificates:
     0. 🔑 myca
        Key: ca/myca/myca.key.pem
        Cert: ca/myca/myca.cert.pem
     1. 🔑 company-ca
        Key: ca/company-ca/company-ca.key.pem
        Cert: ca/company-ca/company-ca.cert.pem

.. note::

   This command is useful for:
   - Finding the correct CA name to use with the ``sign`` command
   - Verifying that a CA was created successfully
   - Checking which CAs exist before creating new ones

list-certs
~~~~~~~~~~

List all signed certificates, optionally filtered by CA.

**Syntax:**

.. code-block:: bash

   certica list-certs [--ca <ca_name>]

**Options:**

- ``--ca <name>``: Filter certificates by CA name (optional)

**Examples:**

List all certificates:

.. code-block:: bash

   certica list-certs

List certificates for a specific CA:

.. code-block:: bash

   certica list-certs --ca myca

**Example Output:**

.. code-block:: text

   Certificates for CA: myca
     📜 localhost-server
        Key: certs/myca/localhost-server/key.pem
        Cert: certs/myca/localhost-server/cert.pem
     📜 web-server
        Key: certs/myca/web-server/key.pem
        Cert: certs/myca/web-server/cert.pem

.. note::

   Certificates are automatically organized by CA in the directory structure. 
   This makes it easy to see which certificates belong to which CA and to 
   manage certificates in bulk (e.g., deleting all certificates for a specific CA).

create-template
~~~~~~~~~~~~~~~

Create a template file with default values for certificate generation.

**Syntax:**

.. code-block:: bash

   certica create-template --name <template_name> [OPTIONS]

**Required Options:**

- ``--name <name>``: Template name (required)

**Options:**

- ``--org <organization>``: Organization name (default: ``Development``)
- ``--country <code>``: Country code (default: ``CN``)
- ``--state <state>``: State/Province (default: ``Beijing``)
- ``--city <city>``: City (default: ``Beijing``)
- ``--validity <days>``: Default validity in days (default: ``365``)
- ``--key-size <bits>``: Default key size in bits (default: ``2048``)

**Examples:**

Create a template for your organization:

.. code-block:: bash

   certica create-template --name myorg \
       --org "My Company Inc." \
       --country US \
       --state "California" \
       --city "San Francisco" \
       --validity 730 \
       --key-size 2048

**Template File Location:**

Templates are saved as JSON files in ``output/templates/<name>.json``. 
You can edit these files directly if needed.

**Example Template Content:**

.. code-block:: json

   {
     "organization": "My Company Inc.",
     "country": "US",
     "state": "California",
     "city": "San Francisco",
     "default_validity_days": 730,
     "default_key_size": 2048
   }

.. note::

   Templates are particularly useful when you need to create multiple certificates 
   with the same organization information. Instead of typing the same values repeatedly, 
   you can create a template once and reuse it.

list-templates
~~~~~~~~~~~~~~

List all available template files.

**Syntax:**

.. code-block:: bash

   certica list-templates

**Example Output:**

.. code-block:: text

   Available Templates:
     📝 myorg
     📝 default
     📝 production

install
~~~~~~~

Install a CA certificate to the system trust store.

**Syntax:**

.. code-block:: bash

   certica install --ca <ca_name> [--password <password>]

**Required Options:**

- ``--ca <name>``: CA name to install (required)

**Options:**

- ``--password <password>``: Sudo password (will prompt if not provided)

**Examples:**

Install a CA (will prompt for password):

.. code-block:: bash

   certica install --ca myca

Install a CA with password (useful for automation):

.. code-block:: bash

   certica install --ca myca --password "your-password"

.. note::

   Installing a CA to the system trust store makes all certificates signed by that CA 
   trusted by the system and browsers. This is essential for local development and testing.
   
   After installation, you won't see browser warnings when accessing sites using 
   certificates signed by this CA.

.. warning::

   Installing a CA to the system trust store requires sudo/administrator privileges. 
   Only install CAs that you trust. A compromised CA can be used to create certificates 
   for any domain, which is a serious security risk.

.. note::

   Certica automatically detects your Linux distribution and uses the appropriate 
   installation method:
   
   - **Debian/Ubuntu**: Uses ``update-ca-certificates``
   - **Fedora/RHEL/CentOS**: Uses ``update-ca-trust extract``
   - **Arch/Manjaro**: Uses ``trust extract-compat`` or ``update-ca-certificates``
   - **openSUSE/SLES**: Uses ``update-ca-certificates``

remove
~~~~~~

Remove a CA certificate from the system trust store.

**Syntax:**

.. code-block:: bash

   certica remove --ca <ca_name> [--password <password>]

**Required Options:**

- ``--ca <name>``: CA name to remove (required)

**Options:**

- ``--password <password>``: Sudo password (will prompt if not provided)

**Examples:**

Remove a CA (will prompt for password):

.. code-block:: bash

   certica remove --ca myca

.. note::

   Removing a CA from the system trust store means certificates signed by that CA 
   will no longer be trusted. This is useful when:
   
   - You no longer need a development CA
   - You want to test certificate validation
   - You're cleaning up old CAs

info
~~~~

Display detailed information about a certificate.

**Syntax:**

.. code-block:: bash

   certica info --cert <certificate_path>

**Required Options:**

- ``--cert <path>``: Path to certificate file (required)

**Examples:**

Show information about a certificate:

.. code-block:: bash

   certica info --cert output/certs/myca/localhost-server/cert.pem

**Example Output:**

The output shows detailed certificate information including:
- Subject and Issuer information
- Validity period (not before/not after)
- Serial number
- Key usage and extended key usage
- Subject Alternative Names (SANs)
- Certificate extensions

.. note::

   This command is useful for:
   - Verifying certificate details
   - Checking expiration dates
   - Debugging certificate issues
   - Confirming DNS names and IP addresses are correct

ui
~~

Launch the interactive UI mode.

**Syntax:**

.. code-block:: bash

   certica ui [--lang <language_code>]

**Options:**

- ``--lang <code>`` or ``-l <code>``: Language code for UI (en, zh, fr, ru, ja, ko)

**Examples:**

Launch UI with default language (English):

.. code-block:: bash

   certica ui

Launch UI with Chinese:

.. code-block:: bash

   certica ui --lang zh

.. note::

   The UI mode provides a user-friendly menu-driven interface for all operations. 
   It's perfect for beginners or when you're not sure which command to use.
   
   The ``--lang`` option is **only available in UI mode**. CLI commands always use 
   English for script compatibility.

Common Usage Patterns
---------------------

Automation Scripts
~~~~~~~~~~~~~~~~~~

When using Certica in automation scripts, use ``--skip-check`` to avoid interactive prompts:

.. code-block:: bash

   #!/bin/bash
   certica --skip-check create-ca --name auto-ca
   certica --skip-check sign --ca auto-ca --name auto-cert --type server --dns example.com

Using Custom Base Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Manage certificates for different environments:

.. code-block:: bash

   # Production certificates
   certica --base-dir /var/certs/prod create-ca --name prod-ca
   
   # Staging certificates
   certica --base-dir /var/certs/staging create-ca --name staging-ca

Batch Certificate Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create multiple certificates using a loop:

.. code-block:: bash

   #!/bin/bash
   CA_NAME="myca"
   DOMAINS=("api.example.com" "www.example.com" "admin.example.com")
   
   for domain in "${DOMAINS[@]}"; do
       certica sign --ca "$CA_NAME" --name "$domain" \
           --type server --dns "$domain"
   done

Troubleshooting
----------------

Command Not Found
~~~~~~~~~~~~~~~~~

If you get "command not found", make sure Certica is installed:

.. code-block:: bash

   pip install certica

Or check if it's in your PATH:

.. code-block:: bash

   which certica

Permission Denied
~~~~~~~~~~~~~~~~~

If you get permission errors when installing/removing CAs:

- Make sure you have sudo privileges
- Check that the password is correct
- Verify that the CA exists: ``certica list-cas``

CA Not Found
~~~~~~~~~~~~

If you get "CA not found" errors:

- List all CAs: ``certica list-cas``
- Check the CA name spelling (case-sensitive)
- Verify the CA was created successfully

Certificate Validation Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If browsers show certificate errors:

- Make sure the CA is installed: ``certica install --ca <ca_name>``
- Verify DNS names match exactly (including www vs non-www)
- Check certificate expiration: ``certica info --cert <path>``
- Ensure the certificate type matches (server vs client)

