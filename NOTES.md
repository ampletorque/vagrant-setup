Concept
-------

Rewrite the platform powering the crowdsupply.com site in a new codebase, free
from links to scrappy / Cart Logic.

Maintainability is an extreme priority, and no new customer-facing features
should be introduced, except as essentially accidental byproducts of the
rewrite.

Until the platform takes over running the live site, this repo should also
serve to maintain the script(s) to migrate data from the old site.


Platform
--------

- Pyramid
- sqlalchemy
- gimlet
- manhattan for analytics / possible AB testing (this can be added later)
- pyramid_frontend for templating/theme/frontend
- pyramid_es with Elasticsearch
- pyramid_uniform for form validation?
- pyramid_cron for tasks
- pyramid_mailer for email
- alembic

Webserver
---------

- nginx
- uwsgi


Deployment
----------

- ansible


New Theme
---------

Since the theme needs to be somewhat re-implemented anyways, we may as well fix
a few things.

- Use bootstrap 3.3.1 but be prepared for the possibility that bootstrap 4 gets
introduced during dev, and switch to it if possible.
- Use require.js
- Try to avoid direct use of jquery?
