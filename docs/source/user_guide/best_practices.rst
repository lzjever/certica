Best Practices and Common Pitfalls
====================================

This guide helps you avoid common mistakes and follow best practices when using Certica. 
Written for IT system operators who are new to certificate management.

Common Pitfalls
---------------

Pitfall 1: Forgetting to Install the CA
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:**

You create a CA and sign certificates, but browsers still show security warnings.

**Why it happens:**

Browsers and operating systems only trust certificates from CAs in their trust store. 
Your custom CA isn't trusted until you install it.

**Solution:**

Always install the CA to the system trust store after creating it:

.. code-block:: bash

   certica create-ca --name myca
   sudo certica install --ca myca  # Don't forget this step!

.. note::

   You only need to install the CA once. All certificates signed by that CA will 
   be trusted automatically.

Pitfall 2: Missing DNS Names or IP Addresses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:**

You create a certificate for ``example.com``, but when you access ``www.example.com``, 
you get a certificate error.

**Why it happens:**

Modern TLS checks the Subject Alternative Names (SANs), not just the Common Name. 
If a DNS name or IP address isn't in the SAN list, the certificate will be rejected.

**Solution:**

Include all DNS names and IP addresses that will be used:

.. code-block:: bash

   certica sign --ca myca --name web-server \
       --dns example.com \
       --dns www.example.com \
       --dns api.example.com \
       --ip 192.168.1.100 \
       --ip 127.0.0.1

.. note::

   Common mistakes:
   - Forgetting ``localhost`` when testing locally
   - Not including both ``example.com`` and ``www.example.com``
   - Missing IP addresses when accessing by IP
   - Not including all subdomains

Pitfall 3: Using the Same CA for Everything
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:**

You use one CA for development, staging, and production. When you need to revoke 
a certificate, it affects all environments.

**Why it happens:**

It seems convenient to use one CA, but it creates security and management issues.

**Solution:**

Use separate CAs for different environments:

.. code-block:: bash

   # Development
   certica create-ca --name dev-ca --org "Dev Environment"
   certica install --ca dev-ca
   
   # Staging
   certica create-ca --name staging-ca --org "Staging Environment"
   certica install --ca staging-ca
   
   # Production
   certica create-ca --name prod-ca --org "Production Environment"
   certica install --ca prod-ca

.. warning::

   Production CAs should be treated with extra security. Consider:
   - Storing CA keys in secure locations
   - Limiting access to production CA keys
   - Using hardware security modules (HSMs) for production
   - Regular security audits

Pitfall 4: Not Tracking Certificate Expiration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:**

Certificates expire unexpectedly, causing service outages.

**Why it happens:**

Certificates have expiration dates. If you don't monitor them, they'll expire 
and services will fail.

**Solution:**

Set up monitoring and renewal processes:

.. code-block:: bash

   # Check certificate expiration
   certica info --cert output/certs/myca/web-server/cert.pem
   
   # Look for "Not After" date in the output

**Best Practice:**

- Set up alerts for certificates expiring in 30 days
- Use longer validity periods for CAs (10 years)
- Use shorter validity periods for server certificates (1-2 years)
- Automate certificate renewal when possible

Pitfall 5: Incorrect File Permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:**

Private keys are readable by everyone, creating a security risk.

**Why it happens:**

File permissions weren't set correctly, or someone changed them.

**Solution:**

Certica automatically sets correct permissions:
- CA keys: ``600`` (read/write for owner only)
- Certificates: ``644`` (readable by all, writable by owner)

If you manually copy files, ensure permissions are correct:

.. code-block:: bash

   chmod 600 output/ca/myca/myca.key.pem
   chmod 644 output/ca/myca/myca.cert.pem

.. warning::

   Never make private keys world-readable. If a private key is compromised, 
   anyone can impersonate your server.

Pitfall 6: Using Weak Key Sizes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:**

You use 1024-bit keys, which are considered insecure.

**Why it happens:**

Older defaults or compatibility concerns.

**Solution:**

