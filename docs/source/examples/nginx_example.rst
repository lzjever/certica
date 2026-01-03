Nginx Example
=============

Create certificates for local Nginx development:

.. code-block:: bash

   # 1. Create root CA
   certica create-ca --name local-ca

   # 2. Sign server certificate
   certica sign --ca local-ca --name nginx \
       --type server --dns localhost --ip 127.0.0.1

   # 3. Install CA to system
   sudo certica install --ca local-ca

   # 4. Use in nginx configuration
   # ssl_certificate output/certs/local-ca/nginx/cert.pem;
   # ssl_certificate_key output/certs/local-ca/nginx/key.pem;

