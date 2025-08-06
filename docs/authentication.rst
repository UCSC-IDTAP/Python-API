Authentication
==============

The IDTAP API uses Google OAuth for secure authentication. This guide explains how to set up and manage authentication.

Quick Authentication
--------------------

For most users, authentication is simple:

.. code-block:: python

   from idtap import login_google
   
   # This will open your browser for Google OAuth
   login_google()

The authentication process:

1. Opens your default web browser
2. Redirects to Google OAuth login
3. You authorize the IDTAP application
4. Tokens are securely stored on your system
5. Future API calls are automatically authenticated

Using the Client
----------------

Once authenticated, create a client and start using the API:

.. code-block:: python

   from idtap import SwaraClient
   
   client = SwaraClient()
   transcriptions = client.get_transcriptions()

Token Storage
-------------

The API uses a multi-layered security approach for storing OAuth tokens:

1. **OS Keyring** (Primary) - System keychain/credential manager
2. **Encrypted File** (Fallback) - AES encryption with machine-specific keys  
3. **Plain File** (Legacy) - Only for backward compatibility

Security Features
-----------------

* **Automatic token refresh** - Expired tokens are automatically renewed
* **CSRF protection** - State parameter validation during OAuth flow
* **Secure storage** - Tokens encrypted at rest
* **Machine-specific keys** - Encryption keys tied to your system

Manual Token Management
-----------------------

Advanced users can manage tokens programmatically:

.. code-block:: python

   from idtap.auth import get_stored_tokens, clear_stored_tokens
   
   # Check if tokens exist
   tokens = get_stored_tokens()
   if tokens:
       print("Already authenticated")
   else:
       print("Need to authenticate")
   
   # Clear stored tokens (logout)
   clear_stored_tokens()

Troubleshooting Authentication
------------------------------

Browser doesn't open
~~~~~~~~~~~~~~~~~~~~

If the browser doesn't open automatically:

.. code-block:: python

   from idtap import login_google
   
   # Get the auth URL manually
   auth_url = login_google(open_browser=False)
   print(f"Please visit: {auth_url}")

Permission denied errors
~~~~~~~~~~~~~~~~~~~~~~~~

If you get permission errors, try:

1. **Clear existing tokens**: ``clear_stored_tokens()``
2. **Check system keyring**: Ensure your OS keyring is accessible
3. **Use fallback storage**: Set environment variable ``IDTAP_USE_FILE_STORAGE=1``

Token corruption
~~~~~~~~~~~~~~~~

If tokens appear corrupted:

.. code-block:: python

   from idtap.auth import clear_stored_tokens
   
   # Clear all stored tokens and re-authenticate  
   clear_stored_tokens()
   login_google()

Environment Variables
--------------------

Optional environment variables for advanced configuration:

* ``IDTAP_USE_FILE_STORAGE=1`` - Force file-based token storage
* ``IDTAP_TOKEN_DIR`` - Custom directory for token files
* ``IDTAP_SERVER_HOST`` - Custom server hostname (for development)

Multiple Accounts
-----------------

The API currently supports one authenticated account per system. To switch accounts:

1. Clear existing tokens: ``clear_stored_tokens()``
2. Re-authenticate with new account: ``login_google()``