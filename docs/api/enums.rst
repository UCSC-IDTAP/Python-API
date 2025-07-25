Enumerations
============

Enumeration types used throughout the API.

.. currentmodule:: idtap_api

.. autoclass:: Instrument
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

.. code-block:: python

   from idtap_api import Instrument
   
   # Available instruments
   print(Instrument.SITAR)        # "Sitar"
   print(Instrument.VOCAL_MALE)   # "Vocal Male"
   print(Instrument.VOCAL_FEMALE) # "Vocal Female"