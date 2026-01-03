etcd Example
============

Create certificates for etcd cluster:

.. code-block:: bash

   # 1. Create root CA
   certica create-ca --name etcd-ca

   # 2. Sign server certificate
   certica sign --ca etcd-ca --name etcd-server \
       --type server --dns etcd.local --dns etcd-0.etcd.local \
       --ip 10.0.0.1 --ip 10.0.0.2

   # 3. Sign client certificate
   certica sign --ca etcd-ca --name etcd-client --type client

