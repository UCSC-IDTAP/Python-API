API Reference
=============

Complete API documentation for all classes and methods in the IDTAP API.

Core Client
-----------

.. toctree::
   :maxdepth: 2

   client
   auth

Data Models
-----------

Musical transcription data models:

.. toctree::
   :maxdepth: 2

   transcription-models
   audio-models

Utilities
---------

.. toctree::
   :maxdepth: 2

   enums
   utils

Quick Reference
---------------

Main Classes
~~~~~~~~~~~~

* :class:`idtap_api.SwaraClient` - Main API client
* :class:`idtap_api.Piece` - Complete transcription
* :class:`idtap_api.Phrase` - Musical phrase
* :class:`idtap_api.Trajectory` - Pitch trajectory
* :class:`idtap_api.Pitch` - Individual pitch point

Authentication
~~~~~~~~~~~~~~

* :func:`idtap_api.login_google` - Authenticate with Google OAuth

Audio Management
~~~~~~~~~~~~~~~~

* :class:`idtap_api.AudioMetadata` - Audio file metadata
* :class:`idtap_api.AudioUploadResult` - Upload response
* :class:`idtap_api.Musician` - Performer information