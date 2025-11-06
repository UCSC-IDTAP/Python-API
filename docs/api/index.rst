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
   spectrogram

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

* :class:`idtap.SwaraClient` - Main API client
* :class:`idtap.Piece` - Complete transcription
* :class:`idtap.Phrase` - Musical phrase
* :class:`idtap.Trajectory` - Pitch trajectory
* :class:`idtap.Pitch` - Individual pitch point

Authentication
~~~~~~~~~~~~~~

* :func:`idtap.login_google` - Authenticate with Google OAuth

Audio Management
~~~~~~~~~~~~~~~~

* :class:`idtap.AudioMetadata` - Audio file metadata
* :class:`idtap.AudioUploadResult` - Upload response
* :class:`idtap.Musician` - Performer information

Spectrogram Analysis
~~~~~~~~~~~~~~~~~~~~

* :class:`idtap.SpectrogramData` - CQT spectrogram data and visualization
* :data:`idtap.SUPPORTED_COLORMAPS` - Available colormap names