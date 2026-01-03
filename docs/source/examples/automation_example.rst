Automation Example
==================

This example demonstrates how to automate certificate generation using Certica's 
Python API, perfect for integration with deployment scripts and CI/CD pipelines.

Scenario
--------

You need to automatically generate certificates for multiple services during deployment. 
The script should:

- Create a CA if it doesn't exist
- Generate certificates for a list of services
- Update configuration files
- Handle errors gracefully

Complete Python Script
----------------------

.. code-block:: python

   #!/usr/bin/env python3
   """
   Automated certificate generation script
   """
   
   import sys
   from pathlib import Path
   from certica.ca_manager import CAManager
   from certica.cert_manager import CertManager
   
   # Configuration
   BASE_DIR = "output"
   CA_NAME = "production-ca"
   CA_ORG = "My Company Inc."
   CA_COUNTRY = "US"
   CA_STATE = "California"
   CA_CITY = "San Francisco"
   CA_VALIDITY_DAYS = 3650  # 10 years
   
   # Services configuration: {name: {dns: [...], ip: [...]}}
   SERVICES = {
       "web-server": {
           "dns": ["example.com", "www.example.com"],
           "ip": ["192.168.1.100"]
       },
       "api-server": {
           "dns": ["api.example.com"],
           "ip": ["192.168.1.101"]
       },
       "admin-server": {
           "dns": ["admin.example.com"],
           "ip": ["192.168.1.102"]
       }
   }
   
   CERT_VALIDITY_DAYS = 365  # 1 year
   CERT_KEY_SIZE = 2048
   
   def create_ca_if_needed(ca_manager):
       """Create CA if it doesn't exist"""
       ca_info = ca_manager.get_ca(CA_NAME)
       
       if ca_info:
           print(f"✓ CA '{CA_NAME}' already exists")
           return ca_info
       
       print(f"Creating CA: {CA_NAME}...")
       try:
           result = ca_manager.create_root_ca(
               ca_name=CA_NAME,
               organization=CA_ORG,
               country=CA_COUNTRY,
               state=CA_STATE,
               city=CA_CITY,
               validity_days=CA_VALIDITY_DAYS,
               key_size=CERT_KEY_SIZE
           )
           print(f"✓ CA created successfully")
           return ca_manager.get_ca(CA_NAME)
       except Exception as e:
           print(f"✗ Error creating CA: {e}")
           sys.exit(1)
   
   def create_certificate(cert_manager, ca_info, service_name, config):
       """Create a certificate for a service"""
       print(f"  Creating certificate for {service_name}...")
       
       try:
           result = cert_manager.sign_certificate(
               ca_key=ca_info["key"],
               ca_cert=ca_info["cert"],
               ca_name=ca_info["name"],
               cert_name=service_name,
               cert_type="server",
               common_name=config["dns"][0] if config["dns"] else service_name,
               dns_names=config.get("dns", []),
               ip_addresses=config.get("ip", []),
               organization=CA_ORG,
               country=CA_COUNTRY,
               state=CA_STATE,
               city=CA_CITY,
               validity_days=CERT_VALIDITY_DAYS,
               key_size=CERT_KEY_SIZE
           )
           print(f"    ✓ Certificate created: {result['cert']}")
           return result
       except Exception as e:
           print(f"    ✗ Error creating certificate: {e}")
           return None
   
   def update_config_file(service_name, cert_info):
       """Update configuration file with certificate paths"""
       config_file = Path(f"config/{service_name}.json")
       config_file.parent.mkdir(parents=True, exist_ok=True)
       
       config = {
           "ssl_certificate": str(cert_info["cert"]),
           "ssl_certificate_key": str(cert_info["key"])
       }
       
       import json
       with open(config_file, "w") as f:
           json.dump(config, f, indent=2)
       
       print(f"    ✓ Configuration updated: {config_file}")
   
   def main():
       """Main function"""
       print("=" * 60)
       print("Automated Certificate Generation")
       print("=" * 60)
       
       # Initialize managers
       ca_manager = CAManager(BASE_DIR)
       cert_manager = CertManager(BASE_DIR)
       
       # Create or get CA
       ca_info = create_ca_if_needed(ca_manager)
       if not ca_info:
           print("✗ Failed to get CA information")
           sys.exit(1)
       
       # Generate certificates for each service
       print(f"\nGenerating certificates for {len(SERVICES)} services...")
       results = {}
       
       for service_name, config in SERVICES.items():
           cert_info = create_certificate(cert_manager, ca_info, service_name, config)
           if cert_info:
               results[service_name] = cert_info
               update_config_file(service_name, cert_info)
       
       # Summary
       print("\n" + "=" * 60)
       print("Summary")
       print("=" * 60)
       print(f"CA: {ca_info['name']}")
       print(f"Certificates created: {len(results)}/{len(SERVICES)}")
       
       if len(results) == len(SERVICES):
           print("✓ All certificates created successfully!")
           return 0
       else:
           print("✗ Some certificates failed to create")
           return 1
   
   if __name__ == "__main__":
       sys.exit(main())

Using the Script
----------------

Save the script as ``generate_certs.py`` and make it executable:

.. code-block:: bash

   chmod +x generate_certs.py
   ./generate_certs.py

Integration with CI/CD
-----------------------

**GitHub Actions Example:**

.. code-block:: yaml

   name: Generate Certificates
   
   on:
     workflow_dispatch:
     push:
       branches: [main]
   
   jobs:
     generate-certs:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.9'
         
         - name: Install Certica
           run: pip install certica
         
         - name: Generate certificates
           run: python generate_certs.py
         
         - name: Upload certificates
           uses: actions/upload-artifact@v3
           with:
             name: certificates
             path: output/

**GitLab CI Example:**

.. code-block:: yaml

   generate_certificates:
     stage: build
     image: python:3.9
     before_script:
       - pip install certica
     script:
       - python generate_certs.py
     artifacts:
       paths:
         - output/
       expire_in: 1 week

Integration with Ansible
-------------------------

Create an Ansible playbook:

.. code-block:: yaml

   - name: Generate certificates
     hosts: localhost
     tasks:
       - name: Install Certica
         pip:
           name: certica
       
       - name: Generate certificates
         command: python generate_certs.py
         register: cert_result
       
       - name: Display results
         debug:
           var: cert_result.stdout

Error Handling
--------------

The script includes basic error handling, but you can enhance it:

.. code-block:: python

   def create_certificate_safe(cert_manager, ca_info, service_name, config, retries=3):
       """Create certificate with retry logic"""
       for attempt in range(retries):
           try:
               return create_certificate(cert_manager, ca_info, service_name, config)
           except Exception as e:
               if attempt < retries - 1:
                   print(f"    Retrying... (attempt {attempt + 1}/{retries})")
                   time.sleep(1)
               else:
                   print(f"    ✗ Failed after {retries} attempts: {e}")
                   return None
       return None

Logging
-------

Add logging for better debugging:

.. code-block:: python

   import logging
   
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('cert_generation.log'),
           logging.StreamHandler()
       ]
   )
   
   logger = logging.getLogger(__name__)
   
   def create_ca_if_needed(ca_manager):
       logger.info(f"Checking for CA: {CA_NAME}")
       # ... rest of function

Best Practices
--------------

- **Validate inputs** before generating certificates
- **Use configuration files** instead of hardcoding values
- **Implement retry logic** for network operations
- **Log all operations** for audit trails
- **Test in development** before using in production
- **Back up CA keys** before automation runs
- **Monitor certificate expiration** and set up alerts

