IDTAP API Documentation
=======================

The **IDTAP API** is a Python client library for the Interactive Digital Transcription and Analysis Platform, designed specifically for transcribing, analyzing, and managing Hindustani music recordings.

.. note::
   This is the client API documentation. For the main IDTAP web application, visit `swara.studio <https://swara.studio>`_.

Quick Start
-----------

Install the package from PyPI:

.. code-block:: bash

   pip install idtap-api

Basic usage:

.. code-block:: python

   from idtap_api import SwaraClient, login_google
   
   # Authenticate with Google OAuth
   login_google()
   
   # Create client and get transcriptions
   client = SwaraClient()
   transcriptions = client.get_transcriptions()

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   authentication
   quickstart
   user-guide
   api/index
   examples/index

Features
--------

* **OAuth Authentication** - Secure Google OAuth integration with token storage
* **Rich Data Models** - Comprehensive classes for musical transcription data
* **Audio Management** - Upload, download, and manage audio files
* **Export Capabilities** - Export transcriptions to JSON and Excel formats
* **Permissions System** - Manage public/private visibility and sharing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`