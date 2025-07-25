SwaraClient
===========

The main client class for interacting with the IDTAP API.

.. currentmodule:: idtap_api

.. autoclass:: SwaraClient
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from idtap_api import SwaraClient
   
   client = SwaraClient()
   transcriptions = client.get_transcriptions()

Custom Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Use custom server (for development)
   client = SwaraClient(base_url="http://localhost:3000")

Methods Overview
----------------

Transcription Methods
~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   
   SwaraClient.get_transcriptions
   SwaraClient.get_transcription
   SwaraClient.create_transcription
   SwaraClient.update_transcription
   SwaraClient.delete_transcription

Audio Methods
~~~~~~~~~~~~~

.. autosummary::
   
   SwaraClient.upload_audio
   SwaraClient.download_audio
   SwaraClient.get_audio_metadata

Export Methods
~~~~~~~~~~~~~~

.. autosummary::
   
   SwaraClient.export_transcription_json
   SwaraClient.export_transcription_excel

Permission Methods
~~~~~~~~~~~~~~~~~~

.. autosummary::
   
   SwaraClient.update_visibility
   SwaraClient.get_permissions