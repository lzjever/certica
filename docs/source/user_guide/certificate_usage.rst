Using Generated Certificates
=============================

For Web Servers (Nginx, Apache)
--------------------------------

1. Install CA to system:

   .. code-block:: bash

      sudo certica install --ca your-ca-name

2. Configure your web server with the certificate paths.

For etcd
--------

Use the certificates in your etcd configuration file.

For Docker
----------

Copy certificates into your Docker containers or mount as volumes.

