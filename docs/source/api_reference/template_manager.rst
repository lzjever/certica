Template Manager
================

The ``TemplateManager`` class handles template files for storing default certificate values. 
Templates help reduce repetitive input and ensure consistency.

Overview
--------

Templates store default values that can be reused when creating CAs and certificates:

- Organization information
- Location details (country, state, city)
- Default validity periods
- Default key sizes

Initialization
--------------

.. code-block:: python

   from certica.template_manager import TemplateManager
   
   # Initialize with default base directory
   template_manager = TemplateManager()
   
   # Or specify a custom base directory
   template_manager = TemplateManager(base_dir="/path/to/certificates")

**Parameters:**

- ``base_dir`` (str, optional): Base directory for storing templates. Default: ``"output"``

.. note::

   Templates are stored as JSON files in: ``{base_dir}/templates/{name}.json``

Methods
-------

create_template
~~~~~~~~~~~~~~~

Create a new template file.

.. code-block:: python

   template_path = template_manager.create_template(
       template_name="myorg",
       organization="My Company Inc.",
       country="US",
       state="California",
       city="San Francisco",
       default_validity_days=730,
       default_key_size=2048
   )

**Parameters:**

- ``template_name`` (str): Name for the template (required)
- ``organization`` (str, optional): Organization name. Default: ``"Development"``
- ``country`` (str, optional): Country code. Default: ``"CN"``
- ``state`` (str, optional): State/Province. Default: ``"Beijing"``
- ``city`` (str, optional): City. Default: ``"Beijing"``
- ``default_validity_days`` (int, optional): Default validity in days. Default: ``365``
- ``default_key_size`` (int, optional): Default key size in bits. Default: ``2048``

**Returns:**

Path to the created template file (str).

**Example:**

.. code-block:: python

   path = template_manager.create_template(
       template_name="production",
       organization="My Company Inc.",
       country="US",
       default_validity_days=730
   )
   print(f"Template created: {path}")

**Template File Format:**

Templates are stored as JSON:

.. code-block:: json

   {
     "organization": "My Company Inc.",
     "country": "US",
     "state": "California",
     "city": "San Francisco",
     "default_validity_days": 730,
     "default_key_size": 2048
   }

load_template
~~~~~~~~~~~~~

Load a template file to get default values.

.. code-block:: python

   template_data = template_manager.load_template("myorg")

**Parameters:**

- ``template_name`` (str, optional): Name of the template to load. If ``None``, loads default template.

**Returns:**

Dictionary containing template values. If template doesn't exist, returns default values.

**Example:**

.. code-block:: python

   template = template_manager.load_template("myorg")
   print(f"Organization: {template['organization']}")
   print(f"Country: {template['country']}")

.. note::

   If a template doesn't exist, this method returns default values instead of raising 
   an error. This makes it safe to use templates that may not exist yet.

list_templates
~~~~~~~~~~~~~~

List all available template files.

.. code-block:: python

   templates = template_manager.list_templates()

**Returns:**

List of template names (str).

**Example:**

.. code-block:: python

   templates = template_manager.list_templates()
   for template in templates:
       print(f"Template: {template}")

delete_template
~~~~~~~~~~~~~~~

Delete a template file.

.. code-block:: python

   success = template_manager.delete_template("myorg")

**Parameters:**

- ``template_name`` (str): Name of the template to delete

**Returns:**

``True`` if deletion was successful, ``False`` if template doesn't exist.

**Example:**

.. code-block:: python

   if template_manager.delete_template("myorg"):
       print("Template deleted")
   else:
       print("Template not found")

Complete Example
----------------

.. code-block:: python

   from certica.template_manager import TemplateManager
   from certica.ca_manager import CAManager
   
   template_manager = TemplateManager()
   ca_manager = CAManager()
   
   # Create a template
   template_manager.create_template(
       template_name="myorg",
       organization="My Company Inc.",
       country="US",
       state="California",
       city="San Francisco",
       default_validity_days=730
   )
   
   # Load template and use it
   template = template_manager.load_template("myorg")
   
   # Create CA using template values
   ca_manager.create_root_ca(
       ca_name="company-ca",
       organization=template["organization"],
       country=template["country"],
       state=template["state"],
       city=template["city"],
       validity_days=template["default_validity_days"]
   )

.. automodule:: certica.template_manager
   :members:
   :undoc-members:
   :show-inheritance:

