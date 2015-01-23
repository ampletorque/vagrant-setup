Security-specific Notes
=======================

Security Page
-------------

- See security.html


Password Storage
----------------

- Use scrypt instead of bcrypt?
- At the very least, consider increasing the bcrypt work factor.


Password Resets
---------------

- Carefully consider expiration criteria and reuse criteria
- Don't reveal the presence or lack of an account in the password reset form or signup form(s) or checkout path

- Use a decorator like @quantize_time to prevent timing attacks, areas to
  consider are:
    - Login processing
    - Password resets


Customer Communication
----------------------

- Allow customers to supply a GPG key for correspondence


HTTPS Server Configuration
--------------------------

- Use OpenSSL 1.0.1j bleeeergh
