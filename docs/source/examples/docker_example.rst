Docker Certificate Example
===========================

This example shows how to use Certica to generate certificates for Docker containers 
and services.

Scenario
--------

You're running multiple Docker containers that need to communicate securely using TLS. 
You need certificates for:

- A web server container
- An API server container
- Inter-container communication

Step 1: Create a CA
-------------------

First, create a CA for your Docker environment:

.. code-block:: bash

   certica create-ca --name docker-ca \
       --org "Docker Development" \
       --validity 3650

Step 2: Generate Server Certificates
-------------------------------------

Create certificates for each service:

.. code-block:: bash

   # Web server certificate
   certica sign --ca docker-ca --name web-server \
       --type server \
       --dns web.example.com \
       --dns localhost \
       --ip 127.0.0.1
   
   # API server certificate
   certica sign --ca docker-ca --name api-server \
       --type server \
       --dns api.example.com \
       --dns localhost \
       --ip 127.0.0.1

Step 3: Install CA (Optional)
------------------------------

If you want to access services from your host machine, install the CA:

.. code-block:: bash

   sudo certica install --ca docker-ca

Step 4: Use Certificates in Docker
-----------------------------------

**Option A: Copy certificates into container**

Create a Dockerfile that copies certificates:

.. code-block:: dockerfile

   FROM nginx:alpine
   
   # Copy certificates
   COPY output/certs/docker-ca/web-server/cert.pem /etc/ssl/certs/web-server.crt
   COPY output/certs/docker-ca/web-server/key.pem /etc/ssl/private/web-server.key
   
   # Configure nginx
   COPY nginx.conf /etc/nginx/nginx.conf

**Option B: Mount certificates as volumes**

Use Docker volumes to mount certificates:

.. code-block:: bash

   docker run -d \
       -v $(pwd)/output/certs/docker-ca/web-server:/etc/ssl/certs \
       -p 443:443 \
       nginx:alpine

**Option C: Use Docker secrets (Docker Swarm)**

For Docker Swarm, use secrets:

.. code-block:: bash

   # Create secrets
   docker secret create web-server-cert output/certs/docker-ca/web-server/cert.pem
   docker secret create web-server-key output/certs/docker-ca/web-server/key.pem
   
   # Use in service
   docker service create \
       --secret web-server-cert \
       --secret web-server-key \
       --name web-server \
       nginx:alpine

Step 5: Configure Application
------------------------------

Configure your application to use the certificates:

**Nginx example:**

.. code-block:: nginx

   server {
       listen 443 ssl;
       server_name web.example.com;
       
       ssl_certificate /etc/ssl/certs/web-server.crt;
       ssl_certificate_key /etc/ssl/private/web-server.key;
       
       location / {
           return 200 "Hello from secure web server!";
           add_header Content-Type text/plain;
       }
   }

**Python Flask example:**

.. code-block:: python

   from flask import Flask
   
   app = Flask(__name__)
   
   if __name__ == '__main__':
       app.run(
           host='0.0.0.0',
           port=443,
           ssl_context=(
               'output/certs/docker-ca/web-server/cert.pem',
               'output/certs/docker-ca/web-server/key.pem'
           )
       )

**Node.js Express example:**

.. code-block:: javascript

   const express = require('express');
   const https = require('https');
   const fs = require('fs');
   
   const app = express();
   
   const options = {
       cert: fs.readFileSync('output/certs/docker-ca/web-server/cert.pem'),
       key: fs.readFileSync('output/certs/docker-ca/web-server/key.pem')
   };
   
   https.createServer(options, app).listen(443, () => {
       console.log('Server running on https://localhost:443');
   });

Complete Docker Compose Example
-------------------------------

Here's a complete Docker Compose setup:

.. code-block:: yaml

   version: '3.8'
   
   services:
     web:
       image: nginx:alpine
       ports:
         - "443:443"
       volumes:
         - ./output/certs/docker-ca/web-server:/etc/ssl/certs
         - ./nginx.conf:/etc/nginx/nginx.conf
       networks:
         - app-network
   
     api:
       image: python:3.9
       command: python app.py
       volumes:
         - ./output/certs/docker-ca/api-server:/etc/ssl/certs
         - ./api:/app
       networks:
         - app-network
   
   networks:
     app-network:
       driver: bridge

Automation Script
-----------------

Create a script to automate certificate generation for Docker:

.. code-block:: bash

   #!/bin/bash
   
   CA_NAME="docker-ca"
   BASE_DIR="output"
   
   # Create CA if it doesn't exist
   if ! certica list-cas | grep -q "$CA_NAME"; then
       echo "Creating CA: $CA_NAME"
       certica create-ca --name "$CA_NAME" --org "Docker Development"
   fi
   
   # Services to create certificates for
   declare -A services=(
       ["web-server"]="web.example.com,localhost"
       ["api-server"]="api.example.com,localhost"
   )
   
   # Generate certificates
   for service_name in "${!services[@]}"; do
       dns_names=$(echo "${services[$service_name]}" | tr ',' ' ')
       dns_args=""
       for dns in $dns_names; do
           dns_args="$dns_args --dns $dns"
       done
       
       echo "Creating certificate for $service_name..."
       certica sign --ca "$CA_NAME" --name "$service_name" \
           --type server $dns_args --ip 127.0.0.1
   done
   
   echo "Certificates created successfully!"
   echo "Use them in Docker with:"
   echo "  docker run -v \$(pwd)/$BASE_DIR/certs/$CA_NAME:/etc/ssl/certs ..."

.. note::

   This script creates certificates for multiple services automatically. 
   You can extend it to include more services or customize DNS names.

Tips
----

- **Use separate CAs** for different Docker environments (dev, staging, prod)
- **Mount certificates as read-only** volumes for better security
- **Use Docker secrets** in production for better security
- **Rotate certificates** regularly, especially in production
- **Monitor certificate expiration** to avoid service outages

