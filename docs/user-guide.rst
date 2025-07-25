User Guide
==========

Comprehensive guide to using the IDTAP API for musical transcription analysis.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   user-guide/getting-started
   user-guide/working-with-transcriptions
   user-guide/audio-management
   user-guide/data-export
   user-guide/advanced-features

Overview
--------

The IDTAP API provides programmatic access to the Interactive Digital Transcription and Analysis Platform, a specialized system for analyzing Hindustani classical music. This guide covers:

* **Authentication** - Setting up secure access
* **Transcription Management** - Loading and working with musical data
* **Audio Processing** - Uploading and managing audio files
* **Data Export** - Exporting analysis results
* **Advanced Features** - Batch processing and custom analysis

Key Concepts
------------

Transcription Structure
~~~~~~~~~~~~~~~~~~~~~~~

IDTAP transcriptions follow a hierarchical structure:

.. code-block::

   Piece (Complete Transcription)
   ├── Phrases (Musical phrases/segments)
   │   ├── Trajectories (Pitch contours)
   │   │   └── Pitches (Individual frequency points)
   │   └── Articulations (Performance techniques)
   ├── Sections (Structural divisions)
   └── Metadata (Title, raga, tala, etc.)

Data Models
~~~~~~~~~~~

The API provides rich data models that map to this structure:

* :class:`~idtap_api.Piece` - Complete transcription
* :class:`~idtap_api.Phrase` - Musical phrase
* :class:`~idtap_api.Trajectory` - Pitch trajectory  
* :class:`~idtap_api.Pitch` - Individual pitch point
* :class:`~idtap_api.Raga` - Raga information
* :class:`~idtap_api.Section` - Structural sections

Authentication Model
~~~~~~~~~~~~~~~~~~~~

The API uses Google OAuth with secure token storage:

* **One-time setup** - Authenticate once per system
* **Automatic refresh** - Tokens renewed automatically
* **Secure storage** - Encrypted token storage
* **Cross-platform** - Works on Windows, macOS, Linux

Getting Help
------------

* **Documentation** - Complete API reference and examples
* **GitHub Issues** - Bug reports and feature requests
* **Community** - Discussion and questions

Next Steps
----------

Start with :doc:`user-guide/getting-started` for a step-by-step introduction.