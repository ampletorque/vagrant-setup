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
