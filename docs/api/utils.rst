Utilities
=========

Utility functions for data conversion and processing.

.. currentmodule:: idtap_api.utils

Case Conversion
---------------

.. autofunction:: to_camel_case

.. autofunction:: to_snake_case

.. autofunction:: convert_keys

Usage Examples
--------------

.. code-block:: python

   from idtap_api.utils import to_camel_case, to_snake_case
   
   # Convert naming conventions
   snake_name = "phrase_number"
   camel_name = to_camel_case(snake_name)  # "phraseNumber"
   
   back_to_snake = to_snake_case(camel_name)  # "phrase_number"