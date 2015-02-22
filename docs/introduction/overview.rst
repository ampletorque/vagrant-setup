Overview
========

Zaphod is the platform that powers https://www.crowdsupply.com. It is built with
`Pyramid <http://docs.pylonsproject.org/en/latest/docs/pyramid.html>`_, a
modular Python web framework.

It is, of course, named after `Zaphod Beeblebrox <https://en.wikipedia.org/wiki/Zaphod_Beeblebrox>`_.

.. image:: /images/zaphod.jpg

Important Dependencies
----------------------

* Pyramid
* SQLAlchemy
* pyramid_tm
* pyramid_mailer
* pyramid_frontend
* pyramid_uniform
* pyramid_es
* pyramid_cron
* gimlet

History / Legacy
----------------

The initial launch of Crowd Supply used a platform built on top of a
proprietary platform built by `Cart Logic <http://www.cartlogic.com>`_. Zaphod
is an extraction of the important core concepts that worked well from the
initial platform, rewritten with simpler structure, better data integrity, and
no extraneous features.

Goals
-----

While rolling out Zaphod as the live platform, maintainability and simplicity
is an extreme priority. No new cusotmer-facing features should be introduced,
except as essentially accidental byproducts of the rewrite.

Until the platform takes over running the live site, this repo should also
serve to maintain the script(s) to migrate the data from the old site.

Browser Support
---------------

Zaphod should support IE9+, modern FF, and Chrome. IE8 support is nice but no
effort should be expended towards it.