Always use at least 2048-bit keys (Certica's default):

.. code-block:: bash

   certica create-ca --name myca --key-size 2048
   certica sign --ca myca --name server --key-size 2048

.. note::

   For high-security environments, consider 4096-bit keys, but be aware they 
   have performance implications.

Pitfall 7: Not Backing Up CA Keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:**

You lose the CA private key, and can't create new certificates or verify existing ones.

**Why it happens:**

CA keys weren't backed up, and the system failed or files were deleted.

**Solution:**

Always back up CA keys securely:

.. code-block:: bash

   # Create backup
   tar -czf ca-backup-$(date +%Y%m%d).tar.gz output/ca/
   
   # Store backup securely (encrypted, off-site, etc.)

.. warning::

   CA keys are extremely sensitive. If you back them up:
   - Encrypt the backup
   - Store in a secure location
   - Limit access to backups
   - Use secure transfer methods

Pitfall 8: Confusing Certificate Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:**

You create a client certificate but try to use it as a server certificate.

**Why it happens:**

Server and client certificates have different purposes and extensions.

**Solution:**

Use the correct certificate type:

.. code-block:: bash

   # Server certificate (for web servers, APIs, etc.)
   certica sign --ca myca --name web-server --type server
   
   # Client certificate (for client authentication)
   certica sign --ca myca --name client1 --type client

.. note::

   - **Server certificates**: Used by servers to prove their identity to clients
   - **Client certificates**: Used by clients to prove their identity to servers
   - Some applications support both (mutual TLS)

Best Practices
--------------

Practice 1: Use Templates for Consistency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create templates for your organization to ensure consistency:

.. code-block:: bash

   # Create organization template
   certica create-template --name myorg \
       --org "My Company Inc." \
       --country US \
       --state "California" \
       --city "San Francisco"
   
   # Use template for all certificates
   certica create-ca --template myorg --name company-ca
   certica sign --ca company-ca --name server1 --template myorg

**Benefits:**

- Consistent organization information
- Less typing and fewer errors
- Easy to update organization-wide

Practice 2: Organize by Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use different base directories for different environments:

.. code-block:: bash

   # Development
   certica --base-dir output/dev create-ca --name dev-ca
   
   # Staging
   certica --base-dir output/staging create-ca --name staging-ca
   
   # Production
   certica --base-dir output/prod create-ca --name prod-ca

**Benefits:**

- Clear separation of environments
- Easy to manage and clean up
- Reduces risk of using wrong certificates

Practice 3: Document Your Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Keep a record of your CA and certificate setup:

.. code-block:: text

   # Certificate Management Log
   
   ## CAs
   - dev-ca: Created 2024-01-01, Validity: 10 years
   - staging-ca: Created 2024-01-01, Validity: 10 years
   - prod-ca: Created 2024-01-01, Validity: 10 years
   
   ## Certificates
   - web-server (dev-ca): example.com, www.example.com
   - api-server (dev-ca): api.example.com
   
   ## Expiration Dates
   - web-server: 2025-01-01
   - api-server: 2025-01-01

**Benefits:**

- Easy to track what certificates exist
- Helps with renewal planning
- Useful for troubleshooting

Practice 4: Test Certificates Before Production
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Always test certificates in development first:

.. code-block:: bash

   # 1. Create test CA
   certica create-ca --name test-ca
   sudo certica install --ca test-ca
   
   # 2. Create test certificate
   certica sign --ca test-ca --name test-server \
       --dns test.example.com
   
   # 3. Test with your application
   # 4. If successful, create production certificate

**Benefits:**

- Catches configuration errors early
- Verifies certificate works with your application
- Reduces production issues

Practice 5: Use Descriptive Names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use clear, descriptive names for CAs and certificates:

.. code-block:: bash

   # ❌ Bad: Unclear names
   certica create-ca --name ca1
   certica sign --ca ca1 --name cert1
   
   # ✅ Good: Descriptive names
   certica create-ca --name production-ca
   certica sign --ca production-ca --name api-production-server

**Benefits:**

- Easier to identify certificates
- Reduces confusion
- Better for documentation

Practice 6: Regular Cleanup
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Periodically review and clean up unused certificates:

.. code-block:: bash

   # List all certificates
   certica list-certs
   
   # Remove unused CAs (this also removes all their certificates)
   # Be careful - this cannot be undone!

**Benefits:**

- Reduces clutter
- Easier to find what you need
- Better security (fewer certificates to manage)

Practice 7: Monitor Certificate Expiration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set up monitoring for certificate expiration:

.. code-block:: python

   # Example: Check expiration dates
   import subprocess
   from datetime import datetime
   
   def check_expiry(cert_path):
       result = subprocess.run(
           ["openssl", "x509", "-in", cert_path, "-noout", "-enddate"],
           capture_output=True, text=True
       )
       # Parse and check date
       # Alert if expiring soon

**Benefits:**

- Prevents unexpected outages
- Allows time for renewal
- Better service reliability

Security Considerations
------------------------

CA Key Security
~~~~~~~~~~~~~~~

The CA private key is the most critical security component:

- **Never share CA keys** - If someone has your CA key, they can create trusted certificates
- **Use strong file permissions** - Certica sets 600 automatically, don't change it
- **Back up securely** - Encrypt backups and store in secure locations
- **Limit access** - Only trusted personnel should have access to CA keys
- **Monitor for changes** - Set up file integrity monitoring

Certificate Validity Periods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choose appropriate validity periods:

- **CA certificates**: 10 years (3650 days) - CAs are long-lived
- **Server certificates**: 1-2 years (365-730 days) - Balance security and convenience
- **Client certificates**: 1 year or less - Shorter for better security

.. note::

   Shorter validity periods are more secure (less time for compromise) but require 
   more frequent renewal. Longer validity periods are more convenient but less secure.

Environment Separation
~~~~~~~~~~~~~~~~~~~~~~~

Always separate development, staging, and production:

- **Different CAs** for each environment
- **Different base directories** for organization
- **Different access controls** for production
- **Never use production CAs** in development

Network Security
~~~~~~~~~~~~~~~~

When transferring certificates:

- **Use secure channels** (SSH, HTTPS, encrypted storage)
- **Verify integrity** after transfer (compare checksums)
- **Don't email certificates** - Use secure file transfer methods
- **Encrypt in transit** - Always use encrypted connections

Troubleshooting Guide
---------------------

Certificate Not Trusted
~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:** Browser shows "Certificate not trusted" or "Invalid certificate"

**Solutions:**

1. Check if CA is installed:
   
   .. code-block:: bash
      
      certica list-cas
      # Verify CA exists
   
2. Install the CA:
   
   .. code-block:: bash
      
      sudo certica install --ca myca
   
3. Verify certificate details:
   
   .. code-block:: bash
      
      certica info --cert output/certs/myca/web-server/cert.pem
   
4. Check DNS names match:
   
   - Verify all DNS names are in the certificate
   - Check for typos
   - Ensure www vs non-www is included

Certificate Expired
~~~~~~~~~~~~~~~~~~~

**Symptoms:** "Certificate expired" error

**Solutions:**

1. Check expiration date:
   
   .. code-block:: bash
      
      certica info --cert <cert_path>
      # Look for "Not After" date
   
2. Create new certificate:
   
   .. code-block:: bash
      
      certica sign --ca myca --name web-server --validity 365

3. Update application configuration with new certificate paths

Permission Denied
~~~~~~~~~~~~~~~~~

**Symptoms:** "Permission denied" when accessing keys or certificates

**Solutions:**

1. Check file permissions:
   
   .. code-block:: bash
      
      ls -l output/ca/myca/
   
2. Fix permissions if needed:
   
   .. code-block:: bash
      
      chmod 600 output/ca/myca/myca.key.pem
      chmod 644 output/ca/myca/myca.cert.pem

CA Not Found
~~~~~~~~~~~~~

**Symptoms:** "CA not found" error when signing certificates

**Solutions:**

1. List all CAs:
   
   .. code-block:: bash
      
      certica list-cas
   
2. Check CA name spelling (case-sensitive)
3. Verify CA was created successfully
4. Check base directory if using custom path

OpenSSL Errors
~~~~~~~~~~~~~~~

**Symptoms:** OpenSSL-related errors

**Solutions:**

1. Verify OpenSSL is installed:
   
   .. code-block:: bash
      
      openssl version
   
2. Check system requirements:
   
   .. code-block:: bash
      
      certica --check-only
   
3. Ensure OpenSSL is in PATH
4. Check OpenSSL version (should be recent)

Getting Help
------------

If you encounter issues:

1. **Check the documentation** - This guide and other docs
2. **Review error messages** - They often contain helpful information
3. **Verify system requirements** - Use ``certica --check-only``
4. **Check file permissions** - Ensure proper access
5. **Review certificate details** - Use ``certica info`` to inspect certificates
6. **Check GitHub Issues** - See if others have encountered similar problems

Remember: Certificate management can be complex, but following these best practices 
and avoiding common pitfalls will make your life much easier!

