Quick Start
===========

Installation
------------

Quick Install
~~~~~~~~~~~~~

.. code-block:: bash

   pip install certica

Development Setup
~~~~~~~~~~~~~~~~~

For development, use uv (recommended):

.. code-block:: bash

   curl -LsSf https://astral.sh/uv/install.sh | sh
   make dev-install

Interactive UI Mode
-------------------

Launch the interactive UI:

.. code-block:: bash

   certica ui

Or with a specific language:

.. code-block:: bash

   certica ui --lang zh  # Chinese

Command Line Mode
-----------------

Create a Root CA
~~~~~~~~~~~~~~~~

.. code-block:: bash

   certica create-ca --name myca

Sign a Certificate
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   certica sign --ca myca --name nginx-server --type server \
       --dns localhost --dns example.com --ip 127.0.0.1

List Certificates
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   certica list-cas
   certica list-certs

Install to System
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo certica install --ca myca

For more detailed information, see the :doc:`user_guide/index`.

